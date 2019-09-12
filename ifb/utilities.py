import json
import ifb
import string
from secrets import choice
import random
import xlsxwriter
import time
import datetime
import os
import pprint
import logging
import urllib.parse
import itertools

def genPassword(n=8):
    if n < 8:
        n = 8

    uppercase = string.ascii_uppercase
    numbers = string.digits
    specials = "!@#$%^&"
    pool = string.ascii_letters + numbers + specials

    password = ''.join(choice(specials))
    password += ''.join(choice(numbers))
    password += ''.join(choice(uppercase))
    password += ''.join(choice(pool) for i in range(n-3))

    return ''.join(random.sample(password,len(password)))

def sortOptionList(api,profile_id,option_list_id,reverse=False):
    options = api.readAllOptions(profile_id,option_list_id,"sort_order,key_value")
    if len(options) > 0:
        sorted_options = sorted(options, key=lambda k: k["key_value"],reverse=reverse)
        
        for i in range(len(sorted_options)):
            sorted_options[i]['sort_order'] = i

        return api.updateOptions(profile_id,option_list_id,sorted_options)
    else:
        return False

def deletePersonalData(api,profile_id,page_id):
    elements = api.readAllElements(profile_id,page_id,"name,reference_id_5,data_type,data_size")
    if len(elements) > 0:
        body = {"fields": []}

        for element in elements:
            if element['reference_id_5'] == "PERSONAL_DATA":
                body['fields'].append({"element_name": element['name'], "value": ""})
            elif element['data_type'] == 18:
                deletePersonalData(api,profile_id,element['data_size'])
            else:
                pass
        
        if len(body['fields']) > 0:
            return api.updateRecords(profile_id,page_id,body)
        else:
            return False
    
    else:
        return False

def insertSubformRecords(api,profile_id,page_id,parent_page_id,parent_element_id,parent_record_id,records):
    if isinstance(records,dict):
        records = [records]
    
    body = [{
        "parent_page_id": parent_page_id,
        "parent_element_id": parent_element_id,
        "parent_record_id": parent_record_id,
        "fields": [{"element_name": key, "value": record[key]} for key in record]
    } for record in records]

    result = api.createRecords(profile_id,page_id,body)

    if result:
        count = len(api.readAllRecords(profile_id,page_id,f"parent_page_id(=\"{parent_page_id}\"),parent_element_id(=\"{parent_element_id}\"),parent_record_id(=\"{parent_record_id}\")"))
        parent_element = api.readElement(profile_id,parent_page_id,parent_element_id)
        
        return api.updateRecord(profile_id,parent_page_id,parent_record_id,{
            "fields": [
                {
                    "element_name": parent_element['name'],
                    "value": count
                }
            ]
        })
    
    else:
        return result

def importRecords(api,profile_id,page_id,records):
    # check for mismatching data-column names
    elements = api.readAllElements(profile_id,page_id,"name")
    dcns = [element['name'] for element in elements]

    result = api.createRecords(profile_id,page_id,records)

    return result

def exportRecordsXLSX(api,profile,page,subforms=True):

    def sortByTerm(l,t,r=False):
        return sorted(l,key=lambda l: l[t],reverse=r)

    def getSubformPageIDs(api,profile,page):
        print("Searching through %s for subforms..." % page)
        page_ids = []

        elements = api.readAllElements(profile,page,"name,data_type(=\"18\"),data_size")

        for element in elements:
            page_ids.append({"page_id": element['data_size'], "parent_page_id": page, "parent_element_id": element['id']})
            page_ids += getSubformPageIDs(api,profile,element['data_size'])

        return page_ids

    def buildStructure(ifb,profile_id,page_id):
        dcns = []

        elements = ifb.readAllElements(profile_id,page_id,"name,data_type,data_size")

        for i in range(len(elements)):
            if elements[i]['data_type'] in (16,17,18,35):
                pass
            else:
                dcns.append(elements[i]['name'])

        return dcns

    def buildGrammar(structure,parent_page_id,parent_element_id):
        if parent_page_id == None or parent_element_id == None:
            fields = "id,parent_record_id,parent_page_id,parent_element_id,created_date,created_by,created_location,created_device_id,modified_date,modified_by,modified_location,modified_device_id,server_modified_date,"
        else:
            fields = "id,parent_record_id,parent_page_id(=\"%s\"),parent_element_id(=\"%s\"),created_date,created_by,created_location,created_device_id,modified_date,modified_by,modified_location,modified_device_id,server_modified_date," % (parent_page_id, parent_element_id)

        for i in range(len(structure)):
            fields += structure[i] + ","

        return fields.rstrip(',')

    page_info = api.readPage(profile,page)

    print("Creating XLSX file for <%s>..." % page_info['name'])

    # get list of page ids and parent page ids
    page_list = [{"page_id": page, "parent_page_id": None, "parent_element_id": None}]
    
    if subforms == True:
        page_list += getSubformPageIDs(api,profile,page)

    # get page names
    id_list = "|".join([f"(=\"{p['page_id']}\")" for p in page_list])
    page_names = api.readPages(profile,"id(%s)" % id_list)
    page_names = {p['id']:p['name'] for p in page_names}

    # add page names to page_list
    for i in range(len(page_list)):
        page_list[i]['page_name'] = page_names[page_list[i]['page_id']]

    data = {}

    # loop through page list and append records to data
    for p in page_list:
        print("Fetching records for %s <%s>..." % (p['page_name'],p['page_id']))
        if p['page_name'] not in data:
            data[p['page_name']] = []

        print("Building grammar...")
        structure = buildStructure(api,profile,p['page_id'])
        fields = buildGrammar(structure,p['parent_page_id'],p['parent_element_id'])

        print("Getting records...")
        records = api.readAllRecords(profile,p['page_id'],fields)
        if records is not None:
            data[p['page_name']] += records
            print("%s <%s> has %s records" % (p['page_name'],p['page_id'],len(records)))

    # create workbook
    workbook_name = "%s - %s.xlsx" % (page_info['name'],int(time.time()))
    print("Creating Workbook <%s>..." % workbook_name)
    workbook = xlsxwriter.Workbook(workbook_name,{'constant_memory': True})

    # loop through and create worksheets
    for d in data:
        print("Writing Worksheet <%s>..." % d[0:31])
        worksheet = workbook.add_worksheet(d[0:31])
        data[d] = sortByTerm(data[d],"id",True)

        if len(data[d]) > 0:
            # write data column names as headings
            col = 0
            for record in data[d][0]:
                worksheet.write(0,col,record)
                col += 1

            row = 1

            # write data to worksheet
            for record in data[d]:
                col = 0
                for cell in record:
                    worksheet.write_string(row, col, str(record[cell]))
                    col += 1
                row += 1

    workbook.close()
    return workbook_name
# __init__.py
__version__ = "1.5.1"

import time
import csv
import json
import jwt
import requests
import string
from secrets import choice
from collections import OrderedDict
import random

class IFB():
    class Decorators():
        @staticmethod
        def refreshToken(decorated):
            def wrapper(api,*args,**kwargs):
                if time.time() - api.access_token_expiration > 0:
                    api.requestAccessToken()
                return decorated(api,*args,**kwargs)

            return wrapper

    def __init__(self,server,client_id,client_secret):
        self.server = server
        self.client_id = client_id
        self.client_secret = client_secret

        self.access_token = None
        self.access_token_expiration = None
        self.session = requests.Session()
        self.session.headers.update({ 'Content-Type': 'application/json' })

        try:
            self.requestAccessToken()
        except Exception as e:
            print(e)
            return

    ####################################
    ## MISC RESOURCES
    ####################################
    def genPassword(self,n=8):
        if n < 8:
            return False

        uppercase = string.ascii_uppercase
        numbers = string.digits
        specials = "!@#$%^&"
        pool = string.ascii_letters + numbers + specials

        password = ''.join(choice(specials))
        password += ''.join(choice(numbers))
        password += ''.join(choice(uppercase))
        password += ''.join(choice(pool) for i in range(n-3))

        return ''.join(random.sample(password,len(password)))

    @Decorators.refreshToken
    def sortOptionList(self,profile_id,option_list_id,reverse=False):
        options = self.readAllOptions(profile_id,option_list_id,"sort_order,key_value")
        sorted_options = sorted(options, key=lambda k: k["key_value"],reverse=reverse)
        
        for i in range(len(sorted_options)):
            sorted_options[i]['sort_order'] = i

        self.updateOptions(profile_id,option_list_id,sorted_options)

    @Decorators.refreshToken
    def replaceRecords(self,profile_id,page_id,data):
        # DELETE EXISTING RECORDS
        print("Deleting all data...")
        self.deleteAllRecords(profile_id,page_id)

        # TRANSFORM DATA TO { "element_name": key, "value": value }
        for i in range(len(data)):
            obj = data[i]
            arr = { "fields": [] }

            for key in obj:
                if obj[key] is not None:
                    arr["fields"].append({ "element_name": key, "value": obj[key]})

            data[i] = arr

        # CREATE NEW RECORDS
        i = 0
        while i < len(data):
            step = 1000
            start = i
            stop = i + step if i + step < len(data) else len(data)

            section = data[start:stop]

            print("Creating records %s to %s" % (str(start+1),str(stop)))
            self.createRecords(profile_id,page_id,section)

            i += step

    @Decorators.refreshToken
    def deletePersonalData(self,profile_id,page_id):
        # GET ELEMENTS WITH reference_id_1 == "PERSONAL_DATA"
        elements = self.readAllElements(profile_id,page_id,"name,reference_id_5,data_type,data_size")

        body = {"fields": []}

        for i in range(len(elements)):
            if elements[i]['reference_id_5'] == "PERSONAL_DATA":
                body['fields'].append({"element_name": elements[i]['name'], "value": ""})
            elif elements[i]['data_type'] == 18:
                self.deletePersonalData(profile_id,elements[i]['data_size'])
            else:
                pass

        self.updateRecords(profile_id,page_id,body,'id(>"0")')
        print("Page <%s> cleaned..." % page_id)

    ####################################
    ## TOKEN RESOURCES
    ####################################
 
    def requestAccessToken(self):
        """Create JWT and request iFormBuilder Access Token
        If token is successfully returned, stored in session header
        Else null token is stored in session header
        """
        try:
            token_endpoint = "https://%s/exzact/api/oauth/token" % self.server
            jwt_payload = {
                'iss': self.client_id,
                'aud': token_endpoint,
                'iat': time.time(),
                'exp': time.time() + 300
            }

            encoded_jwt = jwt.encode(jwt_payload,self.client_secret,algorithm='HS256')
            token_body = {
                'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                'assertion': encoded_jwt 
            }

            request_token = requests.post(token_endpoint,data=token_body,timeout=5)
            request_token.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            self.access_token = request_token.json()['access_token']
            self.session.headers.update({ 'Authorization': "Bearer %s" % self.access_token })
            self.access_token_expiration = time.time() + 3300

    @Decorators.refreshToken
    def readAccessToken(self):
        try:
            request = "https://%s/exzact/api/v60/token" % (self.server)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    ####################################
    ## PROFILE RESOURCES
    ####################################

    @Decorators.refreshToken
    def createProfile(self,body):
        try:
            request = "https://%s/exzact/api/v60/profiles" % self.server
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readProfile(self,profile_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s" % (self.server,profile_id)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readProfiles(self,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles?offset=%s&limit=%s" % (self.server,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readAllProfiles(self,grammar=None):
        offset = 0
        limit = 100
        profiles = []

        while True:
            try:
                request = self.readProfiles(grammar,offset,limit)
                if len(request) == 0:
                    break
                else:
                    profiles += request
                    offset += limit
                    print("%s profiles fetched..." % len(profiles))
            except Exception as e:
                print(e)
                return
        
        return profiles

    @Decorators.refreshToken
    def updateProfile(self,profile_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s" % (self.server,profile_id)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readCompanyInfo(self,profile_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/company_info" % (self.server,profile_id)
            get_company_info = self.session.get(request)
            get_company_info.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return get_company_info.json()

    @Decorators.refreshToken
    def updateCompanyInfo(self,profile_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/company_info" % (self.server,profile_id)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    ####################################
    ## USER RESOURCES
    ####################################

    @Decorators.refreshToken
    def createUsers(self,profile_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users" % (self.server,profile_id)
            print(body)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readUser(self,profile_id,user_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users/%s" % (self.server,profile_id,user_id)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readUsers(self,profile_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users?offset=%s&limit=%s" % (self.server,profile_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readAllUsers(self,profile_id,grammar=None):
        offset = 0
        limit = 100
        users = []

        while True:
            try:
                request = self.readUsers(profile_id,grammar,offset,limit)
                if len(request) == 0:
                    break
                else:
                    users += request
                    offset += limit
                    print("%s users fetched..." % len(users))
            except Exception as e:
                print(e)
                return

        return users

    @Decorators.refreshToken
    def updateUser(self,profile_id,user_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users/%s" % (self.server,profile_id,user_id)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updateUsers(self,profile_id,body,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users?offset=%s&limit=%s" % (self.server,profile_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteUser(self,profile_id,user_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users/%s" % (self.server,profile_id,user_id)
            delete_user = self.session.delete(request)
            delete_user.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return delete_user.json()

    @Decorators.refreshToken
    def deleteUsers(self,profile_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users?offset=%s&limit=%s" % (self.server,profile_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def createUserGroup(self,profile_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/user_groups" % (self.server,profile_id)
            print(body)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readUserGroup(self,profile_id,user_group_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/user_groups/%s" % (self.server,profile_id,user_group_id)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readUserGroups(self,profile_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/user_groups?offset=%s&limit=%s" % (self.server,profile_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updateUserGroup(self,profile_id,user_group_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/user_groups/%s" % (self.server,profile_id,user_group_id)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updateUserGroups(self,profile_id,body,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/user_groups?offset=%s&limit=%s" % (self.server,profile_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteUserGroup(self,profile_id,user_group_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/user_groups/%s" % (self.server,profile_id,user_group_id)
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteUserGroups(self,profile_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/user_groups?offset=%s&limit=%s" % (self.server,profile_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def createUserPageAssignments(self,profile_id,user_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users/%s/page_assignments" % (self.server,profile_id,user_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readUserPageAssignment(self,profile_id,user_id,page_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users/%s/page_assignments/%s" % (self.server,profile_id,user_id,page_id)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readUserPageAssignments(self,profile_id,user_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users/%s/page_assignments?offset=%s&limit=%s" % (self.server,profile_id,user_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updateUserPageAssignment(self,profile_id,user_id,page_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users/%s/page_assignments/%s" % (self.server,profile_id,user_id,page_id)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updateUserPageAssignments(self,profile_id,user_id,body,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users/%s/page_assignments?offset=%s&limit=%s" % (self.server,profile_id,user_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteUserPageAssignment(self,profile_id,user_id,page_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users/%s/page_assignments/%s" % (self.server,profile_id,user_id,page_id)
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteUserPageAssignments(self,profile_id,user_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users/%s/page_assignments?offset=%s&limit=%s" % (self.server,profile_id,user_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def createUserRecordAssignments(self,profile_id,user_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users/%s/record_assignments" % (self.server,profile_id,user_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readUserRecordAssignment(self,profile_id,user_id,assignment_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users/%s/record_assignments/%s" % (self.server,profile_id,user_id,assignment_id)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readUserRecordAssignments(self,profile_id,user_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users/%s/record_assignments?offset=%s&limit=%s" % (self.server,profile_id,user_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updateUserRecordAssignment(self,profile_id,user_id,assignment_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users/%s/record_assignments/%s" % (self.server,profile_id,user_id,assignment_id)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updateUserRecordAssignments(self,profile_id,user_id,body,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users/%s/record_assignments?offset=%s&limit=%s" % (self.server,profile_id,user_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteUserRecordAssignment(self,profile_id,user_id,assignment_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users/%s/record_assignments/%s" % (self.server,profile_id,user_id,assignment_id)
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteUserRecordAssignments(self,profile_id,user_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/users/%s/record_assignments?offset=%s&limit=%s" % (self.server,profile_id,user_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    ####################################
    ## PAGE RESOURCES
    ####################################

    @Decorators.refreshToken
    def createPage(self,profile_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages" % (self.server,profile_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readPage(self,profile_id,page_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s" % (self.server,profile_id,page_id)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readPages(self,profile_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages?offset=%s&limit=%s" % (self.server,profile_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readAllPages(self,profile_id,grammar=None):
        offset = 0
        limit = 100
        pages = []

        while True:
            try:
                request = self.readPages(profile_id,grammar,offset,limit)
                if len(request) == 0:
                    break
                else:
                    pages += request
                    offset += limit
                    print("%s pages fetched..." % len(pages))
            except Exception as e:
                print(e)
                return

        return pages

    @Decorators.refreshToken
    def updatePage(self,profile_id,page_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s" % (self.server,profile_id,page_id)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updatePages(self,profile_id,body,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages?offset=%s&limit=%s" % (self.server,profile_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deletePage(self,profile_id,page_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s" % (self.server,profile_id,page_id)
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deletePages(self,profile_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages?offset=%s&limit=%s" % (self.server,profile_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def createPageGroup(self,profile_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/page_groups" % (self.server,profile_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readPageGroup(self,profile_id,page_group_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/page_groups/%s" % (self.server,profile_id,page_group_id)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readPageGroups(self,profile_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/page_groups?offset=%s&limit=%s" % (self.server,profile_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updatePageGroup(self,profile_id,page_group_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/page_groups/%s" % (self.server,profile_id,page_group_id)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updatePageGroups(self,profile_id,body,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/page_groups?offset=%s&limit=%s" % (self.server,profile_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deletePageGroup(self,profile_id,page_group_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/page_groups/%s" % (self.server,profile_id,page_group_id)
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deletePageGroups(self,profile_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/page_groups?offset=%s&limit=%s" % (self.server,profile_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def createPageAssignments(self,profile_id,page_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/assignments" % (self.server,profile_id,page_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readPageAssignment(self,profile_id,page_id,user_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/assignments/%s" % (self.server,profile_id,page_id,user_id)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readPageAssignments(self,profile_id,page_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/assignments?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readAllPageAssignments(self,profile_id,page_id,grammar=None):
        offset = 0
        limit = 100
        page_assignments = []

        while True:
            try:
                request = self.readPageAssignments(profile_id,page_id,grammar,offset,limit)
                if len(request) == 0:
                    break
                else:
                    page_assignments += request
                    offset += limit
                    print("%s page assignments fetched..." % len(page_assignments))
            except Exception as e:
                print(e)
                return

        return page_assignments

    @Decorators.refreshToken
    def updatePageAssignment(self,profile_id,page_id,user_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/assignments/%s" % (self.server,profile_id,page_id,user_id)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updatePageAssignments(self,profile_id,page_id,body,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/assignments?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deletePageAssignment(self,profile_id,page_id,user_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/assignments/%s" % (self.server,profile_id,page_id,user_id)
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deletePageAssignments(self,profile_id,page_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/assignments?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def createPageRecordAssignments(self,profile_id,page_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/record_assignments" % (self.server,profile_id,page_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readPageRecordAssignment(self,profile_id,page_id,assignment_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/record_assignments/%s" % (self.server,profile_id,page_id,assignment_id)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readPageRecordAssignments(self,profile_id,page_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/record_assignments?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updatePageRecordAssignment(self,profile_id,page_id,assignment_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/record_assignments/%s" % (self.server,profile_id,page_id,assignment_id)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updatePageRecordAssignments(self,profile_id,page_id,body,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/record_assignments?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deletePageRecordAssignment(self,profile_id,page_id,assignment_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/record_assignments/%s" % (self.server,profile_id,page_id,assignment_id)
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deletePageRecordAssignments(self,profile_id,page_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/record_assignments?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def createPageShares(self,profile_id,page_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/shared_page" % (self.server,profile_id,page_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readPageShares(self,profile_id,page_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/shared_page?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readPageDependencies(self,profile_id,page_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/dependencies" % (self.server,profile_id,page_id)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updatePageShares(self,profile_id,page_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/shared_page" % (self.server,profile_id,page_id)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deletePageShares(self,profile_id,page_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/shared_page" % (self.server,profile_id,page_id)
            result = self.session.delete(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def createPageDynamicAttributes(self,profile_id,page_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/dynamic_attributes" % (self.server,profile_id,page_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readPageDynamicAttribute(self,profile_id,page_id,attribute_name):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/dynamic_attributes/%s" % (self.server,profile_id,page_id,attribute_name)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readPageDynamicAttributes(self,profile_id,page_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/dynamic_attributes?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updatePageDynamicAttribute(self,profile_id,page_id,attribute_name,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/dynamic_attributes/%s" % (self.server,profile_id,page_id,attribute_name)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updatePageDynamicAttributes(self,profile_id,page_id,body,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/dynamic_attributes?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deletePageDynamicAttribute(self,profile_id,page_id,attribute_name):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/dynamic_attributes/%s" % (self.server,profile_id,page_id,attribute_name)
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deletePageDynamicAttributes(self,profile_id,page_id,grammar=None,offset=0,limit=0):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/dynamic_attributes?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def createPageLocalizations(self,profile_id,page_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/localizations" % (self.server,profile_id,page_id)
            post_page_localizations = self.session.post(request,data=json.dumps(body))
            post_page_localizations.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return post_page_localizations.json()

    @Decorators.refreshToken
    def readPageLocalization(self,profile_id,page_id,language_code):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/localizations/%s" % (self.server,profile_id,page_id,language_code)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readPageLocalizations(self,profile_id,page_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/localizations?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updatePageLocalization(self,profile_id,page_id,language_code,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/localizations/%s" % (self.server,profile_id,page_id,language_code)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updatePageLocalizations(self,profile_id,page_id,body,grammar=None,offset=0,limit=1000):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/localizations?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deletePageLocalization(self,profile_id,page_id,language_code):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/localizations/%s" % (self.server,profile_id,page_id,language_code)
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deletePageLocalizations(self,profile_id,page_id,grammar=None,offset=0,limit=1000):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/localizations?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def createPageEndpoint(self,profile_id,page_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/http_callbacks" % (self.server,profile_id,page_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readPageEndpoint(self,profile_id,page_id,endpoint_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/http_callbacks/%s" % (self.server,profile_id,page_id,endpoint_id)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()
    
    def readPageEndpoints(self,profile_id,page_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/http_callbacks?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updatePageEndpoint(self,profile_id,page_id,endpoint_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/http_callbacks/%s" % (self.server,profile_id,page_id,endpoint_id)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()
    
    def updatePageEndpoints(self,profile_id,page_id,body,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/http_callbacks?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deletePageEndpoint(self,profile_id,page_id,endpoint_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/http_callbacks/%s" % (self.server,profile_id,page_id,endpoint_id)
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()
    
    def deletePageEndpoints(self,profile_id,page_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/http_callbacks?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def createPageEmailAlerts(self,profile_id,page_id,emails):
        try:
            body = [{"email": emails[i]} for i in range(len(emails))]
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/email_alerts" % (self.server,profile_id,page_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readPageEmailAlerts(self,profile_id,page_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/email_alerts?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deletePageEmailAlerts(self,profile_id,page_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/email_alerts?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def createPageTriggerPost(self,profile_id,page_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/trigger_posts" % (self.server,profile_id,page_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readPageFeed(self,profile_id,page_id,grammar=None,offset=0,limit=100,deep=False):
        try:
            deep = 1 if deep == True else 0
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/feed?offset=%s&limit=%s&deep=%s" % (self.server,profile_id,page_id,offset,limit,deep)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    ####################################
    ## ELEMENT RESOURCES
    ####################################

    @Decorators.refreshToken
    def createElements(self,profile_id,page_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements" % (self.server,profile_id,page_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readElement(self,profile_id,page_id,element_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements/%s" % (self.server,profile_id,page_id,element_id)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readElements(self,profile_id,page_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readAllElements(self,profile_id,page_id,grammar=None):
        offset = 0
        limit = 100
        elements = []
        
        while True:
            try:
                request = self.readElements(profile_id,page_id,grammar,offset,limit)
                if len(request) == 0:
                    break
                else:
                    elements += request
                    offset += limit
                    print("%s elements fetched..." % len(elements))
            except Exception as e:
                print(e)
                return

        return elements

    @Decorators.refreshToken
    def updateElement(self,profile_id,page_id,element_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements/%s" % (self.server,profile_id,page_id,element_id)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updateElements(self,profile_id,page_id,body,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteElement(self,profile_id,page_id,element_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements/%s" % (self.server,profile_id,page_id,element_id)
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteElements(self,profile_id,page_id,grammar=None,offset=0,limit=0):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def createElementDynamicAttributes(self,profile_id,page_id,element_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements/%s/dynamic_attributes" % (self.server,profile_id,page_id,element_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readElementDynamicAttribute(self,profile_id,page_id,element_id,attribute_name):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements/%s/dynamic_attributes/%s" % (self.server,profile_id,page_id,element_id,attribute_name)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readElementDynamicAttributes(self,profile_id,page_id,element_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements/%s/dynamic_attributes?offset=%s&limit=%s" % (self.server,profile_id,page_id,element_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updateElementDynamicAttribute(self,profile_id,page_id,element_id,attribute_name,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements/%s/dynamic_attributes/%s" % (self.server,profile_id,page_id,element_id,attribute_name)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updateElementDynamicAttributes(self,profile_id,page_id,element_id,body,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements/%s/dynamic_attributes?offset=%s&limit=%s" % (self.server,profile_id,page_id,element_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteElementDynamicAttribute(self,profile_id,page_id,element_id,attribute_name):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements/%s/dynamic_attributes/%s" % (self.server,profile_id,page_id,element_id,attribute_name)
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteElementDynamicAttributes(self,profile_id,page_id,element_id,grammar=None,offset=0,limit=0):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements/%s/dynamic_attributes?offset=%s&limit=%s" % (self.server,profile_id,page_id,element_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def createElementLocalizations(self,profile_id,page_id,element_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements/%s/localizations" % (self.server,profile_id,page_id,element_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readElementLocalization(self,profile_id,page_id,element_id,language_code):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements/%s/localizations/%s" % (self.server,profile_id,page_id,element_id,language_code)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readElementLocalizations(self,profile_id,page_id,element_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements/%s/localizations?offset=%s&limit=%s" % (self.server,profile_id,page_id,element_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updateElementLocalization(self,profile_id,page_id,element_id,language_code,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements/%s/localizations/%s" % (self.server,profile_id,page_id,element_id,language_code)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updateElementLocalizations(self,profile_id,page_id,element_id,body,grammar=None,offset=0,limit=1000):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements/%s/localizations?offset=%s&limit=%s" % (self.server,profile_id,page_id,element_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteElementLocalization(self,profile_id,page_id,element_id,language_code):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements/%s/localizations/%s" % (self.server,profile_id,page_id,element_id,language_code)
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteElementLocalizations(self,profile_id,page_id,element_id,grammar=None,offset=0,limit=1000):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/elements/%s/localizations?offset=%s&limit=%s" % (self.server,profile_id,page_id,element_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    ####################################
    ## OPTION LIST RESOURCES
    ####################################

    @Decorators.refreshToken
    def createOptionList(self,profile_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists" % (self.server,profile_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readOptionList(self,profile_id,option_list_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists/%s" % (self.server,profile_id,option_list_id)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readOptionLists(self,profile_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists?offset=%s&limit=%s" % (self.server,profile_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readAllOptionLists(self,profile_id,grammar=None):
        offset = 0
        limit = 100
        option_lists = []

        while True:
            try:
                request = self.readOptionLists(profile_id,grammar,offset,limit)
                if len(request) == 0:
                    break
                else:
                    option_lists += request
                    offset += limit
                    print("%s option lists fetched..." % len(option_lists))
            except Exception as e:
                print(e)
                return
        
        return option_lists

    @Decorators.refreshToken
    def updateOptionList(self,profile_id,option_list_id,element_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists/%s" % (self.server,profile_id,option_list_id)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updateOptionLists(self,profile_id,body,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists?offset=%s&limit=%s" % (self.server,profile_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteOptionList(self,profile_id,option_list_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists/%s" % (self.server,profile_id,option_list_id)
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteOptionLists(self,profile_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists?offset=%s&limit=%s" % (self.server,profile_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readOptionListDependencies(self,profile_id,option_list_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists/%s/dependencies" % (self.server,profile_id,option_list_id)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    ####################################
    ## OPTION RESOURCES
    ####################################

    @Decorators.refreshToken
    def createOptions(self,profile_id,option_list_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists/%s/options" % (self.server,profile_id,option_list_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readOption(self,profile_id,option_list_id,option_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists/%s/options/%s" % (self.server,profile_id,option_list_id,option_id)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readOptions(self,profile_id,option_list_id,grammar=None,offset=0,limit=1000):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists/%s/options?offset=%s&limit=%s" % (self.server,profile_id,option_list_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readAllOptions(self,profile_id,option_list_id,grammar=None):
        offset = 0
        limit = 1000
        options = []

        while True:
            try:
                request = self.readOptions(profile_id,option_list_id,grammar,offset,limit)
                if len(request) == 0:
                    break
                else:
                    options += request
                    offset += limit
                    print("%s options fetched..." % len(options))
            except Exception as e:
                print(e)
                return
        
        return options

    @Decorators.refreshToken
    def updateOption(self,profile_id,option_list_id,option_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists/%s/options/%s" % (self.server,profile_id,option_list_id,option_id)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updateOptions(self,profile_id,option_list_id,body,grammar=None,offset=0,limit=1000):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists/%s/options?offset=%s&limit=%s" % (self.server,profile_id,option_list_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteOption(self,profile_id,option_list_id,option_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists/%s/options/%s" % (self.server,profile_id,option_list_id,option_id)
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteOptions(self,profile_id,option_list_id,grammar=None,offset=0,limit=1000):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists/%s/options?offset=%s&limit=%s" % (self.server,profile_id,option_list_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def createOptionLocalizations(self,profile_id,option_list_id,option_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists/%s/options/%s/localizations" % (self.server,profile_id,option_list_id,option_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readOptionLocalization(self,profile_id,option_list_id,option_id,language_code):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists/%s/options/%s/localizations/%s" % (self.server,profile_id,option_list_id,option_id,language_code)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readOptionLocalizations(self,profile_id,option_list_id,option_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists/%s/options/%s/localizations?offset=%s&limit=%s" % (self.server,profile_id,option_list_id,option_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updateOptionLocalization(self,profile_id,option_list_id,option_id,language_code,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists/%s/options/%s/localizations/%s" % (self.server,profile_id,option_list_id,option_id,language_code)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updateOptionLocalizations(self,profile_id,option_list_id,option_id,body,grammar=None,offset=0,limit=1000):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists/%s/options/%s/localizations?offset=%s&limit=%s" % (self.server,profile_id,option_list_id,option_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteOptionLocalization(self,profile_id,option_list_id,option_id,language_code):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists/%s/options/%s/localizations/%s" % (self.server,profile_id,option_list_id,option_id,language_code)
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteOptionLocalizations(self,profile_id,option_list_id,option_id,grammar=None,offset=0,limit=1000):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/optionlists/%s/options/%s/localizations?offset=%s&limit=%s" % (self.server,profile_id,option_list_id,option_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    ####################################
    ## RECORD RESOURCES
    ####################################

    @Decorators.refreshToken
    def createRecords(self,profile_id,page_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/records" % (self.server,profile_id,page_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readRecord(self,profile_id,page_id,record_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/records/%s" % (self.server,profile_id,page_id,record_id)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readRecords(self,profile_id,page_id,grammar=None,offset=0,limit=1000):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/records?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readAllRecords(self,profile_id,page_id,grammar=None):
        offset = 0
        limit = 1000
        records = []

        while True:
            try:
                request = self.readRecords(profile_id,page_id,grammar,offset,limit)
                if len(request) == 0:
                    break
                else:
                    records += request
                    offset += limit
                    print("%s records fetched..." % len(records))
            except Exception as e:
                print(e)
                return

        return records

    @Decorators.refreshToken
    def updateRecord(self,profile_id,page_id,record_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/records/%s" % (self.server,profile_id,page_id,record_id)
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def updateRecords(self,profile_id,page_id,body,grammar=None,offset=0,limit=1000):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/records?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.put(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteRecord(self,profile_id,page_id,record_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/records/%s" % (self.server,profile_id,page_id,record_id)
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteRecords(self,profile_id,page_id,grammar=None,offset=0,limit=1000):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/records?offset=%s&limit=%s" % (self.server,profile_id,page_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteAllRecords(self,profile_id,page_id,grammar="id(>\"0\")"):
        offset = 0
        limit = 1000
        total = 0

        while True:
            try:
                request = self.deleteRecords(profile_id,page_id,grammar,offset,limit)
                if len(request) == 0:
                    break
                else:
                    total += len(request)
                    print("Deleted %s records, %s total..." % (len(request),total))
            except Exception as e:
                print(e)
                return False

        return True

    @Decorators.refreshToken
    def createRecordAssignments(self,profile_id,page_id,record_id,body):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/records/%s/assignments" % (self.server,profile_id,page_id,record_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readRecordAssignment(self,profile_id,page_id,record_id,user_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/records/%s/assignments/%s" % (self.server,profile_id,page_id,record_id,user_id)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readRecordAssignments(self,profile_id,page_id,record_id,grammar=None,offset=0,limit=1000):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/records/%s/assignments?offset=%s&limit=%s" % (self.server,profile_id,page_id,record_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteRecordAssignment(self,profile_id,page_id,record_id,user_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/records/%s/assignments/%s" % (self.server,profile_id,page_id,record_id,user_id)
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def deleteRecordAssignments(self,profile_id,page_id,record_id,grammar=None,offset=0,limit=1000):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/pages/%s/records/%s/assignments?offset=%s&limit=%s" % (self.server,profile_id,page_id,record_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.delete(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    ####################################
    ## NOTIFICATION RESOURCES
    ####################################

    @Decorators.refreshToken
    def createNotification(self,profile_id,users,message):
        try:
            body = {"message": message, "users": users}
            request = "https://%s/exzact/api/v60/profiles/%s/notifications" % (self.server,profile_id)
            result = self.session.post(request,data=json.dumps(body))
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    ####################################
    ## PRIVATE MEDIA RESOURCES
    ####################################

    @Decorators.refreshToken
    def readNotification(self,profile_id,media_url):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/media?URL=%s" % (self.server,profile_id,media_url)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    ####################################
    ## DEVICE LICENSE RESOURCES
    ####################################

    @Decorators.refreshToken
    def readDeviceLicense(self,profile_id,license_id):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/licenses/%s" % (self.server,profile_id,license_id)
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

    @Decorators.refreshToken
    def readDeviceLicenses(self,profile_id,grammar=None,offset=0,limit=100):
        try:
            request = "https://%s/exzact/api/v60/profiles/%s/licenses?offset=%s&limit=%s" % (self.server,profile_id,offset,limit)
            if grammar != None:
                request += "&fields=%s" % grammar
            result = self.session.get(request)
            result.raise_for_status()
        except Exception as e:
            print(e)
            return
        else:
            return result.json()

if __name__ == "__main__":
    pass
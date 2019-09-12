import ifb
import time
import pytest
from fixtures import basic_user,form_builder,company_admin,server_admin
import random
import string
import os

#####
#
# genPassword Tests
#
#####

def test_genPassword(server_admin):
    assert ifb.utilities.genPassword() is not None

def test_genPassword_includes_uppercase(server_admin):
    password = ifb.utilities.genPassword()
    assert any(c.isupper() for c in password) == True

def test_genPassword_includes_digit(server_admin):
    password = ifb.utilities.genPassword()
    assert any(c.isdigit() for c in password) == True

def test_genPassword_includes_special(server_admin):
    password = ifb.utilities.genPassword()
    assert any(c in "!@#$%^&" for c in password) == True

#####
#
# sortOptionList Tests
#
#####

def test_sortOptionList_asc(server_admin):
    profile = server_admin.readProfile("self")
    option_lists = server_admin.readOptionLists(profile['id'])
    option_list_id = random.choice([o['id'] for o in option_lists])

    assert ifb.utilities.sortOptionList(server_admin,profile['id'],option_list_id)

def test_sortOptionList_desc(server_admin):
    profile = server_admin.readProfile("self")
    option_lists = server_admin.readOptionLists(profile['id'])
    option_list_id = random.choice([option_list['id'] for option_list in option_lists])

    assert ifb.utilities.sortOptionList(server_admin,profile['id'],option_list_id,True)

#####
#
# deletePersonalData Tests
#
#####

def test_deletePersonalData(server_admin):
    profile = server_admin.readProfile("self")
    pages = server_admin.readPages(profile['id'])
    page_id = random.choice([page['id'] for page in pages])

    assert ifb.utilities.deletePersonalData(server_admin,profile['id'],page_id) is not None

#####
#
# deletePersonalData Tests
#
#####

def test_insertSubformRecords_single(server_admin):
    assert ifb.utilities.insertSubformRecords(server_admin,461881,3586126,3586123,280487857,1,{
        "first_name": "PyTest",
        "last_name": "Automation"
    }) is not None

def test_insertSubformRecords_multiple(server_admin):
    assert ifb.utilities.insertSubformRecords(server_admin,461881,3586126,3586123,280487857,1,
    [
        {
            "first_name": "PyTest",
            "last_name": "Automation"
        },
        {
            "first_name": "PyTest2",
            "last_name": "Automation"
        }
    ]
    ) is not None

#####
#
# exportRecordsXLSX Tests
#
#####

def test_exportRecordsXLSX_subforms(server_admin):
    result = ifb.utilities.exportRecordsXLSX(server_admin,461881,3586123)
    assert os.path.isfile(f'./{result}') is True
    os.remove(result)

def test_exportRecordsXLSX_subformsFalse(server_admin):
    result = ifb.utilities.exportRecordsXLSX(server_admin,461881,3586123,False)
    assert os.path.isfile(f'./{result}') is True
    os.remove(result)

#####
#
# exportRecordsJSON Tests
#
#####

# def test_exportRecordsJSON_subforms(server_admin):
#     result = ifb.utilities.exportRecordsJSON(server_admin,461881,3586123)
#     assert os.path.isfile(f'./{result}') is True
#     os.remove(result)

# def test_exportRecordsJSON_subformsFalse(server_admin):
#     result = ifb.utilities.exportRecordsJSON(server_admin,461881,3586123,False)
#     assert os.path.isfile(f'./{result}') is True
#     os.remove(result)
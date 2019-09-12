import ifb
import time
import pytest
import datetime
from fixtures import basic_user,form_builder,company_admin,server_admin

#####
#
# Profile Tests
#
#####

profile_id = 461881

def test_readProfileSelf(server_admin):
    assert server_admin.readProfile("self")

def test_readProfileID(server_admin):
    assert server_admin.readProfile(profile_id)

# def test_createProfile(server_admin):
#     assert server_admin.createProfile(
#         {
#             "name": "PyTest Profile %s" % int(time.time()),
#             "max_user": 0,
#             "max_page": 0,
#             "is_active": False,
#             "email": "solutions@zerionsoftware.com"
#         }
#     )

def test_updateProfile(server_admin):
    profile = server_admin.readProfile("self")

    assert server_admin.updateProfile(profile['id'],{
        "max_page": profile['max_page'] + 1
    })

def test_readCompanyInfo(server_admin):
    assert server_admin.readCompanyInfo(461881)

def test_updateCompanyInfo(server_admin):
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    assert server_admin.updateCompanyInfo(461881,{
        "homemessage": f"Updated {timestamp}"
    })
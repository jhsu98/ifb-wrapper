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

def test_readUser(server_admin):
    assert server_admin.readUser(profile_id,53924848)

def test_readUsers(server_admin):
    assert server_admin.readUsers(profile_id)

def test_readAllUsers(server_admin):
    assert server_admin.readAllUsers(profile_id)

def test_createUsers_single(server_admin):
    result = server_admin.createUsers(profile_id, {
        "username": "automation",
        "password": ifb.utilities.genPassword(),
        "email": "solutions@zerionsoftware.com"
    })

    assert result is not None

    # server_admin.deleteUser(profile_id,result['id'])

def test_createUsers_multiple(server_admin):
    result = server_admin.createUsers(profile_id, [
        {
            "username": "automation1",
            "password": ifb.utilities.genPassword(),
            "email": "solutions@zerionsoftware.com"
        },
        {
            "username": "automation2",
            "password": ifb.utilities.genPassword(),
            "email": "solutions@zerionsoftware.com"
        }
    ])

    assert result is not None

    # for user in result:
    #     server_admin.deleteUser(profile_id,user['id'])

def test_updateUser(server_admin):
    assert server_admin.updateUser(profile_id,53924848,{
        "can_thunderplug_sync": True
    })

def test_updateUsers(server_admin):
    assert server_admin.updateUsers(profile_id,{
        "can_thunderplug_sync": False
    }, "id(>\"0\")")
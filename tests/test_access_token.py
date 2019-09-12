import ifb
import time
import pytest
from fixtures import basic_user,form_builder,company_admin,server_admin

#####
#
# Access Token Tests
#
#####

def test_empty_class():
    with pytest.raises(TypeError):
        ifb.IFB()

def test_bad_credentials():
    assert ifb.IFB("zeriontest.iformbuilder.com","invalid","invalid").access_token is None

def test_basic_user_token(basic_user):
    assert basic_user.access_token

def test_form_builder_token(form_builder):
    assert form_builder.access_token

def test_company_admin_token(company_admin):
    assert company_admin.access_token

def test_server_admin_token(server_admin):
    assert server_admin.access_token

# def test_refresh_token(server_admin):
#     time.sleep(3601)
#     assert server_admin.readProfile("self")

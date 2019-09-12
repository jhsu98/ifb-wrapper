import ifb
import pytest

#####
#
# Fixtures: Different user roles
# (basic, form_builde, company, server)
#
#####
@pytest.fixture
def basic_user():
    return ifb.IFB("","","")

@pytest.fixture
def form_builder():
    return ifb.IFB("","","")

@pytest.fixture
def company_admin():
    return ifb.IFB("","","")

@pytest.fixture
def server_admin():
    return ifb.IFB("","","")

# - End Fixtures -----------------------
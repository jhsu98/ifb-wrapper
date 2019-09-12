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
    return ifb.IFB("zeriontest.iformbuilder.com","a32746c06e15eb39e0998bda29f6c5e3f929937d","d8dbe3f3849a96861f7d3b200ccd40ff8979c5d2")

@pytest.fixture
def form_builder():
    return ifb.IFB("zeriontest.iformbuilder.com","3a8f367c086d422032fc06c57110f11d529a6e09","bca9455112bba78f3c9780049acd85b530e61fe7")

@pytest.fixture
def company_admin():
    return ifb.IFB("zeriontest.iformbuilder.com","2c7e95f3fbdbce1aeb902cc8f59a0c708d680560","2aecf63ef9fad53334ea6a8dc235cdc4c152771b")

@pytest.fixture
def server_admin():
    return ifb.IFB("zeriontest.iformbuilder.com","8b357ac8a027c7e480ee87f80d083b4019a8b0a3","5e7bd78ec54901e0b72b52140f3c11eb08a2fc6d")

# - End Fixtures -----------------------
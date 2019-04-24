# __init__.py
__version__ = "1.3.0"

import time
import json
import jwt
import requests
import string
from secrets import choice
import random
 
class IFB():

    def __init__(self,server,client_id,client_secret):
        self.server = server
        self.client_id = client_id
        self.client_secret = client_secret

        self.access_token = None
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

    def sortOptionList(self,profile_id,option_list_id,reverse=False):
        options = self.readAllOptions(profile_id,option_list_id,"sort_order,key_value")
        sorted_options = sorted(options, key=lambda k: k["key_value"],reverse=reverse)
        
        for i in range(len(sorted_options)):
            sorted_options[i]['sort_order'] = i

        self.updateOptions(profile_id,option_list_id,sorted_options)

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

    ####################################
    ## ELEMENT RESOURCES
    ####################################

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

if __name__ == "__main__":
    pass
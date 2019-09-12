# __init__.py
__version__ = "1.5.4"

import logging
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
import time
import csv
import json
import jwt
import requests
from collections import OrderedDict
import math
import urllib.parse
from . import utilities

class IFB():
    class Decorators():
        @staticmethod
        def refreshToken(decorated):
            def wrapper(api,*args,**kwargs):
                if api.access_token is not None:
                    if time.time() - api.access_token_expiration > 0:
                        api.requestAccessToken()
                    return decorated(api,*args,**kwargs)

            return wrapper

    def __init__(self,server=None,client_key=None,client_secret=None):
        if not isinstance(server, str) or not isinstance(client_key, str) or not isinstance(client_key, str):
            raise TypeError("Invalid API credentials")

        self.server = server
        self.client_key = client_key
        self.client_secret = client_secret

        self.home_profile = None
        self.api_calls = 0
        self.access_token = None
        self.access_token_expiration = None
        self.__start_time = time.time()
        self.session = requests.Session()
        self.session.headers.update({ 'Content-Type': 'application/json' })

        try:
            self.requestAccessToken()
            self.host = f"https://{self.server}/exzact/api/v60/"
            self.home_profile = self.readAccessToken()['user']['profile_id']

        except Exception as e:
            print(e)
            return

    def getExecutionTime(self):
        return math.ceil(time.time() - self.__start_time)

    @Decorators.refreshToken
    def __get(self,resource):
        try:
            result = self.session.get(self.host+resource)
            self.api_calls += 1
            if result.status_code >= 300:
                result.raise_for_status()
        except Exception as e:
            print(f"<{result.status_code}> {e}, {result.json()['error_message']}")
        finally:
            return result.json()

    @Decorators.refreshToken
    def __post(self,resource,body):
        try:
            result = self.session.post(self.host+resource,data=body)
            self.api_calls += 1
            result.status_code = 999
            if result.status_code >= 300:
                result.raise_for_status()
        except Exception as e:
            print(f"<{result.status_code}> {e}, {result.json()['error_message']}")
        finally:
            return result.json()

    @Decorators.refreshToken
    def __put(self,resource,body):
        try:
            result = self.session.put(self.host+resource,data=body)
            self.api_calls += 1
            if result.status_code >= 300:
                result.raise_for_status()
        except Exception as e:
            print(f"<{result.status_code}> {e}, {result.json()['error_message']}")
        finally:
            return result.json()
    
    @Decorators.refreshToken
    def __delete(self,resource):
        try:
            result = self.session.delete(self.host+resource)
            self.api_calls += 1
            if result.status_code >= 300:
                result.raise_for_status()
        except Exception as e:
            print(f"<{result.status_code}> {e}, {result.json()['error_message']}")
        finally:
            return result.json()

    def __buildOffsetLimitGrammar(self,resource,offset,limit,grammar):
        if grammar is not None or offset is not None or limit is not None:
            resource += "?"
            fields = []
            if grammar is not None:
                fields.append(f"fields={urllib.parse.quote(grammar)}")
            if offset is not None:
                fields.append(f"offset={offset}")
            if limit is not None:
                fields.append(f"limit={limit}")
            return resource + "&".join(fields)
        else:
            return resource

    def __formatFieldsElementNameValue(self,r):
        if isinstance(r,dict):
            record = {}
            
            if 'parent_page_id' in r and r['parent_page_id'] > 0:
                record['parent_page_id'] = r['parent_page_id']
                r.pop('parent_page_id')
            if 'parent_element_id' in r and r['parent_element_id'] > 0:
                record['parent_element_id'] = r['parent_element_id']
                r.pop('parent_element_id')
            if 'parent_record_id' in r and r['parent_record_id'] > 0:
                record['parent_record_id'] = r['parent_record_id']
                r.pop('parent_record_id')

            record['fields'] = [{"element_name": key, "value": r[key]} for key in r]
            return record
        else:
            return r

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
                'iss': self.client_key,
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

    def readAccessToken(self):
        request = "token"
        return self.__get(request)

    ####################################
    ## PROFILE RESOURCES
    ####################################

    def getHomeProfile(self):
        request = "profiles/self"
        return self.__get(request)

    def createProfile(self,body):
        request = "profiles"
        return self.__post(request,json.dumps(body))

    def readProfile(self,profile_id):
        request = "profiles/%s" % (profile_id)
        return self.__get(request)

    def readProfiles(self,grammar=None,offset=None,limit=None):
        request = "profiles"
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def readAllProfiles(self,grammar=None):
        offset = 0
        limit = 100
        profiles = []

        while True:
            request = self.readProfiles(grammar=grammar,offset=offset,limit=limit)
            profiles += request
            offset += limit
            if len(request) < limit:
                break
            
        return profiles

    def updateProfile(self,profile_id,body):
        request = "profiles/%s" % (profile_id)
        return self.__put(request,json.dumps(body))

    def readCompanyInfo(self,profile_id):
        request = "profiles/%s/company_info" % (profile_id)
        return self.__get(request)

    def updateCompanyInfo(self,profile_id,body):
        request = "profiles/%s/company_info" % (profile_id)
        return self.__put(request,json.dumps(body))

    ####################################
    ## USER RESOURCES
    ####################################

    def createUsers(self,profile_id,body):
        request = "profiles/%s/users" % (profile_id)
        return self.__post(request,json.dumps(body))

    def readUser(self,profile_id,user_id):
        request = "profiles/%s/users/%s" % (profile_id,user_id)
        return self.__get(request)

    def readUsers(self,profile_id,grammar=None,offset=None,limit=None):
        request = f"profiles/{profile_id}/users"
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def readAllUsers(self,profile_id,grammar=None):
        offset = 0
        limit = 100
        users = []

        while True:
            request = self.readUsers(profile_id,grammar=grammar,offset=offset,limit=limit)
            users += request
            offset += limit
            if len(request) < limit:
                break

        return users

    def updateUser(self,profile_id,user_id,body):
        request = "profiles/%s/users/%s" % (profile_id,user_id)
        return self.__put(request,json.dumps(body))

    def updateUsers(self,profile_id,body,grammar=None,offset=None,limit=None):
        request = "profiles/%s/users" % (profile_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__put(request,json.dumps(body))

    def deleteUser(self,profile_id,user_id):
        request = "profiles/%s/users/%s" % (profile_id,user_id)
        return self.__delete(request)

    def deleteUsers(self,profile_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/users" % (profile_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    def createUserGroup(self,profile_id,body):
        request = "profiles/%s/user_groups" % (profile_id)
        return self.__post(request,json.dumps(body))

    def readUserGroup(self,profile_id,user_group_id):
        request = "profiles/%s/user_groups/%s" % (profile_id,user_group_id)
        return self.__get(request)

    def readUserGroups(self,profile_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/user_groups" % (profile_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def updateUserGroup(self,profile_id,user_group_id,body):
        request = "profiles/%s/user_groups/%s" % (profile_id,user_group_id)
        return self.__put(request,json.dumps(body))

    def updateUserGroups(self,profile_id,body,grammar=None,offset=None,limit=None):
        request = "profiles/%s/user_groups" % (profile_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__put(request,json.dumps(body))

    def deleteUserGroup(self,profile_id,user_group_id):
        request = "profiles/%s/user_groups/%s" % (profile_id,user_group_id)
        return self.__delete(request)

    def deleteUserGroups(self,profile_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/user_groups" % (profile_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)
        
    def createUserPageAssignments(self,profile_id,user_id,body):
        request = "profiles/%s/users/%s/page_assignments" % (profile_id,user_id)
        return self.__post(request,json.dumps(body))

    def readUserPageAssignment(self,profile_id,user_id,page_id):
        request = "profiles/%s/users/%s/page_assignments/%s" % (profile_id,user_id,page_id)
        return self.__get(request)
        
    def readUserPageAssignments(self,profile_id,user_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/users/%s/page_assignments" % (profile_id,user_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def updateUserPageAssignment(self,profile_id,user_id,page_id,body):
        request = "profiles/%s/users/%s/page_assignments/%s" % (profile_id,user_id,page_id)
        return self.__put(request,json.dumps(body))

    def updateUserPageAssignments(self,profile_id,user_id,body,grammar=None,offset=None,limit=None):
        request = "profiles/%s/users/%s/page_assignments" % (profile_id,user_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__put(request,json.dumps(body))

    def deleteUserPageAssignment(self,profile_id,user_id,page_id):
        request = "profiles/%s/users/%s/page_assignments/%s" % (profile_id,user_id,page_id)
        return self.__delete(request)

    def deleteUserPageAssignments(self,profile_id,user_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/users/%s/page_assignments?offset=%s&limit=%s" % (profile_id,user_id,offset,limit)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    def createUserRecordAssignments(self,profile_id,user_id,body):
        request = "profiles/%s/users/%s/record_assignments" % (profile_id,user_id)
        return self.__post(request,json.dumps(body))

    def readUserRecordAssignment(self,profile_id,user_id,assignment_id):
        request = "profiles/%s/users/%s/record_assignments/%s" % (profile_id,user_id,assignment_id)
        return self.__get(request)

    def readUserRecordAssignments(self,profile_id,user_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/users/%s/record_assignments" % (profile_id,user_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def updateUserRecordAssignment(self,profile_id,user_id,assignment_id,body):
        request = "profiles/%s/users/%s/record_assignments/%s" % (profile_id,user_id,assignment_id)
        return self.__put(request,json.dumps(body))

    def updateUserRecordAssignments(self,profile_id,user_id,body,grammar=None,offset=None,limit=None):
        request = "profiles/%s/users/%s/record_assignments" % (profile_id,user_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__put(request,json.dumps(body))

    def deleteUserRecordAssignment(self,profile_id,user_id,assignment_id):
        request = "profiles/%s/users/%s/record_assignments/%s" % (profile_id,user_id,assignment_id)
        return self.__delete(request)

    def deleteUserRecordAssignments(self,profile_id,user_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/users/%s/record_assignments" % (profile_id,user_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    ####################################
    ## PAGE RESOURCES
    ####################################

    def createPage(self,profile_id,body):
        request = "profiles/%s/pages" % (profile_id)
        return self.__post(request,json.dumps(body))

    def readPage(self,profile_id,page_id):
        request = "profiles/%s/pages/%s" % (profile_id,page_id)
        return self.__get(request)

    def readPages(self,profile_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages" % (profile_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def readAllPages(self,profile_id,grammar=None):
        offset = 0
        limit = 100
        pages = []

        while True:
            request = self.readPages(profile_id,grammar=grammar,offset=offset,limit=limit)
            pages += request
            offset += limit
            if len(request) < limit:
                break

        return pages

    def updatePage(self,profile_id,page_id,body):
        request = "profiles/%s/pages/%s" % (profile_id,page_id)
        return self.__put(request,json.dumps(body))

    def updatePages(self,profile_id,body,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages" % (profile_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__put(request,json.dumps(body))

    def deletePage(self,profile_id,page_id):
        request = "profiles/%s/pages/%s" % (profile_id,page_id)
        return self.__delete(request)

    def deletePages(self,profile_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages" % (profile_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    def createPageGroup(self,profile_id,body):
        request = "profiles/%s/page_groups" % (profile_id)
        return self.__post(request,json.dumps(body))

    def readPageGroup(self,profile_id,page_group_id):
        request = "profiles/%s/page_groups/%s" % (profile_id,page_group_id)
        return self.__get(request)

    def readPageGroups(self,profile_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/page_groups" % (profile_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def updatePageGroup(self,profile_id,page_group_id,body):
        request = "profiles/%s/page_groups/%s" % (profile_id,page_group_id)
        return self.__put(request,json.dumps(body))

    def updatePageGroups(self,profile_id,body,grammar=None,offset=None,limit=None):
        request = "profiles/%s/page_groups" % (profile_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__put(request,json.dumps(body))

    def deletePageGroup(self,profile_id,page_group_id):
        request = "profiles/%s/page_groups/%s" % (profile_id,page_group_id)
        return self.__delete(request)

    def deletePageGroups(self,profile_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/page_groups" % (profile_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    def createPageAssignments(self,profile_id,page_id,body):
        request = "profiles/%s/pages/%s/assignments" % (profile_id,page_id)
        return self.__post(request,json.dumps(body))

    def readPageAssignment(self,profile_id,page_id,user_id):
        request = "profiles/%s/pages/%s/assignments/%s" % (profile_id,page_id,user_id)
        return self.__get(request)

    def readPageAssignments(self,profile_id,page_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/assignments" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def readAllPageAssignments(self,profile_id,page_id,grammar=None):
        offset = 0
        limit = 100
        page_assignments = []

        while True:
            request = self.readPageAssignments(profile_id,page_id,grammar=grammar,offset=offset,limit=limit)
            page_assignments += request
            offset += limit
            if len(request) < limit:
                break

        return page_assignments

    def updatePageAssignment(self,profile_id,page_id,user_id,body):
        request = "profiles/%s/pages/%s/assignments/%s" % (profile_id,page_id,user_id)
        return self.__put(request,json.dumps(body))

    def updatePageAssignments(self,profile_id,page_id,body,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/assignments" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__put(request,json.dumps(body))

    def deletePageAssignment(self,profile_id,page_id,user_id):
        request = "profiles/%s/pages/%s/assignments/%s" % (profile_id,page_id,user_id)
        return self.__delete(request)

    def deletePageAssignments(self,profile_id,page_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/assignments" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    def createPageRecordAssignments(self,profile_id,page_id,body):
        request = "profiles/%s/pages/%s/record_assignments" % (profile_id,page_id)
        return self.__post(request,json.dumps(body))

    def readPageRecordAssignment(self,profile_id,page_id,assignment_id):
        request = "profiles/%s/pages/%s/record_assignments/%s" % (profile_id,page_id,assignment_id)
        return self.__get(request)

    def readPageRecordAssignments(self,profile_id,page_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/record_assignments" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def updatePageRecordAssignment(self,profile_id,page_id,assignment_id,body):
        request = "profiles/%s/pages/%s/record_assignments/%s" % (profile_id,page_id,assignment_id)
        return self.__put(request,json.dumps(body))

    def updatePageRecordAssignments(self,profile_id,page_id,body,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/record_assignments" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__put(request,json.dumps(body))

    def deletePageRecordAssignment(self,profile_id,page_id,assignment_id):
        request = "profiles/%s/pages/%s/record_assignments/%s" % (profile_id,page_id,assignment_id)
        return self.__delete(request)

    def deletePageRecordAssignments(self,profile_id,page_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/record_assignments" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    def createPageShares(self,profile_id,page_id,body):
        request = "profiles/%s/pages/%s/shared_page" % (profile_id,page_id)
        return self.__post(request,json.dumps(body))

    def readPageShares(self,profile_id,page_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/shared_page" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def readPageDependencies(self,profile_id,page_id):
        request = "profiles/%s/pages/%s/dependencies" % (profile_id,page_id)
        return self.__get(request)

    def updatePageShares(self,profile_id,page_id,body):
        request = "profiles/%s/pages/%s/shared_page" % (profile_id,page_id)
        return self.__put(request,json.dumps(body))

    def deletePageShares(self,profile_id,page_id,grammar=None,offset=None,limit=None):
    # need to revisit and include way to delete via body with list of ids
        request = "profiles/%s/pages/%s/shared_page" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    def createPageDynamicAttributes(self,profile_id,page_id,body):
        request = "profiles/%s/pages/%s/dynamic_attributes" % (profile_id,page_id)
        return self.__post(request,json.dumps(body))

    def readPageDynamicAttribute(self,profile_id,page_id,attribute_name):
        request = "profiles/%s/pages/%s/dynamic_attributes/%s" % (profile_id,page_id,attribute_name)
        return self.__get(request)

    def readPageDynamicAttributes(self,profile_id,page_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/dynamic_attributes" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def updatePageDynamicAttribute(self,profile_id,page_id,attribute_name,body):
        request = "profiles/%s/pages/%s/dynamic_attributes/%s" % (profile_id,page_id,attribute_name)
        return self.__put(request,json.dumps(body))

    def updatePageDynamicAttributes(self,profile_id,page_id,body,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/dynamic_attributes" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__put(request,json.dumps(body))

    def deletePageDynamicAttribute(self,profile_id,page_id,attribute_name):
        request = "profiles/%s/pages/%s/dynamic_attributes/%s" % (profile_id,page_id,attribute_name)
        return self.__delete(request)

    def deletePageDynamicAttributes(self,profile_id,page_id,grammar=None,offset=0,limit=0):
        request = "profiles/%s/pages/%s/dynamic_attributes" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    def createPageLocalizations(self,profile_id,page_id,body):
        request = "profiles/%s/pages/%s/localizations" % (profile_id,page_id)
        return self.__post(request,body)

    def readPageLocalization(self,profile_id,page_id,language_code):
        request = "profiles/%s/pages/%s/localizations/%s" % (profile_id,page_id,language_code)
        return self.__get(request)

    def readPageLocalizations(self,profile_id,page_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/localizations" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def updatePageLocalization(self,profile_id,page_id,language_code,body):
        request = "profiles/%s/pages/%s/localizations/%s" % (profile_id,page_id,language_code)
        return self.__put(request,json.dumps(body))

    def updatePageLocalizations(self,profile_id,page_id,body,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/localizations" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__put(request,json.dumps(body))

    def deletePageLocalization(self,profile_id,page_id,language_code):
        request = "profiles/%s/pages/%s/localizations/%s" % (profile_id,page_id,language_code)
        return self.__delete(request)

    def deletePageLocalizations(self,profile_id,page_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/localizations" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    def createPageEndpoint(self,profile_id,page_id,body):
        request = "profiles/%s/pages/%s/http_callbacks" % (profile_id,page_id)
        return self.__post(request,json.dumps(body))

    def readPageEndpoint(self,profile_id,page_id,endpoint_id):
        request = "profiles/%s/pages/%s/http_callbacks/%s" % (profile_id,page_id,endpoint_id)
        return self.__get(request)
    
    def readPageEndpoints(self,profile_id,page_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/http_callbacks" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def updatePageEndpoint(self,profile_id,page_id,endpoint_id,body):
        request = "profiles/%s/pages/%s/http_callbacks/%s" % (profile_id,page_id,endpoint_id)
        return self.__put(request,json.dumps(body))
    
    def updatePageEndpoints(self,profile_id,page_id,body,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/http_callbacks" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__put(request,json.dumps(body))

    def deletePageEndpoint(self,profile_id,page_id,endpoint_id):
        request = "profiles/%s/pages/%s/http_callbacks/%s" % (profile_id,page_id,endpoint_id)
        return self.__delete(request)
    
    def deletePageEndpoints(self,profile_id,page_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/http_callbacks" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    def createPageEmailAlerts(self,profile_id,page_id,emails):
        body = [{"email": emails[i]} for i in range(len(emails))]
        request = "profiles/%s/pages/%s/email_alerts" % (profile_id,page_id)
        return self.__post(request,json.dumps(body))

    def readPageEmailAlerts(self,profile_id,page_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/email_alerts" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def deletePageEmailAlerts(self,profile_id,page_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/email_alerts" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    def createPageTriggerPost(self,profile_id,page_id,body):
        request = "profiles/%s/pages/%s/trigger_posts" % (profile_id,page_id)
        return self.__post(request,json.dumps(body))

    def readPageFeed(self,profile_id,page_id,grammar=None,offset=None,limit=None,deep=False):
        deep = 1 if deep == True else 0
        request = "profiles/%s/pages/%s/feed" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        request += f"?deep={deep}" if "?" not in request else f"&deep={deep}"
        return self.__get(request)

    ####################################
    ## ELEMENT RESOURCES
    ####################################

    def createElements(self,profile_id,page_id,body):
        request = "profiles/%s/pages/%s/elements" % (profile_id,page_id)
        return self.__post(request,json.dumps(body))

    def readElement(self,profile_id,page_id,element_id):
        request = "profiles/%s/pages/%s/elements/%s" % (profile_id,page_id,element_id)
        return self.__get(request)

    def readElements(self,profile_id,page_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/elements" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def readAllElements(self,profile_id,page_id,grammar=None):
        offset = 0
        limit = 100
        elements = []
        
        while True:
            request = self.readElements(profile_id,page_id,grammar=grammar,offset=offset,limit=limit)
            elements += request
            offset += limit
            if len(request) < limit:
                break

        return elements

    def updateElement(self,profile_id,page_id,element_id,body):
        request = "profiles/%s/pages/%s/elements/%s" % (profile_id,page_id,element_id)
        return self.__put(request,json.dumps(body))

    def updateElements(self,profile_id,page_id,body,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/elements" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__put(request,json.dumps(body))

    def deleteElement(self,profile_id,page_id,element_id):
        request = "profiles/%s/pages/%s/elements/%s" % (profile_id,page_id,element_id)
        return self.__delete(request)

    def deleteElements(self,profile_id,page_id,grammar=None,offset=0,limit=0):
        request = "profiles/%s/pages/%s/elements" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    def createElementDynamicAttributes(self,profile_id,page_id,element_id,body):
        request = "profiles/%s/pages/%s/elements/%s/dynamic_attributes" % (profile_id,page_id,element_id)
        return self.__post(request,json.dumps(body))

    def readElementDynamicAttribute(self,profile_id,page_id,element_id,attribute_name):
        request = "profiles/%s/pages/%s/elements/%s/dynamic_attributes/%s" % (profile_id,page_id,element_id,attribute_name)
        return self.__get(request)

    def readElementDynamicAttributes(self,profile_id,page_id,element_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/elements/%s/dynamic_attributes" % (profile_id,page_id,element_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def updateElementDynamicAttribute(self,profile_id,page_id,element_id,attribute_name,body):
        request = "profiles/%s/pages/%s/elements/%s/dynamic_attributes/%s" % (profile_id,page_id,element_id,attribute_name)
        return self.__put(request,json.dumps(body))

    def updateElementDynamicAttributes(self,profile_id,page_id,element_id,body,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/elements/%s/dynamic_attributes" % (profile_id,page_id,element_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__put(request,json.dumps(body))

    def deleteElementDynamicAttribute(self,profile_id,page_id,element_id,attribute_name):
        request = "profiles/%s/pages/%s/elements/%s/dynamic_attributes/%s" % (profile_id,page_id,element_id,attribute_name)
        return self.__delete(request)

    def deleteElementDynamicAttributes(self,profile_id,page_id,element_id,grammar=None,offset=0,limit=0):
        request = "profiles/%s/pages/%s/elements/%s/dynamic_attributes" % (profile_id,page_id,element_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    def createElementLocalizations(self,profile_id,page_id,element_id,body):
        request = "profiles/%s/pages/%s/elements/%s/localizations" % (profile_id,page_id,element_id)
        return self.__post(request,json.dumps(body))

    def readElementLocalization(self,profile_id,page_id,element_id,language_code):
        request = "profiles/%s/pages/%s/elements/%s/localizations/%s" % (profile_id,page_id,element_id,language_code)
        return self.__get(request)

    def readElementLocalizations(self,profile_id,page_id,element_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/elements/%s/localizations" % (profile_id,page_id,element_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def updateElementLocalization(self,profile_id,page_id,element_id,language_code,body):
        request = "profiles/%s/pages/%s/elements/%s/localizations/%s" % (profile_id,page_id,element_id,language_code)
        return self.__put(request,json.dumps(body))

    def updateElementLocalizations(self,profile_id,page_id,element_id,body,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/elements/%s/localizations" % (profile_id,page_id,element_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__put(request,json.dumps(body))

    def deleteElementLocalization(self,profile_id,page_id,element_id,language_code):
        request = "profiles/%s/pages/%s/elements/%s/localizations/%s" % (profile_id,page_id,element_id,language_code)
        return self.__delete(request)

    def deleteElementLocalizations(self,profile_id,page_id,element_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/elements/%s/localizations" % (profile_id,page_id,element_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    ####################################
    ## OPTION LIST RESOURCES
    ####################################

    def createOptionList(self,profile_id,body):
        request = "profiles/%s/optionlists" % (profile_id)
        return self.__post(request,json.dumps(body))

    def readOptionList(self,profile_id,option_list_id):
        request = "profiles/%s/optionlists/%s" % (profile_id,option_list_id)
        return self.__get(request)

    def readOptionLists(self,profile_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/optionlists" % (profile_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def readAllOptionLists(self,profile_id,grammar=None):
        offset = 0
        limit = 100
        option_lists = []

        while True:
            request = self.readOptionLists(profile_id,grammar=grammar,offset=offset,limit=limit)
            option_lists += request
            offset += limit
            if len(request) < limit:
                break
        
        return option_lists

    def updateOptionList(self,profile_id,option_list_id,element_id,body):
        request = "profiles/%s/optionlists/%s" % (profile_id,option_list_id)
        return self.__put(request,json.dumps(body))

    def updateOptionLists(self,profile_id,body,grammar=None,offset=None,limit=None):
        request = "profiles/%s/optionlists" % (profile_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__put(request,json.dumps(body))

    def deleteOptionList(self,profile_id,option_list_id):
        request = "profiles/%s/optionlists/%s" % (profile_id,option_list_id)
        return self.__delete(request)

    def deleteOptionLists(self,profile_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/optionlists" % (profile_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    def readOptionListDependencies(self,profile_id,option_list_id):
        request = "profiles/%s/optionlists/%s/dependencies" % (profile_id,option_list_id)
        return self.__get(request)

    ####################################
    ## OPTION RESOURCES
    ####################################

    def createOptions(self,profile_id,option_list_id,body):
        request = "profiles/%s/optionlists/%s/options" % (profile_id,option_list_id)
        return self.__post(request,json.dumps(body))

    def readOption(self,profile_id,option_list_id,option_id):
        request = "profiles/%s/optionlists/%s/options/%s" % (profile_id,option_list_id,option_id)
        return self.__get(request)

    def readOptions(self,profile_id,option_list_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/optionlists/%s/options" % (profile_id,option_list_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def readAllOptions(self,profile_id,option_list_id,grammar=None):
        offset = 0
        limit = 1000
        options = []

        while True:
            request = self.readOptions(profile_id,option_list_id,grammar=grammar,offset=offset,limit=limit)
            options += request
            offset += limit
            if len(request) < limit:
                break
        
        return options

    def updateOption(self,profile_id,option_list_id,option_id,body):
        request = "profiles/%s/optionlists/%s/options/%s" % (profile_id,option_list_id,option_id)
        return self.__put(request,json.dumps(body))

    def updateOptions(self,profile_id,option_list_id,body,grammar=None,offset=None,limit=None):
        request = "profiles/%s/optionlists/%s/options" % (profile_id,option_list_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__put(request,json.dumps(body))

    def deleteOption(self,profile_id,option_list_id,option_id):
        request = "profiles/%s/optionlists/%s/options/%s" % (profile_id,option_list_id,option_id)
        return self.__delete(request)

    def deleteOptions(self,profile_id,option_list_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/optionlists/%s/options" % (profile_id,option_list_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    def createOptionLocalizations(self,profile_id,option_list_id,option_id,body):
        request = "profiles/%s/optionlists/%s/options/%s/localizations" % (profile_id,option_list_id,option_id)
        return self.__post(request,json.dumps(body))

    def readOptionLocalization(self,profile_id,option_list_id,option_id,language_code):
        request = "profiles/%s/optionlists/%s/options/%s/localizations/%s" % (profile_id,option_list_id,option_id,language_code)
        return self.__get(request)

    def readOptionLocalizations(self,profile_id,option_list_id,option_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/optionlists/%s/options/%s/localizations" % (profile_id,option_list_id,option_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def updateOptionLocalization(self,profile_id,option_list_id,option_id,language_code,body):
        request = "profiles/%s/optionlists/%s/options/%s/localizations/%s" % (profile_id,option_list_id,option_id,language_code)
        return self.__put(request,json.dumps(body))

    def updateOptionLocalizations(self,profile_id,option_list_id,option_id,body,grammar=None,offset=None,limit=None):
        request = "profiles/%s/optionlists/%s/options/%s/localizations" % (profile_id,option_list_id,option_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__put(request,json.dumps(body))

    def deleteOptionLocalization(self,profile_id,option_list_id,option_id,language_code):
        request = "profiles/%s/optionlists/%s/options/%s/localizations/%s" % (profile_id,option_list_id,option_id,language_code)
        return self.__delete(request)

    def deleteOptionLocalizations(self,profile_id,option_list_id,option_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/optionlists/%s/options/%s/localizations" % (profile_id,option_list_id,option_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    ####################################
    ## RECORD RESOURCES
    ####################################

    def createRecords(self,profile_id,page_id,body):
        request = "profiles/%s/pages/%s/records" % (profile_id,page_id)
        if isinstance(body,dict):
            body = [body]
        if "fields" not in body[0]:
            body = [self.__formatFieldsElementNameValue(record) for record in body]
        return self.__post(request,json.dumps(body))

    def readRecord(self,profile_id,page_id,record_id):
        request = "profiles/%s/pages/%s/records/%s" % (profile_id,page_id,record_id)
        return self.__get(request)

    def readRecords(self,profile_id,page_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/records" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def readAllRecords(self,profile_id,page_id,grammar=None):
        offset = 0
        limit = 1000
        records = []

        while True:
            request = self.readRecords(profile_id,page_id,grammar=grammar,offset=offset,limit=limit)
            records += request
            offset += limit
            if len(request) < limit:
                break

        return records

    def updateRecord(self,profile_id,page_id,record_id,body):
        request = "profiles/%s/pages/%s/records/%s" % (profile_id,page_id,record_id)
        return self.__put(request,json.dumps(body))

    def updateRecords(self,profile_id,page_id,body,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/records" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__put(request,json.dumps(body))

    def updateAllRecords(self,profile_id,page_id,body,grammar=None):
        offset = 0
        limit = 1000
        records = []

        while True:
            request = self.updateRecords(profile_id,page_id,body,grammar=grammar,offset=0,limit=limit)
            records += request
            offset += limit
            if len(request) < limit:
                if offset == 0:
                    break
                else:
                    offset = 0

        return records

    def deleteRecord(self,profile_id,page_id,record_id):
        request = "profiles/%s/pages/%s/records/%s" % (profile_id,page_id,record_id)
        return self.__delete(request)

    def deleteRecords(self,profile_id,page_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/records" % (profile_id,page_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    def deleteAllRecords(self,profile_id,page_id,grammar="id(>\"0\")"):
        offset = 0
        limit = 1000
        records = []

        while True:
            request = self.deleteRecords(profile_id,page_id,grammar,offset,limit)
            records += request
            offset += limit
            if len(request) < limit:
                break

        return records

    def createRecordAssignments(self,profile_id,page_id,record_id,body):
        request = "profiles/%s/pages/%s/records/%s/assignments" % (profile_id,page_id,record_id)
        return self.__post(request,json.dumps(body))

    def readRecordAssignment(self,profile_id,page_id,record_id,user_id):
        request = "profiles/%s/pages/%s/records/%s/assignments/%s" % (profile_id,page_id,record_id,user_id)
        return self.__get(request)

    def readRecordAssignments(self,profile_id,page_id,record_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/records/%s/assignments" % (profile_id,page_id,record_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def deleteRecordAssignment(self,profile_id,page_id,record_id,user_id):
        request = "profiles/%s/pages/%s/records/%s/assignments/%s" % (profile_id,page_id,record_id,user_id)
        return self.__delete(request)

    def deleteRecordAssignments(self,profile_id,page_id,record_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/pages/%s/records/%s/assignments" % (profile_id,page_id,record_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__delete(request)

    ####################################
    ## NOTIFICATION RESOURCES
    ####################################

    def createNotification(self,profile_id,users,message):
        body = {"message": message, "users": users}
        request = "profiles/%s/notifications" % (profile_id)
        return self.__post(request,json.dumps(body))

    ####################################
    ## PRIVATE MEDIA RESOURCES
    ####################################

    def readPrivateMedia(self,profile_id,media_url):
        request = "profiles/%s/media?URL=%s" % (profile_id,media_url)
        return self.__get(request)

    ####################################
    ## DEVICE LICENSE RESOURCES
    ####################################

    def readDeviceLicense(self,profile_id,license_id):
        request = "profiles/%s/licenses/%s" % (profile_id,license_id)
        return self.__get(request)

    def readDeviceLicenses(self,profile_id,grammar=None,offset=None,limit=None):
        request = "profiles/%s/licenses" % (profile_id)
        request = self.__buildOffsetLimitGrammar(request,offset,limit,grammar)
        return self.__get(request)

    def readAllDeviceLicenses(self,profile_id,grammar=None):
        offset = 0
        limit = 100
        licenses = []

        while True:
            request = self.readDeviceLicenses(profile_id,grammar=grammar,offset=0,limit=limit)
            licenses += request
            offset += limit
            if len(request) < limit:
                if offset == 0:
                    break
                else:
                    offset = 0

        return licenses

if __name__ == "__main__":
    pass
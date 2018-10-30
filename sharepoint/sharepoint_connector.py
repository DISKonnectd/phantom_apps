# Phantom App imports
import phantom.app as phantom
from phantom.rules import Vault
from phantom.base_connector import BaseConnector
from phantom.action_result import ActionResult

from sharepoint_consts import *
import requests
import urllib
import json
import xml.etree.ElementTree as ET
import datetime
import xmltodict
import itertools
import re
from bs4 import BeautifulSoup
from requests_ntlm import HttpNtlmAuth


class RetVal(tuple):
    def __new__(cls, val1, val2):
        return tuple.__new__(RetVal, (val1, val2))


class SharepointConnector(BaseConnector):

    def __init__(self):

        # Call the BaseConnectors init first
        super(SharepointConnector, self).__init__()

        self._state = None

    def _process_empty_reponse(self, response, action_result):

        if response.status_code == 200:
            return RetVal(phantom.APP_SUCCESS, {})

        return RetVal(action_result.set_status(phantom.APP_ERROR, "Empty response and no information in the header"), None)

    def _process_html_response(self, response, action_result):

        # An html response, treat it like an error
        status_code = response.status_code

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            error_text = soup.text
            split_lines = error_text.split('\n')
            split_lines = [x.strip() for x in split_lines if x.strip()]
            error_text = '\n'.join(split_lines)
        except:
            error_text = "Cannot parse error details"

        message = "Status Code: {0}. Data from server:\n{1}\n".format(status_code,
                error_text)

        message = message.replace('{', '{{').replace('}', '}}')

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_json_response(self, r, action_result):

        # Try a json parse
        try:
            resp_json = r.json()
        except Exception as e:
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Unable to parse JSON response. Error: {0}".format(str(e))), None)

        # Please specify the status codes here
        if 200 <= r.status_code < 399:
            return RetVal(phantom.APP_SUCCESS, resp_json)

        # You should process the error returned in the json
        message = "Error from server. Status Code: {0} Data from server: {1}".format(
                r.status_code, r.text.replace('{', '{{').replace('}', '}}'))

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_xml_response(self, response, action_result):

        # Try to parse xml
        try:
            resp_xml = ET.fromstring(response.content)
        except Exception as e:
            return RetVal(action_result.set_status(phantom.APP_ERROR, "Unable to parse XML response. Error: {0}".format(str(e))), None)

        # Please  specify the status codes here
        if 200 <= response.status_code < 399:
            return RetVal(phantom.APP_SUCCESS, resp_xml)

        message = "Status Code: {0}. Data from server:\n{1}\n".format(status_code,
                error_text)

        message = message.replace('{', '{{').replace('}', '}}')

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _convert_xml_to_json(self, r):
        # Implement the handler here
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        # action_result = self.add_action_result(ActionResult(dict(param)))

        # Parse the XML
        replace_regex = r"&#x([0-8]|[b-cB-C]|[e-fE-F]|1[0-9]|1[a-fA-F]);"
        clean_xml, number_of_substitutes = re.subn(replace_regex, '', r.text)
        self.debug_print("Clean XML - {0}".format(clean_xml))
        # resp_json = xmltodict.parse(clean_xml)
        # resp_json = ET.fromstring(clean_xml)
        self.debug_print(type(clean_xml))
        # resp_json = json.loads(json.dumps(resp_json))

        return clean_xml

    def _process_response(self, r, action_result):
        self.debug_print("Headers - {}".format(r.headers))

        # store the r_text in debug data, it will get dumped in the logs if the action fails
        if hasattr(action_result, 'add_debug_data'):
            action_result.add_debug_data({'r_status_code': r.status_code})
            action_result.add_debug_data({'r_text': r.text})
            action_result.add_debug_data({'r_headers': r.headers})

        # Process each 'Content-Type' of response separately

        # Process a json response
        if 'json' in r.headers.get('Content-Type', ''):
            return self._process_json_response(r, action_result)

        # Process an HTML resonse, Do this no matter what the api talks.
        # There is a high chance of a PROXY in between phantom and the rest of
        # world, in case of errors, PROXY's return HTML, this function parses
        # the error and adds it to the action_result.
        if 'html' in r.headers.get('Content-Type', ''):
            return self._process_html_response(r, action_result)

        # Process a xml response
        if 'xml' in r.headers.get('Content-Type', ''):
            return self._process_xml_response(response, action_result)

        # it's not content-type that is to be parsed, handle an empty response
        if not r.text:
            return self._process_empty_reponse(r, action_result)

        # everything else is actually an error at this point
        message = "Can't process response from server. Status Code: {0} Data from server: {1}".format(
                r.status_code, r.text.replace('{', '{{').replace('}', '}}'))

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _connect_session(self, param, url, headers=None, params=None, data=None, method="get"):
        self.debug_print("Connecting to session...")
        resp = ""

        if method == "post":
            self.debug_print("Calling post method...")
            resp = self._session.post(url, params=params, data=data, headers=headers)

        elif method == "get":
            self.debug_print("Calling get method...")
            resp = self._session.get(url, params=params, data=data, headers=headers)

        else:
            resp = "Can't process connection type"

        return resp

    def _handle_test_connectivity(self, param):

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        test_url = self._base_url + self._base_site + CONTEXTINFO_API_SUBPATH
        self.save_progress("Connecting to SharePoint API")

        self._connect_session(param, url=test_url, method="post")

        if (phantom.is_fail(action_result)):
            self.save_progress("Test Connectivity Failed. Error: {0}".format(action_result.get_message()))
            return action_result.get_status()

        # Return success
        self.save_progress("Test Connectivity Passed")
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_sync_list(self, param):

        # Implement the handler here
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Change Log Item Query Properties
        # https://msdn.microsoft.com/en-us/library/microsoft.sharepoint.client.changelogitemquery_members.aspx
        ViewName = param.get('ViewName', '')
        Query = param.get('Query', '')
        QueryOptions = param.get('QueryOptions', '')
        Contains = param.get('Contains', '')
        ViewFields = param.get('ViewFields', '')
        ChangeToken = param.get('ChangeToken', '')
        RowLimit = param.get('RowLimit', '')

        # Build JSON payload for POST
        payload = {"query":
                    {"__metadata":
                        {"type": "SP.ChangeLogItemQuery"},
                    "ViewName": ViewName,
                    "Query": Query,
                    "QueryOptions": QueryOptions,
                    "RowLimit": RowLimit,
                    "ViewFields": ViewFields,
                    "ChangeToken": ChangeToken,
                    "Contains": Contains}}

        # Build URL string
        sp_list = param['list']
        path = LIST_API_SUBPATH + "/GetByTitle('" + urllib.quote(sp_list) + "')/GetListItemChangesSinceToken"

        # Create a URL to connect to
        target_url = self._base_url + self._base_site + path
        self.debug_print(target_url)
        r = self._session.post(target_url, data=str(payload), headers=self._headers)

        # Parse the XML
        replace_regex = r"&#x([0-8]|[b-cB-C]|[e-fE-F]|1[0-9]|1[a-fA-F]);"
        clean_xml, number_of_substitutes = re.subn(replace_regex, '', r.text)
        self.debug_print(clean_xml)
        resp_json = xmltodict.parse(clean_xml)
        resp_json = json.loads(json.dumps(resp_json))

        list_changes_dict = resp_json['GetListItemChangesSinceTokenResult']['listitems']
        change_token = list_changes_dict['Changes']['@LastChangeToken']
        number_changes = list_changes_dict['rs:data']['@ItemCount']

        # Get user provide data to parse the response
        selected_tag = param.get('tag', '')
        attributes = [x.strip() for x in str(param.get('attributes', '')).split(",")]
        titles = [x.strip() for x in str(param.get('titles', '')).split(",")]
        # text_value = param.get('text', '')

        # Create xml for file
        root = ET.Element('Data')

        list_changes = []
        # Check to see if attributes and titles are provided
        if attributes != '':
            if titles != '':
                attr_titles = titles
            else:
                attr_titles = attributes

            # Process each row in the response dictionary
            for row in list_changes_dict['rs:data'][selected_tag]:
                xml_element = {}

                # Parse attributes from user
                for attr, name in itertools.izip(attributes, attr_titles):
                    # Adding @ sign to provided attributes for xmltodict syntax
                    attr = "@" + attr
                    xml_element[name] = row[attr] if attr in row.keys() else ""
                list_changes.append(xml_element)
                # Create XML items
                item = ET.SubElement(root, "Item")
                for k, v in xml_element.items():
                    ET.SubElement(item, k).text = v

        # Write xml file to vault using the list name and timestamp
        tree = ET.ElementTree(root)
        file_path = "/opt/phantom/vault/tmp/"
        xml_file = "{}-{}.xml".format(sp_list, datetime.datetime.now())
        tree.write(file_path + xml_file, encoding='UTF-8', method='xml')
        attached_file = Vault.add_attachment(file_path + xml_file,
            self.get_container_id(),
            metadata={"contains": ["XML File"]})

        # Add vault information to results
        action_result.add_data(attached_file)

        action_result.add_data({"List Changes": list_changes})
        action_result.add_data({"ChangeToken": change_token})
        action_result.add_data({"Change count": number_changes})
        action_result.add_data({"vaultId": attached_file['vault_id']})
        action_result.add_data({"full_response": resp_json})

        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_get_list(self, param):

        # Implement the handler here
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))

        # Build URL string
        sp_list = param.get('list')
        sp_filter = param.get('filter')
        path = LIST_API_SUBPATH + "/GetByTitle('" + urllib.quote(sp_list) + "')/items"
        if sp_filter:
            path = path + "?$" + sp_filter

        # Create a URL to connect to
        target_url = self._base_url + self._base_site + path
        resp = self._connect_session(param, url=target_url, headers=self._headers)

        # Add response code checking here
        # Process results
        if 200 <= resp.status_code < 400:
            # Parse the basic fields from each entry
            resp_json = json.loads(resp.text)
            resp_entries = resp_json['d']['results']

            # Add the response into the data section
            for entry in resp_entries:
                action_result.add_data(entry)
            action_result.set_status(phantom.APP_SUCCESS)

        else:
            message = "Can't process response from server. Status Code: {0} Data from server: {1}".format(
                resp.status_code, resp.text.replace('{', '{{').replace('}', '}}'))
            action_result.set_status(phantom.APP_ERROR, message)

        return action_result.get_status()

    def _handle_get_file(self, param):
        # Implement the handler here
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))
        sp_folder = param.get('filepath', '')
        sp_file = param.get('filename', '')

        # Build URL string
        path = FILE_API_SUBPATH + "/GetFileByServerRelativeURL('" + urllib.quote(sp_folder) + "/" + urllib.quote(sp_file) + "')/$value"

        # Create a URL to connect to
        target_url = self._base_url + self._base_site + path
        r = self._session.get(target_url, data=None, headers=None)

        if 200 <= r.status_code < 400:
            action_result.set_status(phantom.APP_SUCCESS)

            # Write file to vault
            file_path = "/vault/tmp/"
            with open(file_path + sp_file, 'wb') as f:
                f.write(r.content)
            attached_file = Vault.add_attachment(file_path + sp_file,
                self.get_container_id(),
                metadata={"contains": ["File"]})

            # Add vault information to results
            action_result.add_data(attached_file)

        else:
            message = "Can't process response from server. Status Code: {0} Data from server: {1}".format(
                r.status_code, r.text.replace('{', '{{').replace('}', '}}'))
            action_result.set_status(phantom.APP_ERROR, message)

        return action_result.get_status()

    def _handle_remove_file(self, param):
        # Implement the handler here
        self.save_progress("In action handler for: {0}".format(self.get_action_identifier()))

        # Add an action result object to self (BaseConnector) to represent the action for this param
        action_result = self.add_action_result(ActionResult(dict(param)))
        sp_folder = param.get('filepath', '')
        sp_file = param.get('filename', '')

        # Build URL string
        path = FILE_API_SUBPATH + "/GetFileByServerRelativeURL('" + urllib.quote(sp_folder) + "/" + urllib.quote(sp_file) + "')"

        # Create a URL to connect to
        target_url = self._base_url + self._base_site + path
        headers = self._headers

        # Added the Request Digest token to the headers
        headers.update({"IF-MATCH": "etag or \"*\"", "X-HTTP-Method": "DELETE"})

        r = self._session.post(target_url, data=None, headers=headers)

        # Process results
        if 200 <= r.status_code < 400:
            action_result.set_status(phantom.APP_SUCCESS)

        else:
            message = "Can't process response from server. Status Code: {0} Data from server: {1}".format(
                r.status_code, r.text.replace('{', '{{').replace('}', '}}'))
            action_result.set_status(phantom.APP_ERROR, message)

        self.debug_print("{} - {}".format(r.status_code, r.content))

        return action_result.get_status()

    def handle_action(self, param):

        ret_val = phantom.APP_SUCCESS

        # Get the action that we are supposed to execute for this App Run
        action_id = self.get_action_identifier()

        self.debug_print("action_id", self.get_action_identifier())

        if action_id == 'test_connectivity':
            ret_val = self._handle_test_connectivity(param)
        elif action_id == 'sync_list':
            ret_val = self._handle_sync_list(param)
        elif action_id == 'get_list':
            ret_val = self._handle_get_list(param)
        elif action_id == 'get_file':
            ret_val = self._handle_get_file(param)
        elif action_id == 'remove_file':
            ret_val = self._handle_remove_file(param)

        return ret_val

    def initialize(self):

        # Load the state in initialize, use it to store data
        # that needs to be accessed across actions
        self._state = self.load_state()

        """
        # get the asset config
        config = self.get_config()

        # Access values in asset config by the name

        # Required values can be accessed directly
        required_config_name = config['required_config_name']

        # Optional values should use the .get() function
        optional_config_name = config.get('optional_config_name')
        """
        config = self.get_config()
        self._headers = {
            "Accept": "application/json;odata=verbose",
            "Content-Type": "application/json;odata=verbose",
            "X-RequestForceAuthentication": "true"
        }

        self._session = requests.Session()
        self.save_progress("Using NTLM authentication")
        self._session.auth = HttpNtlmAuth(config.get('username'), config.get('password'))

        # Create a URL to connect to
        self._base_url = config.get('url')
        self._base_site = config.get('site')

        if (self._base_url.endswith('/')):
            self._base_url = self._base_url[:-1]

        if (self._base_site.endswith('/')):
            self._base_site = self._base_site[:-1]

        # Get token
        token_url = self._base_url + self._base_site + CONTEXTINFO_API_SUBPATH
        self.debug_print(token_url)
        response = self._session.post(token_url, params=None, data=None, headers=self._headers)
        self.debug_print(response.text)
        resp_json = response.json()
        form_digest_value = resp_json['d']['GetContextWebInformation']['FormDigestValue']

        # Added the Request Digest token to the headers
        self._headers.update({"X-RequestDigest": form_digest_value})

        return phantom.APP_SUCCESS

    def finalize(self):

        # Save the state, this data is saved accross actions and app upgrades
        self.save_state(self._state)
        return phantom.APP_SUCCESS


if __name__ == '__main__':

    import sys
    import pudb
    pudb.set_trace()

    if (len(sys.argv) < 2):
        print "No test json specified as input"
        exit(0)

    with open(sys.argv[1]) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = SharepointConnector()
        connector.print_progress_message = True
        ret_val = connector._handle_action(json.dumps(in_json), None)
        print (json.dumps(json.loads(ret_val), indent=4))

    exit(0)

# --
# File: bs4_connector.py
#
# --
# -----------------------------------------
# Phantom BS4 Connector python file
# -----------------------------------------

# Phantom App imports
import phantom.app as phantom

from phantom.base_connector import BaseConnector
from phantom.action_result import ActionResult

from bs4_consts import *
from bs4 import BeautifulSoup

import simplejson as json
import datetime
# import re


def _json_fallback(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    else:
        return obj


# Define the App Class
class Bs4Connector(BaseConnector):

    def __init__(self):

        # Call the BaseConnectors init first
        super(Bs4Connector, self).__init__()

    def _get_html_text(self, param):
        self.debug_print('_get_html_text() called.')

        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        # Get the data from the params to parse
        data = param[BS4_SOURCE_STRING]

        if not data:
            action_result.set_status(phantom.APP_ERROR, '', e)
            return action_result.get_status()

        try:
            parsed_html = BeautifulSoup(data, 'html.parser')
            plain_text = parsed_html.get_text()
            # .encode('ascii', 'ignore')

            # self.debug_print('soup text - {}'.format(plain_text))
            action_result.add_data(plain_text)
            action_result.set_status(phantom.APP_SUCCESS)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, '', e)
            return action_result.get_status()

        return action_result.get_status()

    def _get_html_urls(self, param):
        self.debug_print('_get_urls() called.')

        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        # Get the data from the params to parse
        data = param[BS4_SOURCE_STRING]
        urls = []

        if not data:
            action_result.set_status(phantom.APP_ERROR, '', e)
            return action_result.get_status()

        try:
            parsed_html = BeautifulSoup(data, "html.parser")
            for link in parsed_html.find_all('a'):
                urls.append(link.get('href'))

            action_result.add_data(urls)
            action_result.set_status(phantom.APP_SUCCESS)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, '', e)
            return action_result.get_status()

        return action_result.get_status()

    def _find_strings(self, param):
        self.debug_print('_find_string() called.')

        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        # Get the data from the params to parse
        data = param[BS4_SOURCE_STRING]
        search_string = param[BS4_SEARCH_STRING]
        strings = []

        if not data:
            action_result.set_status(phantom.APP_ERROR, '', e)
            return action_result.get_status()

        try:
            parsed_html = BeautifulSoup(data, "html.parser")
            for link in parsed_html.find_all():
                self.debug_print('link -- {}'.format(link.find(search_string)))
                if link.find(search_string) != -1:
                    strings.append(link)
            self.debug_print('data raw - {}'.format(parsed_html.find_all(search_string)))
            self.debug_print('strings - {}'.format(strings))
            action_result.add_data(strings)
            action_result.set_status(phantom.APP_SUCCESS)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, '', e)
            return action_result.get_status()

        return action_result.get_status()

    def handle_action(self, param):

        ret_val = phantom.APP_SUCCESS
        action = self.get_action_identifier()
        self.debug_print("action_id", self.get_action_identifier())

        if (action == "find_strings"):
            ret_val = self._find_strings(param)
        elif (action == "get_html_text"):
            ret_val = self._get_html_text(param)
        elif (action == "get_html_urls"):
            ret_val = self._get_html_urls(param)

        return ret_val


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

        connector = PythonUtilitiesConnector()
        connector.print_progress_message = True
        ret_val = connector._handle_action(json.dumps(in_json), None)
        print (json.dumps(json.loads(ret_val), indent=4))

    exit(0)

# --
# File: python_utilities_connector.py
#
# --
# -----------------------------------------
# Phantom sample App Connector python file
# -----------------------------------------

# Phantom App imports
import phantom.app as phantom

from phantom.base_connector import BaseConnector
from phantom.action_result import ActionResult

# Imports local to this App
from python_utilities_consts import *

import simplejson as json
import datetime
import re
import pprint


def _json_fallback(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    else:
        return obj


# Define the App Class
class PhantomUtilitiesConnector(BaseConnector):

    def __init__(self):

        # Call the BaseConnectors init first
        super(PhantomUtilitiesConnector, self).__init__()

    def _find_string(self, param):
        self.debug_print('_find_string() called.')
        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        try:
            searchString = param['search_string']
            sourceString = param['source_string']
            start = 0
            end = len(sourceString)
            if PYTHONUTILITIES_SOURCE_STRING_START in param:
                start = int(param[PYTHONUTILITIES_SOURCE_STRING_START])
            if PYTHONUTILITIES_SOURCE_STRING_END in param:
                end = int(param[PYTHONUTILITIES_SOURCE_STRING_END])
            results_dict = {}

            result_index = sourceString.find(searchString, start, end)
            results_dict.update({'search_string_index': result_index})
            action_result.add_data(results_dict)
            action_result.set_status(phantom.APP_SUCCESS)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, '', e)
            return action_result.get_status()

        return action_result.get_status()

    '''
    https://docs.python.org/2/library/re.html

    class re.RegexObject

    The RegexObject class supports the following methods and attributes:

    search(string[, pos[, endpos]]):

        Scan through string looking for a location where this regular expression produces a match, and return a corresponding
        MatchObject instance. Return None if no position in the string matches the pattern; note that this is different from
        finding a zero-length match at some point in the string.

        The optional second parameter pos gives an index in the string where the search is to start; it defaults to 0. This
        is not completely equivalent to slicing the string; the '^' pattern character matches at the real beginning of the
        string and at positions just after a newline, but not necessarily at the index where the search is to start.

        The optional parameter endpos limits how far the string will be searched; it will be as if the string is endpos characters
        long, so only the characters from pos to endpos - 1 will be searched for a match. If endpos is less than pos, no match
        will be found, otherwise, if rx is a compiled regular expression object, rx.search(string, 0, 50) is equivalent to
        rx.search(string[:50], 0).

        >>> pattern = re.compile("d")
        >>> pattern.search("dog")     # Match at index 0
        <_sre.SRE_Match object at ...>
        >>> pattern.search("dog", 1)  # No match; search doesn't include the "d"

    match(string[, pos[, endpos]]):

        If zero or more characters at the beginning of string match this regular expression, return a corresponding MatchObject
        instance. Return None if the string does not match the pattern; note that this is different from a zero-length match.

        The optional pos and endpos parameters have the same meaning as for the search() method.

        >>> pattern = re.compile("o")
        >>> pattern.match("dog")      # No match as "o" is not at the start of "dog".
        >>> pattern.match("dog", 1)   # Match as "o" is the 2nd character of "dog".
        <_sre.SRE_Match object at ...>

        If you want to locate a match anywhere in string, use search() instead (see also search() vs. match()).

    split(string, maxsplit=0):

        Identical to the split() function, using the compiled pattern.

    findall(string[, pos[, endpos]]):

        Similar to the findall() function, using the compiled pattern, but also accepts optional pos and endpos parameters
        that limit the search region like for match().

    finditer(string[, pos[, endpos]]):

        Similar to the finditer() function, using the compiled pattern, but also accepts optional pos and endpos parameters
        that limit the search region like for match().

    sub(repl, string, count=0):

        Identical to the sub() function, using the compiled pattern.

    subn(repl, string, count=0):

        Identical to the subn() function, using the compiled pattern.

    flags

        The regex matching flags. This is a combination of the flags given to compile() and any (?...) inline flags in the pattern.

    groups

        The number of capturing groups in the pattern.

    groupindex

        A dictionary mapping any symbolic group names defined by (?P<id>) to group numbers. The dictionary is empty if no
        symbolic groups were used in the pattern.

    pattern

        The pattern string from which the RE object was compiled
    '''
    def _re_function(self, param):
        self.debug_print('_re_function() called.')

        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        # Set variables
        action = param[PYTHONUTILITIES_REGEX_ACTION]
        pattern = re.compile(param[PYTHONUTILITIES_REGEX_PATTERN])
        self.debug_print('pattern - {!r}'.format(param[PYTHONUTILITIES_REGEX_PATTERN]))
        data = param[PYTHONUTILITIES_SOURCE_STRING]
        start = 0
        end = len(data) - 1
        if PYTHONUTILITIES_SOURCE_STRING_START in param:
            start = int(param[PYTHONUTILITIES_SOURCE_STRING_START])
        if PYTHONUTILITIES_SOURCE_STRING_END in param:
            end = int(param[PYTHONUTILITIES_SOURCE_STRING_END])
        if PYTHONUTILITIES_REGEX_REPLACE in param:
            if param[PYTHONUTILITIES_REGEX_REPLACE] == "''":
                replace = r''
            elif param[PYTHONUTILITIES_REGEX_REPLACE] == "' '":
                replace = r' '
            else:
                replace = param[PYTHONUTILITIES_REGEX_REPLACE]
        else:
            replace = r''

        self.debug_print('replace - {!r}'.format(replace))

        # Set case structure for defined action
        if action == 'search':
            result = pattern.search(data, start, end)
        elif action == 'match':
            result = pattern.match(data, start, end)
        elif action == 'split':
            result = pattern.split(data)
        elif action == 'findall':
            result = pattern.findall(data, start, end)
        elif action == 'finditer':
            result = pattern.finditer(data, start, end)
        elif action == 'sub':
            result = pattern.sub(replace, data)
        elif action == 'subn':
            result = pattern.subn(replace, data)
        else:
            action_results.set_status(phantom.APP_ERROR, 'Action not defined. Check requested action.')

        # Check to see if there are results then parse the type for formatting
        if result:
            action_result.set_status(phantom.APP_SUCCESS)
            if isinstance(result, (str, list, dict, tuple)):
                if type(result) is dict:
                    action_result.add_data(result)
                    self.debug_print('dict - {!r}'.format(result))
                else:
                    action_result.add_data(pprint.pformat(result))
                    self.debug_print('value - {!r}'.format(result))
            else:
                action_result.add_data(result.groupdict())

        return action_result.get_status()

    def _get_substring(self, param):
        self.debug_print('_get_substring() called.')

        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        try:
            sourceString = param[PYTHONUTILITIES_SOURCE_STRING]
            start = int(param['start']) - 1
            end = int(param['end']) - 1
            step = param['step']
            substring = sourceString[start:end:step]
            action_result.add_data(substring)
            action_result.set_status(phantom.APP_SUCCESS)
        except Exception as e:
            action_result.set_Status(phantom.APP_ERROR, '', e)
            return action_result.get_status()

        return action_result.get_status()

    def handle_action(self, param):

        ret_val = phantom.APP_SUCCESS
        action = self.get_action_identifier()
        self.debug_print("action_id", self.get_action_identifier())

        if (action == "find_string"):
            ret_val = self._find_string(param)
        elif (action == "split_string"):
            ret_val = self._split_string(param)
        elif (action == "get_substring"):
            ret_val = self._get_substring(param)
        elif (action == "regex_function"):
            ret_val = self._re_function(param)

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

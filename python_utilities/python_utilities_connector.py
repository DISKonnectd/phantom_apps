# --
# File: python_utilities_connector.py
#
# --
# Phantom App imports
import phantom.app as phantom
from phantom.base_connector import BaseConnector
from phantom.action_result import ActionResult

# Imports local to this App
from python_utilities_consts import *
import simplejson as json
import datetime
import re
import ast
# from py_expression_eval import Parser

# import pprint
import inspect


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

    # returns the python type of user provide item
    def _item_type(self, param):
        self.debug_print('{}'.format(inspect.stack()[0][3]))
        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        try:
            user_item = param[PYTHONUTILITIES_ITEM]
            result = type(user_item)
            action_result.add_data({'type': result})
            action_result.set_status(phantom.APP_SUCCESS)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, '', e)
            return action_result.get_status()

        return action_result.get_status()

    # returns a list from a dictionary through items() function
    def _dictionary_to_list(self, param):
        self.debug_print('{}'.format(inspect.stack()[0][3]))
        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        try:
            dictionary = param[PYTHONUTILITIES_ITEM]
            result = dictionary.items()
            action_result.add_data({'result': result})
            action_result.set_status(phantom.APP_SUCCESS)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, '', e)
            return action_result.get_status()

        return action_result.get_status()

    # returns the length of an item using len() function
    def _item_length(self, param):
        self.debug_print('{}'.format(inspect.stack()[0][3]))
        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        try:
            user_item = param[PYTHONUTILITIES_ITEM]
            result = len(user_item)
            action_result.add_data({'length': result})
            action_result.set_status(phantom.APP_SUCCESS)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, '', e)
            return action_result.get_status()

        return action_result.get_status()

    # returns the index of a substring in a string
    def _find_string(self, param):
        self.debug_print('{}'.format(inspect.stack()[0][3]))
        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        try:
            searchString = param[PYTHONUTILITIES_SEARCH_STRING]
            sourceString = param[PYTHONUTILITIES_SOURCE_STRING]
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

    # returns the length of an item using len() function
    def _split_string(self, param):
        self.debug_print('{}'.format(inspect.stack()[0][3]))
        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        try:
            source_string = param[PYTHONUTILITIES_SOURCE_STRING]
            result = source_string.split(PYTHONUTILITIES_SPLIT_VALUE)
            action_result.add_data({'list': result})
            action_result.set_status(phantom.APP_SUCCESS)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, '', e)
            return action_result.get_status()

        return action_result.get_status()

    # implements regex functions for manipulation
    def _re_function(self, param):
        self.debug_print('{}'.format(inspect.stack()[0][3]))

        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        # Set variables
        action = param[PYTHONUTILITIES_REGEX_ACTION]
        pattern = re.compile(param[PYTHONUTILITIES_REGEX_PATTERN])
        data = (param[PYTHONUTILITIES_SOURCE_STRING]).decode('utf8', 'replace')
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

        # Set case structure for defined action
        if action == 'search':
            # Expected result is either string or unicode
            result = pattern.search(data, start, end)
        elif action == 'match':
            # Expected result is either string or unicode
            result = pattern.match(data, start, end)
        elif action == 'split':
            # Expected result is either string or unicode
            result = pattern.split(data)
        elif action == 'findall':
            # Expected result is list
            result = pattern.findall(data, start, end)
        elif action == 'finditer':
            # Expected result is iterator
            result = pattern.finditer(data, start, end)
        elif action == 'sub':
            # Expected result is either string or unicode
            result = pattern.sub(replace, data)
        elif action == 'subn':
            # Expected result is tuple
            result = pattern.subn(replace, data)
        else:
            action_results.set_status(phantom.APP_ERROR, 'Action not defined. Check requested action.')

        # Check to see if there are results then parse the type for formatting
        if result:
            action_result.set_status(phantom.APP_SUCCESS)
            self.debug_print("Type {}".format(type(result)))
            if isinstance(result, (str, unicode, list, dict, tuple)):
                if type(result) is dict:
                    action_result.add_data(result)
                elif type(result) is unicode:
                    self.debug_print("Unicode elif excuted")
                    result_dict = {
                        "result": result.encode('utf8', 'replace')
                    }
                    self.debug_print("{}".format(result_dict))
                    action_result.add_data(result_dict)
                else:
                    result_dict = {
                        "result": result
                    }
                    action_result.add_data(result_dict)
            else:
                action_result.add_data(result.groupdict())

        # action_result.update_summary({"type": str(type(result))})

        return action_result.get_status()

    def _get_substring(self, param):
        self.debug_print('{}'.format(inspect.stack()[0][3]))

        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        try:
            # Find a better way to validate the inputs. Especially if they are left blank.
            sourceString = param[PYTHONUTILITIES_SOURCE_STRING]
            start = 0
            end = len(sourceString) - 1
            step = 1
            if PYTHONUTILITIES_SOURCE_STRING_START in param:
                start = int(param[PYTHONUTILITIES_SOURCE_STRING_START])
            if PYTHONUTILITIES_SOURCE_STRING_END in param:
                end = int(param[PYTHONUTILITIES_SOURCE_STRING_END])
            if PYTHONUTILITIES_SOURCE_STRING_STEP in param:
                step = int(param[PYTHONUTILITIES_SOURCE_STRING_STEP])

            self.debug_print('string {}, start {}, end {}'.format(sourceString, start, end))
            sub_dict = {'substring': sourceString[start:end:step]}

            self.debug_print('substring {}'.format(sub_dict))
            action_result.add_data(sub_dict)
            action_result.set_status(phantom.APP_SUCCESS)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, '', e)
            return action_result.get_status()

        return action_result.get_status()

    def _get_date(self, param):
        self.debug_print('{}'.format(inspect.stack()[0][3]))

        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        format_string = param.get('format_string', "%A, %d %B %Y %I:%M%p")

        # List of local time items
        local_dt = datetime.datetime.now()
        local_iso = local_dt.isocalendar()
        local_tt = local_dt.timetuple()
        local_time = {
            "local_datetime": local_dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "local_year": local_tt[0],
            "local_month": local_tt[1],
            "local_day": local_tt[2],
            "local_hour": local_tt[3],
            "local_minute": local_tt[4],
            "local_second": local_tt[5],
            "local_weekday": local_tt[6],
            "local_day_number": local_tt[7],
            "local_tz": local_tt[8],
            "local_iso_week": local_iso[1],
            "local_iso_weekday": local_iso[2],
            "local_custom": local_dt.strftime(format_string)
        }

        # List of UTC time items
        utc_dt = datetime.datetime.utcnow()
        utc_iso = utc_dt.isocalendar()
        utc_tt = utc_dt.timetuple()
        utc_time = {
            "utc_datetime": utc_dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "utc_year": utc_tt[0],
            "utc_month": utc_tt[1],
            "utc_day": utc_tt[2],
            "utc_hour": utc_tt[3],
            "utc_minute": utc_tt[4],
            "utc_second": utc_tt[5],
            "utc_weekday": utc_tt[6],
            "utc_day_number": utc_tt[7],
            "utc_tz": utc_tt[8],
            "utc_iso_week": utc_iso[1],
            "utc_iso_weekday": utc_iso[2],
            "utc_custom": utc_dt.strftime(format_string)
        }

        # Combine data into one result
        result = local_time.copy()
        result.update(utc_time)

        # Add time values to results
        action_result.add_data(result)
        action_result.set_status(phantom.APP_SUCCESS)

        return action_result.get_status()

    def _offset_date(self, param):
        self.debug_print('{}'.format(inspect.stack()[0][3]))

        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        try:
            date_offset = param.get('date_offset')
            # Splits the string and casts to int for args in timedelta
            date_args = dict([a, int(x)] for a, x in (e.split('=') for e in date_offset.split(', ')))
            date_param = datetime.datetime.strptime(param.get('date'), "%Y-%m-%dT%H:%M:%S")
            # Return date with offset
            result = date_param + datetime.timedelta(**date_args)
            action_result.add_data({ "date": result.strftime("%Y-%m-%dT%H:%M:%S%z") })
            action_result.set_status(phantom.APP_SUCCESS)

        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, '', e)

        return action_result.get_status()

    def _parse_date(self, param):
        self.debug_print('{}'.format(inspect.stack()[0][3]))

        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        try:
            date_string = param.get('date_string')
            format_string = param.get('format_string')

            # List of local time items
            dt = datetime.datetime.strptime(date_string, format_string)
            iso = dt.isocalendar()
            tt = dt.timetuple()
            details = {
                "datetime": dt.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "date": dt.strftime("%Y-%m-%d"),
                "time": dt.strftime("%H:%M:%S"),
                "year": tt[0],
                "month_num": tt[1],
                "month_name": dt.strftime("%B"),
                "month_abbrev": dt.strftime("%b"),
                "day": tt[2],
                "hour": tt[3],
                "minute": tt[4],
                "second": tt[5],
                "weekday_num": tt[6],
                "weekday_name": dt.strftime("%A"),
                "weekday_abbrev": dt.strftime("%a"),
                "day_number": tt[7],
                "tz": tt[8],
                "iso_week": iso[1],
                "iso_weekday": iso[2],
                "custom": dt.strftime(format_string)
            }

            action_result.add_data(details)
            action_result.set_status(phantom.APP_SUCCESS)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, '', e)

        return action_result.get_status()

    def _diff_date(self, param):
        self.debug_print('{}'.format(inspect.stack()[0][3]))

        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        try:
            # get parameters
            start_date = param.get('start_date')
            end_date = param.get('end_date')
            start_format = param.get('start_format')
            end_format = param.get('end_format')

            # get datetime objects
            start_dt = datetime.datetime.strptime(start_date, start_format)
            end_dt = datetime.datetime.strptime(end_date, end_format)

            diff = end_dt - start_dt
            diff_seconds = diff.total_seconds()
            diff_minutes = diff.total_seconds() / 60
            diff_hours = diff.total_seconds() / (60 * 60)
            diff_days = diff.total_seconds() / (60 * 60 * 24)

            self.debug_print("diff - {0}".format(diff))
            self.debug_print("diff - {0}".format(diff_seconds))
            self.debug_print("diff - {0}".format(diff_minutes))
            self.debug_print("diff - {0}".format(diff_hours))
            self.debug_print("diff - {0}".format(diff_days))

            # add results
            action_result.add_data({"difference": str(diff) })
            action_result.add_data({"seconds": str(diff_seconds) })
            action_result.add_data({"minutes": str(diff_minutes) })
            action_result.add_data({"hours": str(diff_hours) })
            action_result.add_data({"days": str(diff_days) })
            action_result.set_status(phantom.APP_SUCCESS)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, '', e)

        return action_result.get_status()

    def _list_functions(self, param):
        self.debug_print('{}'.format(inspect.stack()[0][3]))

        # Add an action result to the App Run
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        try:
            # get all the parameters and define locals
            self.debug_print("Getting parameters...")
            list_1 = ast.literal_eval(param.get('list_1'))
            list_2 = ast.literal_eval(param.get('list_2', '[]'))
            list_value = param.get('list_value')
            list_index = param.get('list_index')

            # currently supported funtions:
            # compare - compares tw0 lists
            # len - returns the length
            # max - returns maximum value
            # min - returns minimum value
            # list - converts a tuple into list
            # append - adds object to list
            # count - counts the number of occurances of x
            # extend - appends seq to list
            # index - returns lowest index of x
            # insert - insert object at offset x
            # pop - removes and returns the last obj
            # remove - removes x from list
            # reverse - reverses the list
            # sort - sorts objest of list

            list_func = param.get('list_function')
            list_results = {}

            self.debug_print("List function picked {}".format(list_func))
            self.debug_print("param type {}".format(type(list_1)))
            self.debug_print("params  {}".format(list_1))

            # Compare function
            if list_func == "cmp":
                # check type of input parameters
                if isinstance(list_1, list) and isinstance(list_2, list):
                    list_results['compare'] = cmp(list_1, list_2)
                    action_result.set_status(phantom.APP_SUCCESS)
                else:
                    action_result.set_status(phantom.APP_ERROR, 'One or more values provided are not of type list')

            # Length function
            elif list_func == "len":
                # check type of input parameters
                if isinstance(list_1, list):
                    self.debug_print(list_1)
                    list_results['length'] = len(list_1)
                    action_result.set_status(phantom.APP_SUCCESS)
                else:
                    action_result.set_status(phantom.APP_ERROR, 'Value provided is not of type list')

            # Max function
            elif list_func == "max":
                # check type of input parameters
                if isinstance(list_1, list):
                    list_results['max'] = max(list_1)
                    action_result.set_status(phantom.APP_SUCCESS)
                else:
                    action_result.set_status(phantom.APP_ERROR, 'Value provided is not of type list')

            # Min function
            elif list_func == "min":
                # check type of input parameters
                if isinstance(list_1, list):
                    list_results['min'] = min(list_1)
                    action_result.set_status(phantom.APP_SUCCESS)
                else:
                    action_result.set_status(phantom.APP_ERROR, 'Value provided is not of type list')

            # Convert function
            elif list_func == "lst":
                # check type of input parameters
                if isinstance(list_1, list):
                    list_results['list'] = list(list_1)
                    action_result.set_status(phantom.APP_SUCCESS)
                else:
                    action_result.set_status(phantom.APP_ERROR, 'Value provided could not be converted to list')

            # Append function
            elif list_func == "app":
                # check type of input parameters
                if isinstance(list_1, list):
                    list_results['list'] = list_1.append(list_value)
                    action_result.set_status(phantom.APP_SUCCESS)
                else:
                    action_result.set_status(phantom.APP_ERROR, 'Value provided is not of type list')

            # Count function
            elif list_func == "cnt":
                # check type of input parameters
                if isinstance(list_1, list):
                    list_results['count'] = list_1.count(list_value)
                    action_result.set_status(phantom.APP_SUCCESS)
                else:
                    action_result.set_status(phantom.APP_ERROR, 'Value provided is not of type list')

            # Extend function
            elif list_func == "ext":
                # check type of input parameters
                if isinstance(list_1, list):
                    list_results['list'] = list_1.extend(list_value)
                    action_result.set_status(phantom.APP_SUCCESS)
                else:
                    action_result.set_status(phantom.APP_ERROR, 'Value provided is not of type list')

            # Index function
            elif list_func == "idx":
                # check type of input parameters
                if isinstance(list_1, list):
                    list_results['list'] = list_1.index(list_value)
                    action_result.set_status(phantom.APP_SUCCESS)
                else:
                    action_result.set_status(phantom.APP_ERROR, 'Value provided is not of type list')

            # Insert function
            elif list_func == "ins":
                # check type of input parameters
                if isinstance(list_1, list) and isinstance(list_index, int):
                    list_results['list'] = list_1.insert(list_index, list_value)
                    action_result.set_status(phantom.APP_SUCCESS)
                else:
                    action_result.set_status(phantom.APP_ERROR, 'Value provided is not of type list or index is not of type int')

            # Pop function
            elif list_func == "pop":
                # check type of input parameters
                if isinstance(list_1, list):
                    list_results['value'] = list_1.pop()
                    list_results['list'] = list_1
                    action_result.set_status(phantom.APP_SUCCESS)
                else:
                    action_result.set_status(phantom.APP_ERROR, 'Value provided is not of type list')

            # Remove function
            elif list_func == "rmv":
                # check type of input parameters
                if isinstance(list_1, list):
                    list_results['list'] = list_1.remove(list_value)
                    action_result.set_status(phantom.APP_SUCCESS)
                else:
                    action_result.set_status(phantom.APP_ERROR, 'Value provided is not of type list')

            # Reverse function
            elif list_func == "rev":
                # check type of input parameters
                if isinstance(list_1, list):
                    list_results['list'] = list_1.reverse()
                    action_result.set_status(phantom.APP_SUCCESS)
                else:
                    action_result.set_status(phantom.APP_ERROR, 'Value provided is not of type list')

            # Sort function
            elif list_func == "srt":
                # check type of input parameters
                if isinstance(list_1, list):
                    list_results['list'] = list_1.sort()
                    action_result.set_status(phantom.APP_SUCCESS)
                else:
                    action_result.set_status(phantom.APP_ERROR, 'Value provided is not of type list')

            action_result.add_data(list_results)
        except Exception as e:
            action_result.set_status(phantom.APP_ERROR, '', e)

        return action_result.get_status()

    def handle_action(self, param):

        ret_val = phantom.APP_SUCCESS
        action = self.get_action_identifier()
        self.debug_print("action_id", self.get_action_identifier())

        if (action == "find_string"):
            ret_val = self._find_string(param)
        elif (action == "item_type"):
            ret_val = self._item_type(param)
        elif (action == "dictionary_to_list"):
            ret_val = self._dictionary_to_list(param)
        elif (action == "item_length"):
            ret_val = self._item_length(param)
        elif (action == "split_string"):
            ret_val = self._split_string(param)
        elif (action == "get_substring"):
            ret_val = self._get_substring(param)
        elif (action == "regex_function"):
            ret_val = self._re_function(param)
        elif (action == "get_date"):
            ret_val = self._get_date(param)
        elif (action == "offset_date"):
            ret_val = self._offset_date(param)
        elif (action == "parse_date"):
            ret_val = self._parse_date(param)
        elif (action == "diff_date"):
            ret_val = self._diff_date(param)
        elif (action == "list_func"):
            ret_val = self._list_functions(param)

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

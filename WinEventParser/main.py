"""import of modules"""
import json
import ctypes
import Helpers
import datetime
import WinOutput
import WinParser
import WinAnalysis
from dateutil import tz


def admin():
    """Function used to check if the person running the Windows environnment is admin"""
    try:
        if ctypes.windll.shell32.IsUserAnAdmin() == 1:
            return True
        else:
            return False
    except NameError:
        return False


def is_valid_char(char):
    """Function to check if each char of timestamp are valid"""
    acceptable_chars = ['-', ' ', ':']
    return char.isdigit() or char in acceptable_chars


def get_string_to_add_to_timestamp(mode):
    """Function used to return the string to add to our timestamp"""
    chars_to_add = ""
    match mode:
        case 2:
            chars_to_add = ":00"
        case 3:
            chars_to_add = ":00:00"
        case 4:
            chars_to_add = " 00:00:00"
        case 5:
            chars_to_add = "-01 00:00:00"
        case 6:
            chars_to_add = "-01-01 00:00:00"
    return chars_to_add


def parse_timestamp(timestamp_to_be_parsed, mode):
    """Function used to parse the input timestamp we had"""
    if timestamp_to_be_parsed is None:
        return None, None
    timestamp_to_be_parsed = ' '.join(timestamp_to_be_parsed.split()[:2])
    if not all(is_valid_char(c) for c in timestamp_to_be_parsed):
        return None, None
    try:
        chars_to_add = get_string_to_add_to_timestamp(mode)
        len_to_remove = len(chars_to_add)
        timestamp_parsed = datetime.datetime.strptime(timestamp_to_be_parsed + chars_to_add, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None, None
    return timestamp_parsed, len_to_remove


def convert_time_in_utc(time_local_timezone):
    """Function used to convert the timestamp we were given in UTC, time zone used by the logs of windows"""
    try:
        time_datetime_type = datetime.datetime.strptime(time_local_timezone, "%Y-%m-%d %H:%M:%S")
        time_utc_raw = time_datetime_type.astimezone(datetime.timezone.utc)
        time_utc = time_utc_raw.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None
    return time_utc


def get_num_of_timestamps(input_mode_timestamp):
    """Function used to get the number of timestamps the user wants to input"""
    if input_mode_timestamp == "two":
        return 2
    return 1


def get_input_mode(iteration_of_for_loop):
    """Function used to get the input mode for a timestamp"""
    mode_to_pass = ""
    mode_to_check = ["1", "2", "3", "4", "5", "6"]
    while mode_to_pass not in mode_to_check:
        mode_to_pass = input(f"[{iteration_of_for_loop}] Please when you input your timestamp do you want to input 1) a full timestamp, 2) a timestamp with date, hour and minute, 3) a timestamp with date and hour, 4) a timestamp with date only, 5) a timestamp with year and month, 6) a timestamp with year (1/2/3/4/5/6): ")
    return int(mode_to_pass)


def second_timestamp_not_greater_than_first_one(timestamp_from_check_function):
    """Function used to check that the second timestamp provided is not greater than the first one"""
    if timestamp_from_check_function[0] > timestamp_from_check_function[1]:
        return True
    return False


def create_current_time():
    """Function used to create a current time suitable to be compared with our timestamp"""
    now = datetime.datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    return current_time


def checking_timestamp(timestamps_provided):
    """Implementing our logic in this function to check if second timestamp is not greater than first one"""
    check = ""
    current_time = create_current_time()
    if len(timestamps_provided) == 2:
        for time_provided in timestamps_provided:
            if time_provided > current_time:
                print("[-] THE TIMESTAMP YOU PROVIDED IS IN THE FUTURE, WHAT ARE YOU DOING ?????")
                check = None
        if second_timestamp_not_greater_than_first_one(timestamps_provided) is True:
            print("[-] FIRST TIMESTAMP YOU INPUTED WAS GREATER THAN THE SECOND ONE, PLEASE INPUT BOTH TIMESTAMPS AGAIN")
            check = None
    else:
        if timestamps_provided[0] > current_time:
            print("[-] THE TIMESTAMP YOU PROVIDED IS IN THE FUTURE, WHAT ARE YOU DOING???")
            check = None
    if check == "":
        return ""
    else:
        return None


def get_input_timestamp(input_mode_timestamp):
    """Function used to get the timestamp the user want to check the events"""
    try:
        num_of_timestamps = get_num_of_timestamps(input_mode_timestamp)
        timestamp_utc = []
        len_timestamp_input = []
        iteration_of_for_loop = 0
        while iteration_of_for_loop != num_of_timestamps:
            iteration_of_for_loop += 1
            input_mode = get_input_mode(iteration_of_for_loop)
            timestamp_parsed = None
            while timestamp_parsed is None:
                prompt = input(f"[{iteration_of_for_loop}] Please input the timestamp to use for searching events: ")
                timestamp_parsed, len_to_remove = parse_timestamp(prompt, input_mode)
            len_timestamp_input.append(len_to_remove)
            timestamp_parsed = str(timestamp_parsed)
            timestamp_utc.append(timestamp_parsed)
            if timestamp_utc is None:
                return None
            if checking_timestamp(timestamp_utc) is None:
                timestamp_utc = []
                len_timestamp_input = []
                iteration_of_for_loop = 0
        return timestamp_utc, len_timestamp_input
    except ValueError as val_err:
        Helpers.exception_handler(True, val_err)
        return None


def get_time_back_in_local(utc_time):
    """Function used to convert back from UTC to local time zone"""
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()                                              # Auto-detect zones:
    utc = datetime.datetime.strptime(utc_time, '%Y-%m-%d %H:%M:%S')
    utc = utc.replace(tzinfo=from_zone)                                 # Tell the datetime object that it's in UTC time zone since datetime objects are 'naive' by default
    local_time = utc.astimezone(to_zone)                                # Convert time zone
    return local_time


def load_rules_list_json(json_event_file):
    """Function used to load our rules from the second json file"""
    try:
        with open(json_event_file, "r", encoding="UTF-8") as json_file:
            data_event_file_json = json.load(json_file)
            return data_event_file_json['rules']
    except IOError as io_err:
        Helpers.exception_handler(True, io_err)
    return None


if __name__ == '__main__':
    if admin() is False:
        print("[-] You should run the script as admin!")
        exit(1)

    input_modes = ["all", "one", "two"]
    input_provided = ""
    while input_provided not in input_modes:
        try:
            input_provided = input("Do you want to input 1) nothing, display all events please, 2) one timestamp that give every events during this time or 3) two timestamps that act as bracket to search for events between two specific times (all/one/two): ")
        except ValueError:
            continue
    if input_provided != "all":
        timestamp_raw, len_to_remove_to_timestamp = get_input_timestamp(input_provided)
        if timestamp_raw is None:
            print("[-] You should try to run the script and input a timestamp again.")
            exit(1)
        num_timestamp_factoring = 0
        if input_provided == "one":
            num_timestamp_factoring = 1
        elif input_provided == "two":
            num_timestamp_factoring = 2
        if num_timestamp_factoring != 0:
            timestamp = ["", ""]
            number_of_occurences = ["", ""]
            for n_t_f in range(0, num_timestamp_factoring):
                timestamp[n_t_f] = timestamp_raw[n_t_f]
                timestamp_temp = ["", ""]
                counting_char_timestamp = 0
                for t in timestamp[n_t_f]:
                    if counting_char_timestamp != 19 - len_to_remove_to_timestamp[n_t_f]:
                        timestamp_temp[n_t_f] += t
                        counting_char_timestamp += 1
                timestamp[n_t_f] = timestamp_temp[n_t_f]
                number_of_occurences[n_t_f] = len_to_remove_to_timestamp[n_t_f]

    if input_provided != "all":
        print("[*] Launching our engine and starting to search events, please wait...")
        interesting_event_list = WinParser.WinParserMain(input_provided, timestamp, number_of_occurences)
        print("[+] Parsing is done.")
        if interesting_event_list is None:
            print("[-] The checking rules engine return an exception.")
            exit(1)

        rules = load_rules_list_json("AnalysisRules.json")
        if rules is None:
            print("[-] The file provided in the script can't be open.")
            exit(1)

        print("[*] Launching the analysis engine, please wait...")

        interesting_event_list = WinAnalysis.analysis_engine(interesting_event_list, rules)

        if interesting_event_list is None:
            print("[-] The Analysis engine return an exception.")
            exit(1)

        print("[+] Analysis is done.")

        WinOutput.WinOutputMain(interesting_event_list)
    else:
        WinParser.WinParserMain(input_provided, None, None)
    exit(0)
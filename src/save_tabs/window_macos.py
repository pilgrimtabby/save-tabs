"""Return a list of Window objects, one for each open Chrome window
selected by the user.

This module is macOS-only. For Windows code, see window_windows.py.

Each Window object has a .mode attribute and a .urls attribute (see
namedtuple documentation in window_windows.py).

Functions:
    get_window_list() -> list
    get_window_mode(index: int) -> str
    get_window_urls(index: int) -> list
    get_window_count() -> int
    choose_windows(window_list: list) -> list
    print_urls(urls: list)
    confirm(chosen_windows: list, chosen_indexes: list) -> bool
"""
import os
import subprocess
import time
import common
import settings
from window_windows import Window


def get_window_list():
    """Return a list of Window objects.

    If get_window_count() returns 0, return None (after the user 
    optionally accesses the settings menu).
    The program will exit after the return call (see main.py).

    Else if get_window_count() returns 1, skip choose_windows(). Just
    ask the user directly if they want to save that window.

    Otherwise, return output of selected_windows.

    Returns:
        list | None: List of Window objects. Returns None if no Chrome
            windows are open.
    """
    window_count = get_window_count()

    if window_count == 0:
        header = common.box("Save tabs | No windows open")
        keep_going = True
        while keep_going:
            common.clear()
            user_choice = input(f"{header}\n\nNo Chrome windows found!\n"
                                "Press \"s\" for settings, or enter to exit: ").lower().strip()
            if user_choice == "s":
                settings.main()
            else:
                keep_going = False
        common.clear()
        return None

    window_list = []
    for i in range(1, window_count + 1):
        window_mode = get_window_mode(i)
        window_urls = get_window_urls(i)
        window_list += [Window(window_mode, window_urls)]

    if window_count == 1:
        save_only_window = confirm(window_list, [1])
        if save_only_window:
            return window_list
        common.clear()
        return None

    return choose_windows(window_list)


def get_window_count():
    """Return total of currently open Chrome windows.
    
    Returns:
        int: Number of open windows.
    """
    program_path = os.path.dirname(os.path.realpath(__file__))
    script = f"{program_path}/scripts/applescript/get_window_count.applescript"

    window_count = subprocess.check_output(["osascript", script]).decode("UTF-8")
    if window_count == "":  # Chrome not running
        return 0
    return int(window_count)


def get_window_mode(index):
    """Returns window's mode (normal or incognito).

    Args:
        index (int): The index of the window being acted on.

    Returns:
        mode (str): "incognito" if window is incognito.
            "normal" otherwise.
    """
    program_path = os.path.dirname(os.path.realpath(__file__))
    script = f"{program_path}/scripts/applescript/get_window_mode.applescript"
    # Return string result of Applescript with newlines stripped
    mode =  subprocess.check_output(["osascript", script, str(index)]).decode("UTF-8").strip("\n")

    # Default to incognito window if something goes wrong
    if "normal" not in mode and "incognito" not in mode:
        return "incognito"
    return mode


def get_window_urls(index):
    """Return list of tab urls from a Chrome window.

    The return type of the subprocess.check_output call is a string,
    so calling .split(", ") is necessary to get a list.
    
    Args:
        index (int): The index of the window being acted on.

    Returns:
        list: List of urls from the window.
    """
    program_path = os.path.dirname(os.path.realpath(__file__))
    script = f"{program_path}/scripts/applescript/get_window_urls.applescript"

    window_urls_string = (subprocess.check_output(["osascript", script, str(index)])
                          .decode("UTF-8").strip("\n"))
    return window_urls_string.split(", ")


def choose_windows(window_list):
    """Prompt user to choose which windows to save.

    If a user enters something besides an int, a comma, or a space, the
    loop repeats.

    After user makes choice, ask to confirm.

    If the user has more than one session of Chrome open, only one
    session's windows will appear here. There appears to be no way
    around this beyond copying Chrome and making a custom app for each
    instance (!) when opening a separate instance, which is beyond the
    pale, at least for now.

    Args:
        window_list (list): Complete list of Window objects.

    Returns:
        chosen_windows (list): Window objects chosen by user.
    """
    keep_going = True
    while keep_going:
        keep_going = False
        common.clear()
        header = common.box("Save tabs | Select windows")
        print(f"{header}\n")
        for i, window in enumerate(window_list, start=1):
            if window.mode == "incognito":
                print(f"{i} ({window.mode})")
            else:
                print(i)
            print_urls(window.urls)

        user_input = input("Your choice (separate w/ commas; blank to save all): "
                           ).strip()

        if user_input == "":
            return window_list

        chosen_indexes = [x for x in user_input.replace(" ", ",").split(",") if x]
        chosen_windows = []
        for index in chosen_indexes:
            if not index.isdigit():
                keep_going = True
                print("Invalid selection: enter only numbers, spaces, and commas.")
                time.sleep(2)
                break
            if index.isdigit() and not 0 < int(index) <= len(window_list):
                keep_going = True
                print("Invalid selection: do not enter numbers out of range.")
                time.sleep(2)
                break
            chosen_windows += [window_list[int(index) - 1]]

        # If all indexes valid
        else:
            confirmation = confirm(chosen_windows, chosen_indexes)
            if not confirmation:
                keep_going = True

    return chosen_windows


def print_urls(urls):
    """Print up to four labelled, abbreviated urls from a window.
    
    Args:
        urls (list): window.urls from a Window object.
    """
    if len(urls) > 5:
        urls_to_print = urls[:4]
        unprinted_url_count = len(urls) - 4
    else:
        urls_to_print = urls
        unprinted_url_count = 0
    for url in urls_to_print:
        if len(url) > 76:
            print(f"{url[:76]}...")
        else:
            print(url)
    if unprinted_url_count > 0:
        print(f"...and {unprinted_url_count} other tabs")
    print()


def confirm(chosen_windows, chosen_indexes):
    """Prompt user to confirm their choice from choose_windows().
    
    Args:
        chosen_windows (list): List of chosen Window objects.
        chosen_indexes (list): List of indexes of chosen Window objects
            from the original window_list in choose_windows. These are
            printed so the user can see which windows they chose on the
            previous screen.
    
    Returns:
        bool: True if user confirms selection, False otherwise.
    """
    header = common.box("Save tabs | Select windows")
    common.clear()
    print(f"{header}\n")
    for i, window in enumerate(chosen_windows):
        if window.mode == "incognito":
            print(f"{chosen_indexes[i]} ({window.mode})")
        else:
            print(chosen_indexes[i])
        print_urls(window.urls)

    if len(chosen_windows) == 1:
        confirmation = (input("Save this window? Type \"y\" to confirm (press enter to go "
                                "back): ").lower().strip())
    else:
        confirmation = (input("Save these windows? Type \"y\" to confirm (press enter to go "
                                "back): ").lower().strip())
    if confirmation == "y":
        return True
    return False

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
"""
import os
import subprocess
import common
from window_windows import Window


def get_window_list():
    """Return a list of Window objects.

    If get_window_count() returns 0, return None.
    The program will exit after the return call (see main.py).

    Otherwise, return output of selected_windows.
    
    Returns:
        list | None: List of Window objects. Returns None if no Chrome
            windows are open.
    """
    window_count = get_window_count()
    if window_count == 0:
        header = common.box("Save tabs | No windows open")
        common.clear()
        input(f"{header}\n\nNo Chrome windows found!\n"
              "Press any key to exit: ")
        common.clear()
        return None

    window_list = []
    for i in range(1, window_count + 1):
        window_mode = get_window_mode(i)
        window_urls = get_window_urls(i)
        window_list += [Window(window_mode, window_urls)]

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
    mode =  subprocess.check_output(["osascript", script, index]).decode("UTF-8").strip("\n")

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

    window_urls_string = (subprocess.check_output(["osascript", script, index])
                          .decode("UTF-8").strip("\n"))
    return window_urls_string.split(", ")


def choose_windows(window_list):
    """Prompt user to choose which windows to save.

    If a user enters something besides an int, a comma, or a space, the
    loop repeats.

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
    invalid_choice = False
    while not invalid_choice:
        invalid_choice = False
        common.clear()
        for i, window in enumerate(window_list):
            if window is not None:
                print(f"{i + 1} ({window.mode})")
                print("\n".join(window.urls))
                print()

        header = common.box("Save tabs | Select windows")
        user_input = (f"{header}\n\nSave which windows? Separate numbers with spaces or commas.\n"
                      "Enter your choice (press enter to save all): ").strip()

        if user_input == "":
            return window_list

        indexes = user_input.replace(" ", ",").split(",")
        chosen_windows = []
        for index in indexes:
            if (not index.isdigit and index != ""
                or index.isdigit and not 0 < int(index) <= len(window_list)):
                print("Invalid selection: enter only numbers in range, spaces, and commas.")
                invalid_choice = True
            if index != "":
                chosen_windows += [window_list[int(index) - 1]]

    return chosen_windows

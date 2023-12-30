"""Return the path to chrome.exe (Windows) or Google Chrome (macOS).

Windows: Iterate through every Chrome installation path since Windows
    XP until one exists. If that doesn't work, ask the user to select
    chrome.exe. If they don't, return None.
macOS: Check Chrome's erstwhile installation location. If it's not
    there, open Chrome (if it's not open already) and use an
    applescript to return the path. If that somehow doesn't work, ask
    the user to select it. If they don't, return None.

Functions:
    get_chrome_path() -> str | None
    prompt_user_for_chrome_path() -> str | None
    get_window_count() -> int
"""
import os
import platform
import subprocess
import common


def get_chrome_path():
    """Get the path to chrome.exe (Windows) or Google Chrome (macOS).
    
    Returns:
        None if all methods of finding the Chrome path fail.
        str (the path) if one of the methods succeeds.
    """
    if platform.system() == "Windows":
        possible_chrome_paths = ["C:/Program Files/Google/Chrome/Application/chrome.exe",
                                 "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
                                 "C:/Program Files (x86)/Google/Application/chrome.exe",
                                 "C:/Users/UserName/AppDataLocal/Google/Chrome/chrome.exe",
                                 "C:/Documents and Settings/UserName/Local Settings/"
                                 "Application Data/Google/Chrome/chrome.exe"]
        for chrome_path in possible_chrome_paths:
            if os.path.exists(chrome_path):
                return chrome_path

        return prompt_user_for_chrome_path()

    # macOS
    default_chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if os.path.exists(default_chrome_path):
        return default_chrome_path

    # This code is in a try block because sometimes, the Applescripts
    # can throw weird errors. I think it's easier in those cases to
    # ask the user directly to select Chrome.
    try:
        program_path = os.path.dirname(os.path.realpath(__file__))
        if get_window_count() == 0:
            script = f"{program_path}/scripts/applescript/get_chrome_path_if_not_open.applescript"
            chrome_path_raw = subprocess.check_output(["osascript", script])
        else:
            script = 'POSIX path of (path to application id "com.google.Chrome")'
            chrome_path_raw = subprocess.check_output(["osascript", "-e", script])
        chrome_path_parsed = chrome_path_raw.decode("UTF-8").replace("/n", "")
        chrome_path = f"{chrome_path_parsed}Contents/MacOS/Google Chrome"

        if os.path.exists(chrome_path):
            return chrome_path
        return None

    except:
        return prompt_user_for_chrome_path()


def prompt_user_for_chrome_path():
    """Prompt user to chrome.exe / Google Chrome.app.
    
    Returns:
        None if the user clicks cancel or chooses the wrong file.
        str (path to Chrome) if the user selects the right file.
    """
    if platform.system() == "Windows":
        chrome_name = "chrome.exe"
        subdirectories = ""
    else:
        chrome_name = "Google Chrome.app"
        subdirectories = "/Contents/MacOS/Google Chrome"

    header = common.box("Save tabs | Chrome path")
    common.clear()
    print(f"{header}\n\nUnable to find {chrome_name}. Please select it:")
    chrome_path = common.get_file_path(file_type="file")
    chrome_path_file_name = os.path.basename(os.path.normpath(chrome_path))

    if chrome_path_file_name == chrome_name:
        full_chrome_path = f"{chrome_path}{subdirectories}"
        if os.path.exists(full_chrome_path):
            return full_chrome_path

    return None


def get_window_count():
    """Uses Applescript to get number of open Chrome windows on macOS.

    Returns:
        window_count (int): The number of open Chrome windows of the
            most recently opened Chrome session."""
    program_path = os.path.dirname(os.path.realpath(__file__))
    script = f"{program_path}/scripts/applescript/get_window_count.applescript"
    window_count = subprocess.check_output(['osascript', script]).decode("UTF-8")
    if window_count == "":  # Chrome not running
        return 0
    return int(window_count)

"""Return a list of Window objects, one for each open Chrome window.

This module is Windows-only. For macOS code, see window_macos.py.

Each Window object has a .mode attribute and a .urls attribute (see
namedtuple documentation below).

Named tuples:
    Window(mode: str, urls: list)

Functions:
    get_window_list() -> list | None
    get_program_pycwnd() -> PyCWnd | None
    get_chrome_pycwnd() -> PyCWnd
    test_click()
    get_window_mode(program_pycwnd: PyCWnd) -> str
    get_window_urls(chrome_pycwnd: PyCWnd) -> list | None

    ensure_chrome_in_front(target_window: PyCWnd, func: funtion)
    open_first_tab()
    empty_clipboard()
    refresh_page()
    select_url()
    copy_to_clipboard()
    open_next_tab()

    ask_if_continue(program_pycwnd: PyCWnd) -> bool
"""
import collections
import platform
import time

if platform.system() == "Windows":
    import pyautogui
    import pyperclip
    import win32ui

import common
import settings


Window = collections.namedtuple("Window", "mode urls")
Window.__doc__ = """\
Contain a window's mode (normal / incognito) and its url list.

Args:
    mode (str): The window's mode. Possible args are "normal" and
        "incognito".
    urls (list): The window's tab urls (strings).
"""


def get_window_list():
    """Return a list of Window objects.

    If user doesn't accept the disclaimer in get_chrome_pycwnd(), exit
    the program.

    If window_list is None, the program will exit after the return
    call (see main.py).
    
    Returns:
        window_list (list | None): List of Window objects.
            Returns None if user quits in get_program_pycwnd().
    """
    program_pycwnd = get_program_pycwnd()
    if program_pycwnd is None:
        return None

    window_list = []
    keep_going = True
    while keep_going:
        chrome_pycwnd = get_chrome_pycwnd()

        window_mode = get_window_mode(program_pycwnd)

        common.focus_window(chrome_pycwnd)
        window_urls = get_window_urls(chrome_pycwnd)
        if window_urls is not None:
            window_list += [Window(window_mode, window_urls)]

        keep_going = ask_if_continue(program_pycwnd)

    return window_list


def get_program_pycwnd():
    """Prompt user to accept disclaimer / get program's PyCWnd object.
    
    If the user types "y", this brings the program window to the front,
    which means win32ui.GetForegroundWindow() should always return a
    object pointing to the program window.

    If the user types "s", bring up the settings menu.

    Returns:
        program_window (PyCWnd object | None): The program window.
            Return None if the user doesn't accept the disclaimer.
    """
    header = common.box("Save tabs | Disclaimer")
    program_window = None
    keep_going = True

    while keep_going:
        common.clear()
        accept = input(f"{header}\n\nPlease make sure the Chrome window you want to save is open "
                        "and snapped to the left side of the screen!\n\n"

                        "Please note this program refreshes your tabs, so make sure to save your "
                        "work.\n"
                        "This program simulates a click at (1, 0) (top left corner) to bring "
                        "Google Chrome into focus.\n"
                        "It also uses keyboard scripting to gather urls.\n"
                        "These are the keyboard shortcuts used:\n\n"

                        "ctrl+1 (to navigate to the first tab)\n"
                        "ctrl+l (to select the url of each tab)\n"
                        "ctrl+c (to copy the url of each tab)\n"
                        "ctrl+r (to refresh tabs)\n"
                        "ctrl+tab (to switch between tabs)\n\n"

                        "If you have rebinded any of these shortcuts or don't accept these terms, "
                        "you've been warned!\n\n"

                        "To proceed, enter \"y\" (enter \"s\" for settings): ").lower().strip()
        if accept == "y":
            program_window = win32ui.GetForegroundWindow()
            common.clear()
            return program_window
        if accept == "s":
            settings.main()
        else:
            keep_going = False
            common.clear()
            return None


def get_chrome_pycwnd():
    """Bring Chrome to the foreground and create a PyCWnd object.

    Using this object later ensures that key bindings are only
    executed when Chrome is in front.
    
    Returns:
        foreground_window (PyCWnd object): The Chrome window.
    """
    header = common.box("Save tabs | Verifying setup")
    common.clear()
    print(f"{header}\n\nChecking Chrome's location...")

    while True:
        test_click()
        foreground_window = win32ui.GetForegroundWindow()
        if "Google Chrome" in foreground_window.GetWindowText():
            return foreground_window
        input("\nLooks like Google Chrome isn't in the right spot. Make sure it's snapped "
              "to the left side of the screen, then click here and press enter: ")


def test_click():
    """Click at (1, 0) to focus Chrome (which should be snapped left).
    
    Immediately after the click, attempt to move the mouse back to
    its original position.
    
    PyAutoGUI won't generally move the mouse into a corner, hence the
    try block.
    """
    original_mouse_position = pyautogui.position()
    try:
        pyautogui.click(1, 0)
        pyautogui.moveTo(original_mouse_position)
    except pyautogui.FailSafeException:
        pass


def get_window_mode(program_pycwnd):
    """Prompt user to enter current Chrome window's mode.

    Args:
        program_pycwnd (PyCWnd object): The program window. Used to
            focus the program so the user can type easily.

    Returns:
        str: "incognito" if user says window is incognito.
             "normal" otherwise.
    """
    header = common.box("Save tabs | Window mode")

    common.clear()
    common.focus_window(program_pycwnd)
    is_window_incognito = input(f"{header}\n\nIs this window incognito? If so, enter \"y\" "
                                "(otherwise press enter): ").lower().strip()

    if is_window_incognito == "y":
        return "incognito"
    return "normal"


def get_window_urls(chrome_pycwnd):
    """Scrape tabs from a Chrome window.

    Once the function finds 2 repeat urls, it assumes all urls have
    been collected.

    The function saves urls even if they are blank. It strips out blank
    urls once collection is complete. This is important because if a
    window is empty or something goes wrong, the function would
    continue indefinitely otherwise.
    
    Returns:
        window_urls (list): List of urls.
    """
    header = common.box("Save tabs | Getting tab urls")
    common.clear()
    print(f"{header}\n\nWorking... (don't click anywhere!)")

    time.sleep(0.1)
    ensure_chrome_in_front(chrome_pycwnd, open_first_tab)

    window_urls = []
    repeat_urls = 0

    while repeat_urls < 2:
        ensure_chrome_in_front(chrome_pycwnd, empty_clipboard)
        ensure_chrome_in_front(chrome_pycwnd, refresh_page)
        url = ""
        tries = 0
        while url == "" and tries < 20:  # Allow 10s for refresh
            time.sleep(0.5)
            ensure_chrome_in_front(chrome_pycwnd, select_url)
            ensure_chrome_in_front(chrome_pycwnd, copy_to_clipboard)
            url = pyperclip.paste()
            tries += 1
        ensure_chrome_in_front(chrome_pycwnd, open_next_tab)
        if url not in window_urls:
            window_urls += [url]
        else:
            repeat_urls += 1

    window_urls = [x for x in window_urls if x]  # Strip blank entries ("")

    if len(window_urls) == 0:
        print("\nSomething went wrong: 0 tab urls gathered.")
        return None

    if len(window_urls) == 1:
        print("\n1 tab url successfully gathered!")
    else:
        print(f"\n{int(len(window_urls))} tab urls successfully gathered!")
    return window_urls


def ensure_chrome_in_front(target_window, func):
    """Make sure Chrome is in focus before executing func."""
    header = common.box("Save tabs | Getting tab urls")
    first_try = True
    foreground_window = win32ui.GetForegroundWindow()

    while foreground_window != target_window:
        if first_try:
            common.clear()
            input(f"{header}\n\nOperation paused: Chrome is no longer in focus.\n"
                "Snap the window to the left side of the screen, then click here and press "
                "enter: ")
            first_try = False
        else:
            input("\nChrome still not detected. Try again, then click here and press enter: ")
        test_click()
        foreground_window = win32ui.GetForegroundWindow()
        if foreground_window == target_window:
            common.clear()
            print(f"{header}\n\nWorking... (don't click anywhere!)")

    func()


def open_first_tab():
    """Go to first tab in Chrome window (input ctrl + 1)."""
    pyautogui.hotkey("ctrl", "1")


def empty_clipboard():
    """Put empty string in clipboard to avoid duplicate url issues."""
    pyperclip.copy("")


def refresh_page():
    """Refresh a Chrome tab (input ctrl + r)."""
    pyautogui.hotkey("ctrl", "r")


def select_url():
    """Highlight a tab's url (input ctrl + l)."""
    pyautogui.hotkey("ctrl", "l")


def copy_to_clipboard():
    """Copy text to the clipboard (input ctrl + c)."""
    pyautogui.hotkey("ctrl", "c")


def open_next_tab():
    """Go to next tab in Chrome window (input ctrl + tab)."""
    pyautogui.hotkey("ctrl", "tab")


def ask_if_continue(program_pycwnd):
    """Prompt user to save additional window(s) if desired. 
    
    Args:
        program_pycwnd (PyCWnd object): The program window. Used to
            focus the program so the user can type easily.
            
    Returns:
        bool: True if user requests another window, False otherwise.
    """
    common.focus_window(program_pycwnd)
    keep_going = input("Save another window's tabs?\n\n"
                       "If yes, snap that window to the left side of the screen, then enter "
                       "\"y\". Otherwise, press enter: ").lower().strip()

    if keep_going == "y":
        return True
    return False

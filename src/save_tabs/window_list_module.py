"""Returns a list of urls (the Google Chrome tabs that are opened), separated into windows."""
import collections
import platform
import subprocess
import time

if platform.system() == "Windows":
    import pyautogui
    import pyperclip
    import win32ui

import advanced_cursor
import common

Window = collections.namedtuple("Window", "type urls")
"""Named tuple to hold a window's type (regular vs. incognito) and its url list."""


def get_window_list():
    """Returns a list containing all open Google Chrome tab urls, divided into sub-lists, each one
    representing a Chrome window. The first index of each sublist contains either the word 
    "regular" (indicating the preceding tabs are part of a regular window) or "incognito" 
    (indicating the preceding tabs are part of an incognito window)."""
    if platform.system() == "Windows":
        user_consent = get_user_consent_windows()
        if user_consent is None:
            return None

        program_window = win32ui.GetForegroundWindow()
        window_list = []
        keep_going = True
        while keep_going:
            focus_chrome_window()
            window_type = get_window_type()
            tab_urls = get_tab_urls()
            window_list += [Window(window_type, tab_urls)]

            common.focus_window(program_window)
            keep_going = ask_if_continue()

        return window_list

    # macOS
    window_count = get_window_count()
    if window_count == 0:  # Exit if Chrome not open / no windows open
        advanced_cursor.hide()
        common.clear()
        print("\n\n\n\n\n\n\n\n\n"
            "           No Chrome windows found!\n"
            "           Press any key to exit...")
        common.get_one_char()
        common.clear()
        advanced_cursor.show()
        return None

    window_list = []
    for i in range(1, window_count + 1):
        window_type = get_window_type(i)
        tab_urls = get_tab_urls(i)
        window_list += [Window(window_type, tab_urls)]
    if window_count == 1:
        return window_list
    selected_windows = select_windows(window_list)
    return selected_windows


def get_user_consent_windows():
    """Print warning message/ confirmation screen and get user assent."""
    common.clear()
    header = common.box("Save tabs | Disclaimer")
    consent = input(f"{header}\n\nPlease make sure the Chrome window you want to save is open and "
                    "snapped to the left side of the screen!\n\n"

                    "Please note that this program uses keyboard scripting to gather urls.\n"
                    "These are the keyboard shortcuts used:\n"
                    "ctrl+l (to select the url of each tab)\n"
                    "ctrl+c (to copy the url of each tab)\n"
                    "ctrl+r (to refresh tabs if necessary)\n"
                    "If you have rebinded any of these shortcuts, or don't want to use a "
                    "program using keyboard scripting, please exit now!\n\n"

                    "Otherwise, enter \"yes\" when you're ready: ").lower()
    if not consent == "yes":
        common.clear()
        return None
    return 0


def focus_chrome_window():
    """Make sure Chrome is actually in the foreground and in the correct position (left side of
    screen)."""
    header = common.box("Save tabs | Verifying setup")
    print(f"{header}\n\nThis program will simulate a mouse click to check Google Chrome's "
          "location. Hang on...")
    time.sleep(1)

    foreground_window_text = ""
    while "Google Chrome" not in foreground_window_text:
        current_mouse = pyautogui.position()
        pyautogui.click(200, 0)  # Click on top left of screen to focus Chrome
        pyautogui.moveTo(current_mouse)  # Restore mouse position
        foreground_window = win32ui.GetForegroundWindow()
        if "Google Chrome" not in foreground_window.GetWindowText():
            input("\nLooks like Google Chrome isn't in the right spot. Make sure it's snapped "
                  "to the left side of the screen, then click here and press enter: ")


def get_window_type(window=None):
    """Returns string "incognito" if Chrome window is incognito, otherwise returns "regular"."""
    if platform.system() == "Windows":
        header = common.box("Save tabs | Window type")
        common.clear()
        is_window_incognito = input(f"{header}\n\nTo save this window as incognito (as opposed to "
                                    "regular), enter \"yes\"; otherwise, press enter: ").lower()
        if is_window_incognito == "yes":
            return "incognito"
        return "regular"

    # macOS
    get_window_type_script = '''
    if application id "com.google.Chrome" is running then tell application id "com.google.Chrome"
        if mode of window ''' + str(window) + ''' = "incognito" then
            return "incognito"
        else
            return "regular"
        end if
    end tell
    '''
    # Return string result of Applescript with newlines removed
    return (subprocess.check_output(['osascript', '-e', get_window_type_script])
            .decode("UTF-8").replace("\n", ""))


def get_tab_urls(window=None):
    """Scrapes tabs from a given Chrome window and returns them as a list."""
    if platform.system() == "Windows":
        header = common.box("Save tabs | Getting tab urls")
        common.clear()
        print(f"{header}\n\nWorking... (don't click anywhere!)")

        tab_urls = []
        repeats = 0
        while repeats <= 2:  # One tab might be a genuine duplicate, but 2 in a row = all tabs done
            pyautogui.hotkey("ctrl", "r")  # Refresh page (resets text in url bar)
            time.sleep(1)
            pyautogui.hotkey("ctrl", "l")  # Select url
            pyautogui.hotkey("ctrl", "c")  # Copy to clipboard
            url = pyperclip.paste()
            pyautogui.hotkey("ctrl", "tab")  # Move to next tab
            if not url in tab_urls:
                tab_urls += [url]  # Only save unique urls
            else:
                repeats += 1

        print("\nTabs successfully gathered!")
        return tab_urls

    # macOS
    get_tab_urls_script = '''
    if application id "com.google.Chrome" is running then tell application id "com.google.Chrome"
        return (URL of tabs of window ''' + str(window) + ''' as list)
    end tell
    '''
    # Return output (tab urls) as string and strip newlines
    tab_urls_string = subprocess.check_output(['osascript', '-e',
                                          get_tab_urls_script]).decode("UTF-8").replace("\n", "")
    tab_urls = tab_urls_string.split(", ")
    return tab_urls


def ask_if_continue():
    """Allow user to save additional window(s). Returns true if another window is requested."""
    keep_going = input("Save another window's tabs?\n\n"
                       "If yes, snap that window to the left side of the screen, then enter "
                       "\"yes\". Otherwise, press enter: ").lower()
    if keep_going == "yes":
        return True
    return False


def get_window_count():
    """Uses Applescript to get number of currently open Chrome windows (macOS only)."""
    get_window_count_script = '''
    if application id "com.google.Chrome" is running then tell application id "com.google.Chrome"
        set window_count to the index of windows whose visible is true
        return (number of items in window_count)
    end tell
    '''
    # Run script, convert output from byte to string
    window_count = subprocess.check_output(['osascript', '-e',
                                            get_window_count_script]).decode("UTF-8")
    if window_count == "":  # Chrome not running
        return 0
    return int(window_count)


def select_windows(window_list):
    """Ask user to select which groups of tabs from tab_list to keep. Returns the selection."""
    window_count = len(window_list)
    selected_window_indexes = []
    selected_windows = []
    selection_complete = False
    advanced_cursor.hide()

    while not selection_complete:
        common.clear()
        header = common.box(f"Save tabs | Select windows | Selected: {selected_window_indexes}")
        # Print instructions
        print(f"{header}\n\nType the number ID of each window you want, then press enter.\n"
              "(Or just press enter to save all windows.)\n")

        # Print available tab/ window options
        for i, window in enumerate(window_list):
            if window is not None:  # Don't print windows that have already been selected
                print(f"{i + 1} ({window.type})")
                print("\n".join(window.urls))
                print()

        # Prompt user input
        user_input = common.get_one_char()

        # Chosen window
        if (user_input.isdigit()
            and 0 < int(user_input) <= window_count
            and int(user_input) not in selected_window_indexes):
            # Move index of chosen window to selected_window_indexes, and chosen window to
            # selected_windows, if chosen_window is a valid choice
            selected_window_indexes += [int(user_input)]
            selected_windows += [window_list[int(user_input) - 1]]
            # Replace chosen window with None in window_list
            window_list[int(user_input) - 1] = None
            # Move on if all windows selected
            if len(selected_windows) == window_count:
                selection_complete = True

        # If user presses enter, confirm choice if at least 1 window is chosen, or choose all if
        # no window has been chosen yet
        elif user_input == "\r":
            if len(selected_window_indexes) == 0:
                selected_windows = window_list
            selection_complete = True

        # Backspace undoes most recent choice
        elif (user_input == '\177' or user_input == '\b') and len(selected_window_indexes) > 0:
            # Get index of most recent saved window
            return_to_windows_list_index = selected_window_indexes.pop() - 1
            # Remove that window from selected_windows and put it back into windows_list
            window_list[return_to_windows_list_index] = selected_windows.pop()

    advanced_cursor.show()
    return selected_windows

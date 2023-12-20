"""Returns a list of urls (the Google Chrome tabs that are opened), separated into windows."""
import platform
import subprocess
import time

if platform.system() == "Windows":
    import pyautogui
    import pyperclip
    import win32ui

import advanced_cursor
import common


def get_window_list():
    """Returns a list containing all open Google Chrome tab urls, divided into sub-lists, each one
    representing a Chrome window. The first index of each sublist contains either the word 
    "regular" (indicating the preceding tabs are part of a regular window) or "incognito" 
    (indicating the preceding tabs are part of an incognito window)."""
    if platform.system() == "Windows":
        window_list = get_window_list_windows()
    else:
        advanced_cursor.hide()
        window_list = get_window_list_mac()
        advanced_cursor.show()
    return window_list


def get_window_list_windows():
    """Make sure user is all right with keyboard scripting, then call the function that gathers
    tab urls from an open Chrome window."""
    # Warning message/ confirmation screen
    consent = input("Please make sure the Chrome window you want to save is open and snapped to "
                    "the left side of the screen!\n\n"

                    "Please note that this program uses keyboard scripting to gather urls.\n"
                    "These are the keyboard shortcuts used:\n"
                    "ctrl+l (to select the url of each tab)\n"
                    "ctrl+c (to copy the url of each tab)\n"
                    "ctrl+r (to refresh tabs if necessary)\n"
                    "If you have rebinded any of these shortcuts, or just don't want to use a "
                    "program using keyboard scripting, please exit now!\n\n"

                    "Otherwise, click this window, type \"yes\", and press enter to proceed when "
                    "you're ready: ").lower()
    if not consent == "yes":
        common.exit_screen_interrupt()
        return None

    # Get tabs from each Chrome window
    keep_going = True
    window_list = []
    while keep_going:
        pyautogui.click(200, 0)  # Click on top left of screen to focus the window on Chrome
        # Make sure Chrome is actually in foreground
        foreground_window = win32ui.GetForegroundWindow().GetWindowText()
        if not foreground_window == "Google Chrome":
            input("Looks like Google Chrome isn't in the right spot. Make sure it's snapped "
                    "to the left side of the screen, then click here and press enter.")
            continue

        tab_list = scrape_window_urls()
        window_list += [tab_list]

        # Ask if user wants to save another window
        one_more = input("Save another window's tabs?\n\nIf yes, Please make sure the window "
                            "you want to save is open and snapped to the left side of the "
                            "screen. Then click here, type \"yes\", and press enter.").lower()
        if not one_more == "yes":
            keep_going = False

    return window_list


def scrape_window_urls():
    """Uses keboard scripting to fetch Chrome urls individually from an open window. Requires
    the window to be present at (200, 0) on the screen -- best way to do this is to snap the
    window to the left side of the screen. """
    tab_list = []
    # Confirm window type before gathering tab information
    is_window_incognito = input("Would you like to save this as an incognito window (as "
                                "opposed to a regular window)? If so, enter \"yes\"; "
                                "otherwise, press enter.").lower()
    if is_window_incognito == "yes":
        tab_list += "incognito"
    else:
        tab_list += "regular"

    pyperclip.copy("")  # Make sure clipboard is empty
    repeated_tabs = 0
    while repeated_tabs < 3:
        pyautogui.hotkey('ctrl', 'l')  # Select url
        pyautogui.hotkey('ctrl', 'c')  # Copy to clipboard
        url = pyperclip.paste()
        # If the text selected doesn't start like a typical url, refresh the page to see
        # if the problem is fixed (e.g. if user previously typed something in the url bar).
        # The goal is to capture the tab's actual url.
        if not url.startswith("https://") or not url.startswith("http://"):
            pyautogui.hotkey('ctrl', 'r')
            time.sleep(1)
            pyautogui.hotkey('ctrl', 'l')
            pyautogui.hotkey('ctrl', 'c')
            url = pyperclip.paste()
        # If the tab has already been added to the list, increment repeated_tabs. If it
        # gets to 3, treat the program like it's already copied all the tab urls in the
        # window.
        if url not in tab_list:
            tab_list += url
        else:
            repeated_tabs += 1

    return tab_list


def get_window_list_mac():
    """Checks the amount of open Google Chrome windows and grabs their tab urls."""
    # Iterate through each window, adding their tabs to tab_list
    window_count = get_window_count_mac()
    if window_count == 0:
        common.clear()
        print("\n\n\n\n\n\n\n\n\n"
              "           No Chrome windows found!\n"
              "           Press any key to exit...")
        common.get_one_char()
        common.exit_screen_interrupt()
        return None

    window_list = []
    for i in range(1, window_count + 1):
        tab_list = get_tab_list_mac(i)
        window_list += [tab_list]
    # Get choice of tabs to actually save from user -- unless there is only one window. If there
    # is only one window, assume the user wants to save it, and move on. (Window count is the
    # number at index 0 of the list-- see the Applescript.)
    if len(window_list) == 1:
        return window_list
    selected_windows = select_windows(window_list)
    return selected_windows


def get_window_count_mac():
    """Uses Applescript to get number of currently open Chrome windows."""
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


def get_tab_list_mac(window):
    """Scrapes tabs from a given Chrome window and returns them as a list."""
    get_tab_urls_script = '''
    if application id "com.google.Chrome" is running then tell application id "com.google.Chrome"
        set tab_list to {}
        if mode of window ''' + str(window) + ''' = "incognito" then
            copy "incognito" to end of tab_list -- put identifier at start of window group
            copy (URL of tabs of window ''' + str(window) + ''' as list) to end of tab_list
        else
            copy "regular" to end of tab_list -- put identifier at start of window group
            copy (URL of tabs of window ''' + str(window) + ''' as list) to end of tab_list
        end if
        return tab_list
    end tell
    '''
    # Get the list contents and convert it from type byte to string, then to list
    tab_string = subprocess.check_output(['osascript', '-e',
                                          get_tab_urls_script]).decode("UTF-8")
    tab_list = tab_string.split(", ")
    # Remove newline that is always placed at end of tab_string
    tab_list[-1] = tab_list[-1].replace("\n", "")
    return tab_list


def select_windows(window_list):
    """Ask user to select which groups of tabs from tab_list to keep. Returns the selection."""
    window_count = len(window_list)
    selection_complete = False
    selected_window_indexes = []
    selected_windows = []
    while not selection_complete:
        common.clear()
        header = common.box(f"Save tabs | Select windows | Chosen: {selected_window_indexes}")
        # Print instructions
        print(f"{header}\n\nType the number ID of each window you want to save.\n"
            "Windows will disappear as you select them.\n"
            "Press enter to confirm your choice.\n"
            "(Pressing enter without making a selection saves all windows.)\n")

        # Print available tab/ window options
        for window_number, tab_list in enumerate(window_list):
            if tab_list != []:  # If the given window hasn't been selected already
                print(f"{window_number + 1} ({tab_list[0]})")  # print window number and identifier
                print("\n".join(tab_list[1:]))  # print urls from tab_list (exclude identifier)
                print()

        # Prompt user input
        user_input = common.get_one_char()

        # Chosen window
        if (user_input.isdigit()
            and 0 < int(user_input) <= window_count
            and int(user_input) not in selected_window_indexes):
            # Move index of chosen_window_index to selected_window_indexes, and chosen_window to
            # selected_windows, if chosen_window is a valid choice
            selected_window_indexes += [int(user_input)]
            selected_windows += [window_list[int(user_input) - 1]]
            # Replace the chosen window with a blank placeholder in window_list
            window_list[int(user_input) - 1] = []
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

    return selected_windows

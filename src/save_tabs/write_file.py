"""Generates a file that will re-open the tabs the user saved."""
import os
import platform
import stat
import common


def write_file(window_list, file_path):
    """Create an executable shortcut to open Chrome tabs selected by user."""
    if platform.system() == "Windows":
        write_file_windows(window_list, file_path)
    else:
        write_file_mac(window_list, file_path)
        write_file_executable(file_path)


def write_file_windows(window_list, file_path):
    """Generates the file at file_path containing the tabs selected in window_list, on Windows."""
    with open(file_path, "w", encoding="UTF-8") as file:
        file.write("import webbrowser\n"

                   "webbrowser.register(\"chrome-regular\", None, webbrowser.BackgroundBrowser"
                   "(\"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\"))\n"

                   "webbrowser.register(\"chrome-incognito\", None, webbrowser.BackgroundBrowser"
                   "(\"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\", "
                   "\"-incognito\"))\n")

        for window in window_list:
            if window[0] == "regular":
                browser_type = "chrome-regular"
            else:
                browser_type = "chrome-incognito"
            for url in window[1:]:
                file.write(f"webbrowser.get(\"{browser_type}\").open(\"{url}\"\n")
        file.close()


def write_file_mac(window_list, file_path):
    """Generates the file at file_path containing the tabs selected in window_list, on macOS."""
    first_window = True
    with open(file_path, "w", encoding="UTF-8") as file:
        file.write("#!/usr/bin/env zsh\n\n")

        for window in window_list:
            if window[0] == "regular":
                file.write("open -na \"Google Chrome\" --args --new-window")
            else:
                file.write("open -na \"Google Chrome\" --args --incognito --new-window")
            for url in window[1:]:
                file.write(f" \"{url}\"")

            # Add fullscreen command if that setting is on.
            if first_window:
                automatic_fullscreen = common.load_pickle("fullscreen.txt")
                if automatic_fullscreen == "on":
                    fullscreen_script = '''
                    -- Wait until Chrome is running, in front, and has a window open
                    set repeatValue to false
                    repeat until repeatValue
                        if application id "com.google.Chrome" is running then
                            if frontmost of application id "com.google.Chrome" then
                                if window 1 of application id "com.google.Chrome" exists then
                                    set repeatValue to true
                                end if
                            end if
                        end if
                    end repeat
                    -- Set fullscreen
                    tell application "System Events"
                        tell front window of process "Google Chrome" to set value of attribute "AXFullScreen" to true
                        delay 1
                    end tell
                    '''
                    file.write("\n"
                               f"osascript << EOF{fullscreen_script}\nEOF")
                first_window = False

            file.write("\n")
        file.close()


def write_file_executable(file_path):
    """Allows the generated file to run as an exectable (double click) on macOS. Equivalent to
    running chmod +x in the shell."""
    st = os.stat(file_path)
    os.chmod(file_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

"""Prompt user for a filename, then write the file.

Functions:
    main(window_list: list) -> bool
    get_filename() -> str
    get_unique_name(path: str, name: str) -> str
    write_file_windows(window_list: list, chrome_path: str,
        files_directory: str, filename: str)
    write_file_macos(window_list: list, chrome_path: str,
        files_directory: str, filename: str)
    """
import os
import platform
import stat
import time
import browser_path
import common
import settings


def main(window_list):
    """Make sure files_directory exists, then prompt user for filename.
    Write the file to files_directory.

    If the user inputs an empty string for a filename, open the
    settings menu GUI.

    If the user has file_overwriting set to "off" (default), change the
    filename if a file with the same name already exists in
    files_directory.

    Returns:
        bool: True if file was successfully made. False if not (caused
            if browser_path.get_chrome_path() returns None).
    """
    files_directory = common.load_pickle("directory.txt")
    if not os.path.exists(files_directory):
        settings.change_directory_settings()
        files_directory = common.load_pickle("directory.txt")

    filename = get_filename()
    while filename == "":
        settings.main()
        files_directory = common.load_pickle("directory.txt")
        filename = get_filename()

    file_overwriting = common.load_pickle("overwrite.txt")
    if file_overwriting == "off":
        if platform.system() == "Windows":
            extension = ".bat"
        else:
            extension = ""
        if os.path.exists(f"{files_directory}/{filename}{extension}"):
            filename = get_unique_name(files_directory, filename, extension)

    chrome_path = browser_path.get_chrome_path()
    if chrome_path is None:
        header = common.box("Save tabs | Make file")
        print(f"{header}\n\nChrome could not be found. Try again after verifying installation..")
        time.sleep(3)
        return False

    if platform.system() == "Windows":
        write_file_windows(window_list, chrome_path, files_directory, filename)
    else:
        write_file_macos(window_list, chrome_path, files_directory, filename)
    return True


def get_filename():
    """Prompt user for filename.

    Returns:
        filename (str): Name of file.
    """
    header = common.box("Save tabs | Filename")
    common.clear()
    filename = input(f"{header}\n\nPlease enter a filename (press enter for settings): ").strip()
    return filename


def get_unique_name(path, name, extension):
    """Return a unique name for a file.
    
    Args:
        path (str): Absolute path to directory for newly named file.
        name (str): The file's name.

    Returns:
        str: The unique new name of the file (not a full path).
    """
    suffix = 2
    while os.path.exists(f"{path}/{name}-{suffix}{extension}"):
        suffix += 1
    return f"{name}-{suffix}"


def write_file_windows(window_list, chrome_path, files_directory, filename):
    """Generate a .bat file with the contents of window_list.

    Write the following to a batch file:

    @ECHO OFF suppresses any output from the file.
    Then, this command is constructed for each window (one line each):

    start "" "[path/to/chrome.exe]" --new-window [--incognito]
        --user-data-dir="[user_data_dir]" [urls]

    `start ""` is essential. It is also essential that the --args go
    before the urls.

    If --user-data-dir gets a non-empty string, it will load whatever
    chrome profile is found at that absolute path. If it is blank, it
    will open Chrome with whatever Chrome's default profile is. 
    This program's default value for --user-data-dir is a blank string,
    but this can be managed in settings.

    Finally, "EXIT" exits the script.

    Args:
        window_list (Window object): List of windows to be saved. See
            window_windows.py for more details.
        files_directory (str): Absolute path to the directory where the
            file goes.
        filename (str): Name of the file.
    """
    path = f"{files_directory}/{filename}.bat"
    with open(path, "w", encoding="UTF-8") as file:
        file.write("@ECHO OFF\n")

        for window in window_list:
            file.write(f"start \"\" \"{chrome_path}\"")
            user_data_dir = common.load_pickle("user_data_dir.txt")
            file.write(f" --new-window --user-data-dir=\"{user_data_dir}\"")
            if window.mode == "incognito":
                file.write(" --incognito")
            for url in window.urls:
                file.write(f" \"{url}\"")
            file.write("\n")
        file.write("EXIT")


def write_file_macos(window_list, chrome_path, files_directory, filename):
    """Write an executable Zsh script with the contents of window_list.

    Write the following to a shell script:

    The shebang #!/usr/bin/env zsh goes at the top.
    For each window, the following is written (one line per window):

    open -na [/path/to/Google Chrome] --args [--incognito] --new-window
        --user-data-dir="[user-data-dir] "[url]" "[url]"

    If --user-data-dir is a non-empty string, the script will start
    Chrome with whatever profile is found at that absolute path. If it
    is blank, it will open Chrome with Chrome's default profile. 
    This program's default value for --user-data-dir is a blank string,
    but this can be managed in settings.

    After the first window line, if automatic_fullscreen is set to "on"
    in settings (default is "off"), write the script in
    scripts/applescript/set_fullscreen.applescript to the file.

    Finally, after each window, including the first one, write
    `sleep 0.1` to prevent windows from opening out of order.

    After the script is written, make it executable so it can be run
    with a double-click.

    Args:
        window_list (Window object): List of windows to be saved. See
            window_windows.py for more details.
        files_directory (str): Absolute path to the directory where the
            file goes.
        filename (str): Name of the file.
    """
    path = f"{files_directory}/{filename}"
    with open(path, "w", encoding="UTF-8") as file:
        file.write("#!/usr/bin/env zsh\n\n")

        first_window = True
        for window in window_list:
            file.write(f"open -na \"{chrome_path}\" --args --new-window")
            if window.mode == "incognito":
                file.write(" --incognito")
            user_data_dir = common.load_pickle("user_data_dir.txt")
            file.write(f" --user-data-dir=\"{user_data_dir}\"")
            for url in window.urls:
                file.write(f" \"{url}\"")

            if first_window:
                first_window = False
                automatic_fullscreen = common.load_pickle("fullscreen.txt")
                if automatic_fullscreen == "on":
                    file.write("\nosascript <<EOF\n")

                    program_path = os.path.dirname(os.path.realpath(__file__))
                    script_path = f"{program_path}/scripts/applescript/set_fullscreen.applescript"
                    with open(script_path, "r", encoding="UTF-8") as script:
                        script_contents = script.readlines()
                    file.writelines(script_contents)

                    file.write("EOF")
            file.write("\nsleep 0.1\n")

    # Make file executable. Equivalent to shell command `chmod +x`
    os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

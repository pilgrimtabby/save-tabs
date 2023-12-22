"""Prompts user to input desired file name. Also allows user to change settings."""
import os
import platform
import time
import common


def main():
    """Verify destination directory and get filename."""
    check_target_directory_exists()
    file_name = get_file_info()
    target_directory = common.load_pickle("directory.txt")
    file_path = get_file_path(target_directory, file_name)
    return file_path


def check_target_directory_exists():
    """Check if directory where file will go exists. If not, prompt user to choose one.
    If they cancel out of the menu, the desktop is automatically chosen."""
    target_directory = common.load_pickle("directory.txt")
    if not os.path.exists(target_directory):
        change_directory_settings()


def change_directory_settings():
    """Prompts user to select a new directory for shortcut files. If the user hits cancel in the
    dialog box, use the old setting -- unless it doesn't exist, in which case the desktop is used.
    If the user doesn't hit cancel, the new directory setting is saved."""
    header = common.box("Save tabs | Settings | File save location")
    current_target_directory = common.load_pickle("directory.txt")
    common.clear()
    print(f"{header}")

    if os.path.exists(current_target_directory):
        print(f"\nCurrent directory: {current_target_directory}")
        print("\nTo choose a new directory, press space. To exit, press enter.")
        user_input = common.get_one_char()
        if user_input != " ":
            return

    print("\nPlease select a location for files:")
    new_target_directory = common.get_dir_path()
    if new_target_directory == "" and not os.path.exists(current_target_directory):
        new_target_directory = os.path.join(os.path.expanduser('~'), 'Desktop')
        common.dump_pickle(new_target_directory, "directory.txt")
        print("\nSet file location to Desktop.")
        time.sleep(1)
    elif os.path.exists(new_target_directory):
        common.dump_pickle(new_target_directory, "directory.txt")
        common.clear()
        print(f"{header}\n\nSet file location to {new_target_directory}")
        time.sleep(1)


def get_file_info():
    """Prompt user for file_name."""
    file_name_chosen = False
    header = common.box("Save tabs | Filename")
    while not file_name_chosen:
        common.clear()
        file_name = input(f"{header}\n\nPlease enter a filename (press enter for settings): ")

        if file_name == "":
            settings_menu()
        elif len(file_name) > 0:
            file_name_chosen = True

    return file_name


def settings_menu():
    """Menu to change program settings."""
    if platform.system() == "Windows":
        menu_options = ["Target directory", "File overwriting", "Go back"]
    else:
        menu_options = ["Target directory", "Automatic fullscreen", "File overwriting", "Go back"]
    quit_menu = False
    while not quit_menu:
        common.clear()
        header = common.box("Save tabs | Settings")

        print(f"{header}\n")
        for i, option in enumerate(menu_options):
            if option == "Go back":
                print("")
            print(f"{str(i + 1)}: {option}")
        print(f"\nChoose an option (1 - {len(menu_options)}): ")

        user_input = ""
        while not user_input.isdigit() and user_input != "\r":
            user_input = common.get_one_char()

        if user_input == "\r":
            quit_menu = True
        elif 0 < int(user_input) <= len(menu_options):
            choice = menu_options[int(user_input) - 1]
            if choice == "Target directory":
                change_directory_settings()
            elif choice == "Automatic fullscreen":
                change_fullscreen_settings()
            elif choice == "File overwriting":
                change_file_overwriting_settings()
            elif choice == "Go back":
                quit_menu = True


def change_fullscreen_settings():
    """Allows user to choose whether windows open in fullscreen mode or not."""
    header = common.box("Save tabs | Settings | Fullscreen settings")
    done = False
    current_setting = common.load_pickle("fullscreen.txt")
    if current_setting == "":
        current_setting = "off"
        common.dump_pickle(current_setting, "fullscreen.txt")

    while not done:
        common.clear()
        print(f"{header}\n\nAutomatic fullscreen is currently: {current_setting.upper()}\n\n"

              "When on, files generated by this program will open windows in fullscreen mode.\n\n"
              "NOTE: This may require allowing System Events to access Accessibility in System "
              "Settings. ALso, depending on what app is in front when you run the shortcut, "
              "fullscreen may not activate unless that app is also given Accessibility access.\n"
              "Thanks, Apple.\n"
              "To toggle this setting, press space. To exit, press enter.")

        user_input = common.get_one_char()

        if user_input == " ":
            if current_setting == "off":
                current_setting = "on"
            else:
                current_setting = "off"
            common.dump_pickle(current_setting, "fullscreen.txt")

        else:
            done = True


def change_file_overwriting_settings():
    """Allows users to allow naming a file the same name as a file that already exists. If this
    option is enabled, naming a file the same name as an already-existing file will overwrite the
    previous file, so this is off by default."""
    header = common.box("Save tabs | Settings | File overwrite settings")
    done = False
    current_setting = common.load_pickle("overwrite.txt")
    if current_setting == "":
        current_setting = "off"
        common.dump_pickle(current_setting, "overwrite.txt")

    while not done:
        common.clear()
        print(f"{header}\n\nFile overwriting is currently: {current_setting.upper()}\n\n"

              "When on, this program will overwrite old files if you give a file the same name "
              "as a file that already exists. This can be convenient, but it can permanently "
              "erase files, so be careful!\n"
              "To toggle this setting, press space. To exit, press enter.")

        user_input = common.get_one_char()

        if user_input == " ":
            if current_setting == "off":
                current_setting = "on"
            else:
                current_setting = "off"
            common.dump_pickle(current_setting, "overwrite.txt")

        else:
            done = True


def get_file_path(target_directory, file_name):
    """Checks the path to a file to see if the path already exists. If it does, change it to a
    unique name (unless file overwriting is on (see settings menu) -- then it just returns the
    path without checking for duplicates)."""
    file_overwriting = common.load_pickle("overwrite.txt")

    if file_overwriting == "off":
        suffix = 2
        if platform.system() == "Windows":
            new_file_name = f"{file_name}.bat"
            while os.path.exists(f"{target_directory}/{new_file_name}"):
                new_file_name = f"{file_name}-{suffix}.bat"
                suffix += 1
        else:
            new_file_name = file_name
            while os.path.exists(f"{target_directory}/{new_file_name}"):
                new_file_name = f"{file_name}-{suffix}"
                suffix += 1
        file_path =  f"{target_directory}/{new_file_name}"

    else:
        if platform.system() == "Windows":
            file_path = f"{target_directory}/{file_name}.bat"
        else:
            file_path =  f"{target_directory}/{file_name}"

    return file_path

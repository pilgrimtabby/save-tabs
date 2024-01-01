"""GUI for settings menu.

Functions:
    main()
    change_directory_settings()
    change_fullscreen_settings()
    change_file_overwriting_settings()
    change_user_data_dir_settings()
"""
import os
import platform
import time
import common


def main():
    """GUI for settings menu."""
    if platform.system() == "Windows":
        menu_options = ["Files directory", "File overwriting", "User data directory", "Go back"]
    else:
        menu_options = ["Files directory", "Automatic fullscreen", "File overwriting",
                        "User data directory", "Go back"]

    quit_menu = False
    while not quit_menu:
        common.clear()
        header = common.box("Save tabs | Settings")

        print(f"{header}\n")
        for i, option in enumerate(menu_options):
            if option == "Go back":
                print()
            print(f"{str(i + 1)}: {option}")

        user_input = input(f"\nChoose an option (1 - {len(menu_options)}): ")

        if user_input.isdigit() and 0 < int(user_input) <= len(menu_options):
            choice = menu_options[int(user_input) - 1]
            if choice == "Files directory":
                change_directory_settings()
            elif choice == "Automatic fullscreen":
                change_fullscreen_settings()
            elif choice == "File overwriting":
                change_file_overwriting_settings()
            elif choice == "User data directory":
                change_user_data_dir_settings()
            elif choice == "Go back":
                quit_menu = True
        else:
            print("Not a valid option! Please try again.")
            time.sleep(1)


def change_directory_settings():
    """Prompt user to select a new directory for files.
    
    If the user hits cancel in the dialog box, use the old setting if
    it exists, or the desktop if not.
    """
    header = common.box("Save tabs | Settings | File save location")
    current_target_directory = common.load_pickle("directory.txt")
    common.clear()
    print(f"{header}")

    if os.path.exists(current_target_directory):
        print(f"\nCurrent directory: {current_target_directory}")
        user_input = (input("\nTo choose a new directory, press \"y\" (press enter to exit): ")
                      .lower().strip())
        if user_input != "y":
            return

    print("\nPlease select a location to save files:")
    new_target_directory = common.get_file_path(file_type="dir")
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


def change_fullscreen_settings():
    """Choose whether windows open in fullscreen mode (macOS only)."""
    header = common.box("Save tabs | Settings | Fullscreen settings")
    done = False

    while not done:
        current_setting = common.load_pickle("fullscreen.txt")
        if current_setting == "":
            current_setting = "off"
            common.dump_pickle(current_setting, "fullscreen.txt")

        common.clear()
        user_input = input(f"{header}\n\nAutomatic fullscreen is: {current_setting.upper()}\n\n"

                           "When on, generated files will open windows in fullscreen.\n\n"

                           "NOTE: For this to work, you may need to allow System Events to access "
                           "Accessibility in System Settings.\n\n"

                           "Options:\n"
                           "Press \"y\" to toggle this setting.\n"
                           "Press enter to go back.\n"
                           "Your choice: ").lower().strip()

        if user_input == "y":
            if current_setting == "off":
                common.dump_pickle("on", "fullscreen.txt")
            else:
                common.dump_pickle("off", "fullscreen.txt")

        else:
            done = True


def change_file_overwriting_settings():
    """Allows users to allow naming a file the same name as a file that already exists. If this
    option is enabled, naming a file the same name as an already-existing file will overwrite the
    previous file, so this is off by default."""
    header = common.box("Save tabs | Settings | File overwrite settings")
    done = False

    while not done:
        current_setting = common.load_pickle("overwrite.txt")
        if current_setting == "":
            current_setting = "off"
            common.dump_pickle(current_setting, "overwrite.txt")

        common.clear()
        user_input = input(f"{header}\n\nFile overwriting is: {current_setting.upper()}\n\n"

                           "If this setting is turned on, this program will overwrite old files "
                           "if you name a file the same name as a file that already exists. This "
                           "can permanently erase files, so be careful.\n\n"

                           "Options:\n"
                           "Press \"y\" to toggle this setting.\n"
                           "Press enter to go back.\n"
                           "Your choice: ").lower().strip()

        if user_input == "y":
            if current_setting == "off":
                common.dump_pickle("on", "overwrite.txt")
            else:
                common.dump_pickle("off", "overwrite.txt")

        else:
            done = True


def change_user_data_dir_settings():
    """Docstring"""
    header = common.box("Save tabs | Settings | User data directory")
    done = False

    while not done:
        current_setting = common.load_pickle("user_data_dir.txt")
        if current_setting == "":
            current_setting = "default"

        common.clear()
        user_input = input(f"{header}\n\nUser data directory is: {current_setting}\n\n"

                           "NOTE: Don't change this unless you know what you're doing!\n\n"

                           "This value points to a Chrome user profile directory.\n"
                           "Changing it here will allow you to create shortcuts that open tabs "
                           "in a Chrome profile besides the default.\n"
                           "If you've been working in a separate instance of Chrome and want to "
                           "save your tabs so they reopen in that instance, select that "
                           "instance's path.\n"
                           "To find the right path, type \"chrome://version/\" into the url bar "
                           "in Chrome and look for \"Profile Path\".\n\n"

                           "Options:\n"
                           "Press \"y\" to choose a directory.\n"
                           "Press \"d\" to restore this setting to default.\n"
                           "Press enter to go back.\n"
                           "Your choice: ").lower().strip()

        if user_input == "y":
            common.clear()
            print(f"{header}\n\nSelect the profile directory:")
            new_user_data_dir = common.get_file_path(file_type="dir")
            if new_user_data_dir != "":
                common.dump_pickle(new_user_data_dir, "user_data_dir.txt")
                common.clear()
                print(f"{header}\n\nSaved tabs will open with:\n"
                      f"{new_user_data_dir}")
                time.sleep(2)
        elif user_input == "d":
            common.dump_pickle("", "user_data_dir.txt")
            common.clear()
        else:
            done = True

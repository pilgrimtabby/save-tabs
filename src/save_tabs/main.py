"""Display program GUI.

Functions:
    main()
    exit_screen()
"""
import platform
import time

if platform.system() == "Windows":
    import window_windows
else:
    import chime
    import window_macos

import advanced_cursor
import common
import make_file


def main():
    """Display GUI for creating a file."""
    if platform.system() == "Windows":
        window_list = window_windows.get_window_list()
    else:
        window_list = window_macos.get_window_list()

    if window_list is not None:
        file_successfully_made = make_file.main(window_list)
        if file_successfully_made:
            exit_screen()


def exit_screen():
    """Display splash screen on exit."""
    advanced_cursor.hide()
    if platform.system() != "Windows":
        chime.theme("mario")
        chime.info()
    common.clear()
    print("\n\n\n           File successfully generated!\n\n\n"
        "               ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇\n"
        "               ⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⠿⠿⠿⢿⡿⢿⣿⣿⣿⠃\n"
        "               ⣿⣿⣿⣿⣿⣿⣥⣄⣀⣀⠀⠀⠀⠀⠀⢰⣾⣿⣿⠏\n"
        "               ⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⣤⣜⡻⠋\n"
        "               ⣿⣿⡿⣿⣿⣿⣿⠿⠿⠟⠛⠛⠛⠋⠉⠉⢉⡽⠃\n"
        "               ⠉⠛⠛⠛⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⡤⠚⠉\n"
        "               ⣿⠉⠛⢶⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⡇\n"
        "               ⠟⠃⠀⠀⠀⠈⠲⣴⣦⣤⣤⣤⣶⡾⠁\n\n")
    time.sleep(.5)
    common.clear()
    advanced_cursor.show()


if __name__ == "__main__":
    main()

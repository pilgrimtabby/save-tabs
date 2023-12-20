"""Scrape url data from open Chrome windows, confirm this data with the user, ask for input
(desired filename and directory), and create a clickable executable that will open the Chrome
tabs on command.
"""
import common
import write_file
import user_input
import window_list_module


def main():
    """Prompt a user for information and generate the executable."""
    window_list = window_list_module.get_window_list()
    if window_list is not None:
        file_path = user_input.get_user_input()
        write_file.write_file(window_list, file_path)
        common.exit_screen_success()

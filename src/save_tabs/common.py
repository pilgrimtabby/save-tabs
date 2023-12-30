"""Functions unrelated to any one module and used in more than one
module.

Functions:
    box(txt: str)
    clear()
    get_file_path(file_type: str)
    focus_window(window: PyCWnd)
    dump_pickle(dat: Any, file_name | str)
    load_pickle(file_name: str)
"""
import os
import pickle
import platform
import subprocess
import tkinter
import tkinter.filedialog

if platform.system() == "Windows":
    import win32ui


def box(txt):
    """Wraps text in a decorative box.
    
    Returns:
        boxed_txt (str): The boxed text.
    """
    txt = str(txt)
    side = "+"
    for _ in range(len(txt) + 4):
        side += "-"
    side += "+"
    middle = f"|  {txt}  |"
    boxed_text = f"{side}\n{middle}\n{side}"
    return boxed_text


def clear():
    """Clear screen and set cursor at top left."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def get_file_path(file_type):
    """Open a window that prompts user to select a file.
    
    Args:
        file_type (str): Accepted args are "file" and "dir". This
            function will, accordingly, ask the user to select a plain
            old file or a directory.

    Returns:
        file_path (str): Path to the file / directory the user selected
    """
    # Get foreground window for focus_window call
    if platform.system() == "Windows":
        program_window = win32ui.GetForegroundWindow()
    else:
        program_window = None
    tkinter.Tk().withdraw()  # Stop empty tkinter window from opening
    if file_type == "file":
        file_path = tkinter.filedialog.askopenfilename()
    elif file_type == "dir":
        file_path = tkinter.filedialog.askdirectory()
    else:
        raise ValueError("file_type must be \"dir\" or \"file\"")
    focus_window(program_window)
    return file_path


def focus_window(window=None):
    """Bring the program's console window to the front.

    This function exists because of a bug, apparently in tkinter, that
    causes the program window not to come back into focus after the
    user interacts with a file select dialog. 
    
    An unfortunate side effect is that (on macOS) all Terminal windows
    will pop up when this function is called, but for most users this
    is unlikely to be a significant annoyance.
    
    Args:
        window (PyCWnd object | str ): 
            On Windows, accepts a win32ui PyCWnd object obtained by 
                calling, for example, win32ui.GetForegroundWindow().
            On macOS, accepts a string (the title of the terminal 
                window).
    """
    if platform.system() == "Windows":
        if window is not None:
            try:
                window.SetForegroundWindow()
            # Weird bugs sometimes happen -- ignore those
            except win32ui.error:
                pass
    else:
        # Call applescript that focuses window.
        program_path = os.path.dirname(os.path.realpath(__file__))
        script = f"{program_path}/scripts/applescript/focus_window.applescript"
        subprocess.run(["osascript", script], check=False)


def dump_pickle(data, file_name):
    """Pickles data (dict or list) into file_name.
    
    file_name is a relative path; it is really the name of a file 
    found in src/pickles/.
    """
    program_dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(f"{program_dir_path}/pickles/{file_name}", "wb") as file:
        pickle.dump(data, file)


def load_pickle(file_name):
    """Loads the contents of a pickle at file_name.
    
    file_name is a relative path; it is really the name of a file 
    found in src/pickles/.
    """
    program_dir_path = os.path.dirname(os.path.realpath(__file__))
    # Create the pickles directory if it doesn't exist
    if not os.path.isdir(f"{program_dir_path}/pickles"):
        os.mkdir(f"{program_dir_path}/pickles")
    # Create the pickle file with an empty list if it doesn't exist
    if not os.path.exists(f"{program_dir_path}/pickles/{file_name}"):
        dump_pickle("", file_name)
    # Read the pickle file
    with open(f"{program_dir_path}/pickles/{file_name}", "rb") as file:
        return pickle.load(file)

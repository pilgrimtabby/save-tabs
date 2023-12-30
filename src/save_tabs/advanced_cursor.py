"""Allow some different cursor actions in the console.

Functions:
    dynamic_input(txt, x=0, y=0) -> str
    dynamic_print(txt, x=0, y=0)
    hide()
    show()
"""


def dynamic_input(txt, x=0, y=0):
    """Move cursor to `(x, y)` (`(0, 0)` is top left) and return an
    input call.

    Not tested on Windows.

    Args:
        txt (str): The input statement's prompt.
        x (int): x-coordinate of the cursor.
        y (int): y-coordinate of the cursor.
    """
    if isinstance(x, int) and isinstance(y, int):
        return input(f"\033[{y};{x}H" + txt)
    raise ValueError("x and y must both be integers")


def dynamic_print(txt, x=0, y=0):
    """Print `txt` at `(x, y)` (`(0, 0)` is top left).

    Not tested on Windows.

    Args:
        txt (str): The printed text.
        x (int): x-coordinate of the cursor.
        y (int): y-coordinate of the cursor.
    """
    if isinstance(x, int) and isinstance(y, int):
        print(f"\033[{y};{x}H" + txt)
    else:
        raise ValueError("x and y must both be integers")


def hide():
    """Hides cursor until shown."""
    print('\033[?25l', end="")


def show():
    """Shows cursor if hidden."""
    print('\033[?25h', end="")

"""Allows user to perform different actions with the cursor (hide and
show, and move to print/ return input).
"""


def dynamic_input(txt, x=0, y=0):
    """Moves cursor to designated line (default is top left) and returns
    the user input, with txt as prompt.
    """
    if isinstance(x, int) and isinstance(y, int):
        response = input(f"\033[{y};{x}H" + txt)
        return response
    print("Error: please enter integers for x and y values.")
    return None


def dynamic_print(txt, x=0, y=0):
    """Prints txt at the given x, y coordinate."""
    if isinstance(x, int) and isinstance(y, int):
        print(f"\033[{y};{x}H" + txt)
    else:
        print("Error: please enter integers for x and y values.")


def hide():
    """Hides cursor until shown."""
    print('\033[?25l', end="")


def show():
    """Shows cursor if hidden."""
    print('\033[?25h', end="")

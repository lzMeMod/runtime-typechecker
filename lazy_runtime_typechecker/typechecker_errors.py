"""
THis module contains all exceptions used at runtime
"""


class TypeingError(TypeError):
    """
    Basic error for a type validation
    """


class InputTypeingError(TypeingError):
    """
    Class for errors that are related to the input into a function.
    """


class OutputTypeingError(TypeingError):
    """
    Class for errors that are related to the output a function generates.
    """

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

if __name__ == '__main__':
    version = "refs/tags/v1.2.3"
    version = version[version.find("v") + 1:]
    if len(version) != 5:
        raise Exception("Version is not in the right format")

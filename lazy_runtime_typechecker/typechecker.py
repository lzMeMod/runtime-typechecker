"""
Module that contains the main function and some helper and wrapper functions.
"""
import inspect
from inspect import signature, Parameter
from types import GenericAlias
from typing import Callable, Generic

from lazy_runtime_typechecker.typechecker_errors import (
    TypeingError,
    InputTypeingError,
    OutputTypeingError,
)

# pylint: disable=W0212, C0103
empty_type = inspect._empty

# pylint: disable=R0912
def _single_argument_checker(
    type_of,
    argument,
    check_generic_types: bool = False,
    error_class=InputTypeingError,
):
    if isinstance(type_of, (GenericAlias, Generic)):
        if check_generic_types:
            type_cache: GenericAlias | Generic = type_of
        type_of = type_of.__origin__
    if type_of is None and argument is not type_of:
        raise error_class(f"Type {type(argument)} is not {type_of}")
    if type_of is not None and not isinstance(argument, type_of):
        raise error_class(f"Type {type(argument)} is not {type_of}")
    if check_generic_types:
        if type_of in (tuple, list, set):
            inner_type = type_cache.__args__[0]
            for el in argument:
                if isinstance(inner_type, (GenericAlias, Generic)):
                    _single_argument_checker(inner_type, el, check_generic_types=True)
                elif not isinstance(el, type_cache.__args__[0]):
                    raise error_class(
                        f"The element '{el}' of type {type(el)} in the list does not fit "
                        f"the generic '{str(type_cache)}'"
                    )
        if type_of is dict:
            key_type, value_type = type_cache.__args__[0], type_cache.__args__[1]
            for key, value in argument.items():
                if isinstance(key_type, (GenericAlias, Generic)):
                    _single_argument_checker(key_type, key, check_generic_types=True)
                elif not isinstance(key, key_type):
                    raise error_class(
                        f"The element '{key}' of type {type(key)} in the dict does not fit "
                        f"the generic '{str(type_cache)}'"
                    )

                if isinstance(value_type, (GenericAlias, Generic)):
                    _single_argument_checker(
                        value_type, value, check_generic_types=True
                    )
                elif not isinstance(value, value_type):
                    raise error_class(
                        f"The element '{value}' of type {type(value)} in the dict does not fit "
                        f"the generic '{str(type_cache)}'"
                    )


def _input_argument_checker(
    func, parameters, check_generic_types: bool = False, defined_by_class: bool = False
):
    def _check_input_wrapper(*args, **kwargs):
        if defined_by_class:
            args_cache, args = args, list(args)[1:]
        # check if to many arguments were passed to the function
        if (len(args) + len(kwargs)) > len(parameters):
            raise InputTypeingError("Too many vales")

        # check if *args contains any typing problems
        parallel_list: list = [v for k, v in parameters.items()]
        for index, temp_value in enumerate(args):
            temp_typing_information = parallel_list[index].annotation
            _single_argument_checker(
                temp_typing_information, temp_value, check_generic_types
            )

        # check if **kwargs has any typing problems
        for argument, temp_value in kwargs.items():
            temp_typing_information = parameters.get(argument, None)
            if temp_typing_information is None:
                raise InputTypeingError(f"This function has no parameter {argument}")
            _single_argument_checker(
                temp_typing_information.annotation, temp_value, check_generic_types
            )
        if defined_by_class:
            args = args_cache
        return func(*args, **kwargs)

    return _check_input_wrapper


def _output_type_checker(func, return_type, check_generic_types: bool = False):
    def _check_output_wrapper(*args, **kwargs):
        output = func(*args, **kwargs)
        _single_argument_checker(
            return_type, output, check_generic_types, error_class=OutputTypeingError
        )
        return func(*args, **kwargs)

    return _check_output_wrapper


def _init_check_input(parameters):
    for key, value in parameters.items():
        typing_information = value.annotation
        if value.default is not empty_type:
            _single_argument_checker(
                typing_information,
                value.default,
                check_generic_types=True,
                error_class=TypeingError,
            )
        if typing_information is empty_type:
            raise TypeingError(
                f"No typing information was provided for parameter '{key}'"
            )


def _init_check_return_type(return_type):
    if return_type is empty_type:
        raise TypeingError(
            "No typing information was provided for the return type of the Callable"
        )


def static_typed(
    init_check: bool,
    check_input_args: bool = True,
    check_return_value: bool = True,
    check_generic_types: bool = True,
    defined_by_class: bool = False,
) -> Callable:
    """
    Decorator to enable strict type checking for a method
    :param init_check: required bool to specify if the typing of the default values and the return
    type should be checked even before the first call of the function to wrap
    :param check_input_args: bool to specify if the input parameters should be checked
    :param check_return_value: bool to specify if the output parameters should be checked
    :param check_generic_types: bool to specify if generic types should be resolved
    :param defined_by_class: set to true if method is defined inside a class
    :return: the wrapped function
    """

    def _wrapper_factory(func):
        parameters: dict[str, Parameter] = dict(signature(func).parameters)
        if defined_by_class:
            del parameters[list(parameters.keys())[0]]
        return_type = signature(func).return_annotation
        if init_check:
            _init_check_input(parameters)
            _init_check_return_type(return_type)

        out: Callable = func
        if check_input_args:
            out = _input_argument_checker(
                out, parameters, check_generic_types, defined_by_class
            )
        if check_return_value:
            out = _output_type_checker(out, return_type, check_generic_types)
        return out

    return _wrapper_factory

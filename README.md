# Runtime typechecker for Python methods
This package provides a simple wrapper for methods to enforce type checking at runtime

![PyPi publishing](https://github.com/lzMeMod/runtime-typechecker/actions/workflows/python-publish.yml/badge.svg)

<!-- toc -->

- [Limitations](#limitations)
- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Documentation](#documentation)
  * [init_check: bool](#init_check-bool)
  * [check_input_args: bool = True](#check_input_args-bool--true)
  * [check_return_value: bool = True](#check_return_value-bool--true)
  * [check_generic_types: bool = True](#check_generic_types-bool--true)
  * [defined_by_class: bool = False](#defined_by_class-bool--false)
- [Exception](#exception)

<!-- tocstop -->

## Limitations
Let's talk about the limitations of this package first
* The type checking only works with the new python 3.10 syntax. For older versions basic type 
checking still works. But `Generics` and `Unions` are not working with the old systax. Have a look 
at [PEP 604](https://peps.python.org/pep-0604/) for more information.
* Performance: Of course checking something at runtime comes with a performance penalty. This module
is intended to be used for only a few methods were type checking is absolutely necessary. If you need typechecking for 
everything consider using something like [mypy](https://github.com/python/mypy)
* Non-callable object: normal function are callable object in python but a function with the `@classmethod` decorator
is not callable. This Package **only** supports callable objects.

## Installation
```bash
pip install lazy_runtime_typechecker
```

## Basic Usage
This module contains one wrapper. This wrapper can be used to type check a function.

```python
from lazy_runtime_typechecker import static_typed

@static_typed(init_check=True)
def my_function(x: str) -> str:
    return x

if __name__ == '__main__':
    my_function(x="hello world") # ok
    my_function(12) # will raise an exception
```
## Documentation
The `@static_typed` wrapper takes different arguments to configure how the types are checked.
The default is always `True` because the assumption is, that if someone adds this wrapper to a 
function, they want to be really sure that nearly all cases are checked. Of course every single 
parameter that is set to true will add a performance penalty to the type checker (except `defined_by_class`).

### init_check: bool
If the parameter is set to true the signature of the arguments and the return type is checked even
before the first call. Also, the default values are checked against the signature of the arguments.  
Example:

```python
from lazy_runtime_typechecker import static_typed

@static_typed(init_check=False)
def my_function(x: str = 12) -> str:
    return x
# this will not raise an exception

@static_typed(init_check=True)
def my_function(x: str = 12) -> str:
    return x
# this will raise an exception because 12 is not a str

@static_typed(init_check=True)
def my_function(x: str = "hi"):
    return x
# this will raise an exception because no return type was specified
```
The exception that is raised for the initial validation is from type `runtime_typechecker.TypeingError`.
All other exceptions from this module are inheritance form this exception.

### check_input_args: bool = True
If this parameter is set to `True` then the input values are checked each time the function is 
called. The exception that is raised by an input validation is from type `runtime_typechecker.InputTypeingError`.

```python
from lazy_runtime_typechecker import static_typed, InputTypeingError

@static_typed(init_check=True, check_input_args=False)
def my_function(x: str = "hi"):
    return x
# this will not raise an exception
my_function(12) 

@static_typed(init_check=True, check_input_args=True)
def my_function(x: str = "hi"):
    return x
# this will raise an exception
my_function(12) 

# or catch the exception
try:
    my_function(12)
except InputTypeingError:
    pass
```

### check_return_value: bool = True
If this parameter is set to `True` then the return value is checked each time the function is 
called. The exception that is raised by an input validation is from type `runtime_typechecker.InputTypeingError`.

```python
from lazy_runtime_typechecker import static_typed, OutputTypeingError

@static_typed(init_check=True, check_return_value=False)
def my_function(x: int) -> int:
    return str(x)
# this will not raise an exception
my_function(12)

@static_typed(init_check=True, check_return_value=True)
def my_function(x: int) -> int:
    return str(x)
# this will raise an exception
my_function(12)

# or catch the exception
try:
    my_function(12)
except OutputTypeingError:
    pass
```

### check_generic_types: bool = True
Until now all examples only showed some basic types. But python also has a rich selection of types to
represent nearly every possible typing expression. Of course with these more complex and nested types
the performance penalty increases. If this parameter is set to `True` generic types are also check 
in full depth. If set to `False` only the first level of the generic type is matched. This behavior
is applied for the input and the output stream.

```python
from lazy_runtime_typechecker import static_typed

@static_typed(init_check=True, check_generic_types=False)
def my_function(x: list[str]) -> list[str]:
    return x
# this will not raise an exception
my_function([12, "hello world"])

@static_typed(init_check=True, check_generic_types=True)
def my_function(x: list[str]) -> list[str]:
    return x
# this will raise an exception
my_function([12, "hello world"])


# also multiple level of depth are supported
@static_typed(init_check=True, check_generic_types=True)
def my_function(x: tuple[str | list[int | float]]) -> dict[str, int]:
    return {"abc": 12}
```

### defined_by_class: bool = False
If a method is defined by a class, then set this parameter to True. This means the first parameter for passing the 
instance of the class to the method is not checked.
```python
from lazy_runtime_typechecker import static_typed

class MyTestClass:
    @static_typed(init_check=True, defined_by_class=True)
    def my_function(self, x: str) -> int:
        return int(x)


    @static_typed(init_check=True, defined_by_class=False)
    @staticmethod
    def my_static_function(x: str) -> str:
        return x

    # this does not work because a class method is not callable
    @static_typed(init_check=True, defined_by_class=False)
    @classmethod
    def my_class_method(cls, x: str) -> str:
        return cls()
```

## Exception
Three exception are part of this module.
* `TypeingError(TypeError)`: is the base exception
* `InputTypeingError(TypeingError)`: this exception is raised if an input parameter validation fails
* `OutputTypeingError(TypeingError)`: this exception is raised if a return value validation fails
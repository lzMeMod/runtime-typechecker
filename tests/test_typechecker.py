from lazy_runtime_typechecker import (
    static_typed,
    TypeingError,
    InputTypeingError,
    OutputTypeingError,
)
import pytest


def test_init_handling():
    @static_typed(init_check=True)
    def _my_test_function(x: str) -> None:
        pass

    with pytest.raises(TypeingError):

        @static_typed(init_check=True)
        def _my_test_function(x: str):
            pass

    with pytest.raises(TypeingError):

        @static_typed(init_check=True)
        def _my_test_function(x) -> None:
            pass

    with pytest.raises(TypeingError):

        @static_typed(init_check=True)
        def _my_test_function(x: list[int | str] = [12.8]) -> None:
            pass

    @static_typed(init_check=False)
    def _my_test_function(x) -> None:
        pass


def test_args_checker():
    @static_typed(init_check=True)
    def _my_test_function(x: str) -> str:
        return x

    assert _my_test_function("abc") == "abc"

    with pytest.raises(InputTypeingError):
        _my_test_function(12)

    with pytest.raises(InputTypeingError):
        _my_test_function("abc", "abc")

    @static_typed(init_check=True, check_generic_types=True)
    def _my_test_function(x: str | int) -> str | int:
        return x

    assert 12 == _my_test_function(12)
    assert "12" == _my_test_function("12")
    with pytest.raises(InputTypeingError):
        _my_test_function(12.5)

    @static_typed(init_check=True, check_generic_types=True)
    def _my_test_function(x: str | int) -> str | int:
        return x

    assert 12 == _my_test_function(12)
    assert "12" == _my_test_function("12")
    with pytest.raises(InputTypeingError):
        _my_test_function(12.5)

    @static_typed(init_check=True, check_generic_types=True)
    def _my_test_function(x: list[str | int]) -> list[str | int]:
        return x

    assert ["abc", "abc"] == _my_test_function(["abc", "abc"])
    assert ["12", 12] == _my_test_function(["12", 12])
    with pytest.raises(InputTypeingError):
        _my_test_function([12.5])

    @static_typed(init_check=False)
    def _my_test_function(y: int = 5) -> int:
        return y

    with pytest.raises(InputTypeingError):
        _my_test_function(x=12)


def test_dict_union():
    @static_typed(init_check=True, check_generic_types=True)
    def _my_test_function(x: dict[str, int]) -> None:
        return None

    _my_test_function(x={"hi": 12})


def test_return_type():
    @static_typed(init_check=True)
    def my_fuction(x: str) -> int:
        return x

    with pytest.raises(OutputTypeingError):
        my_fuction("hi")


def test_object_methods():
    class MyTestClass:
        @static_typed(init_check=True, defined_by_class=True)
        def my_function(self, x: str) -> int:
            return int(x)


        @static_typed(init_check=True, defined_by_class=False)
        @staticmethod
        def my_static_function(x: str) -> str:
            return x


    ab = MyTestClass()
    ab.my_function("12")

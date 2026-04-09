from typing import Any, Optional, TypeVar

T = TypeVar("T")


def first_not_none(*args: T) -> Optional[T]:
    for item in args:
        if item is not None:
            return item
    return None


def none_if_in(some_value: Any, *choices: Any):
    """
    如果值在choices中，返回None，否则返回原值
    此方法处理了pd.isna的情况
    """
    try:
        from pandas import isna

        if isna(some_value):
            return some_value if next(filter(isna, choices), None) is None else None
    except ImportError:
        pass
    return None if some_value in choices else some_value

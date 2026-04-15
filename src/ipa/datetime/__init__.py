import time
from typing import Literal

from .core import *


def timestamp(
    unit: Literal["second", "millisecond", "microsecond"] = "millisecond",
    type: Union[float, int] = int,
) -> Union[float, int]:
    """
    获取当前时间戳
    Args:
        unit: 时间戳单位，默认毫秒
        type: 时间戳类型，默认整数
    Returns:
        时间戳
    """
    s = time.time()
    if unit == "millisecond":
        v = s * 1000
    elif unit == "microsecond":
        v = s * 1000000
    elif unit == "second":
        v = s
    else:
        raise NotImplementedError(f"unsupported unit: {unit}")
    return type(v)

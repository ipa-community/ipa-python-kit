from typing import Any, Callable, Optional

from ..data_type import ErrorHandler


def set_attr_if(
    obj: Any,
    props: dict,
    cond: Callable[[str, Any], bool],
    on_error: Optional[ErrorHandler] = None,
    **kwargs,
):
    """
    如果指定对象满足条件则设置目标属性的值

    Args:
        obj: 目标对象
        props: 要设置的属性值
        cond: 过滤器，接收属性名和属性值，返回是否满足条件
        on_error: 错误处理函数，接收异常对象，默认忽略异常
    """
    assert obj is not None, "obj can't be None"
    for k, v in props.items():
        if not cond(k, v):
            continue
        try:
            setattr(obj, k, v)
        except Exception as e:
            if on_error:
                on_error(e)


def set_attr_if_has(obj: Any, props: dict, **kwargs):
    """
    如果目标对象存在指定属性则设置
    """
    set_attr_if(obj, props, lambda k, v: hasattr(obj, k), **kwargs)

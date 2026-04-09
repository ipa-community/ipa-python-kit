import asyncio


def get_or_new_event_loop(auto_set: bool = True) -> asyncio.AbstractEventLoop:
    """

    获取当前事件循环，如果不存在则创建一个新的事件循环。

    Args:
        auto_set (bool, optional): 是否自动设置为当前事件循环。默认值为True。

    Returns:
        asyncio.AbstractEventLoop: 当前事件循环实例。
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        if auto_set:
            asyncio.set_event_loop(loop)
    return loop

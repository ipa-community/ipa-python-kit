import logging
from importlib import import_module
from typing import Callable, Optional, Set, Tuple

from watchfiles import Change, PythonFilter, awatch


def try_hot_reload(name, package: Optional[str] = None):
    """
    热加载指定模块
    Args:
        name: 模块名
        package: 包名
    """
    try:
        hmlib = import_module(name=name, package=package)
        assert hmlib, f"failed to import module: {package}.{name}"
        logging.info("shall reload: %s", hmlib)
        # TODO: exclude怎么用
        import hmr

        hmr.reload(hmlib)
    except Exception as e:
        logging.warning("failed to reload: %s", e)


async def watch_python_dir(
    dir: str, on_change: Callable[[Set[Tuple[Change, str]]], None]
):
    """
    这是一个使用样例，功能并不通用
    """
    logging.info("watch files in %s", dir)
    async for change in awatch(str(dir), watch_filter=PythonFilter()):
        logging.info("change detected:%s", change)
        on_change(change)

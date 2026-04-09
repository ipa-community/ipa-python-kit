from pathlib import Path
from typing import Union


def get_disk_usage(path: Union[str, Path], follow_symlink: bool = True):
    """
    获取指定路径的磁盘使用情况。

    TODO: 增加缓存；迭代效率

    Args:
        path (Union[str, Path]): 要获取磁盘使用情况的路径。
        follow_symlink (bool, optional): 是否跟随符号链接。默认值为 True。

    Returns:
        int: 路径占用的磁盘空间大小（字节）。
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"path {path} not exists")

    if path.is_symlink() and follow_symlink:
        path = path.resolve()
    if path.is_file():
        byte_size = path.stat().st_size
    elif path.is_dir():
        byte_size = sum(get_disk_usage(f, follow_symlink) for f in path.glob("**/*"))
    else:
        raise ValueError(f"path {path} is not a file or dir")
    return byte_size

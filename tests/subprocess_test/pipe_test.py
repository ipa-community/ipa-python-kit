import subprocess
from pathlib import Path

import pytest


def test_pipe_block():
    cmd = [
        "uv",
        "run",
        str(Path(__file__).parent / "child.py"),
        "keep-write",
        "--big-write",
    ]
    print(" ".join(cmd))
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    # # 一直读取
    # while p.stdout.readable():
    #     line = p.stdout.readline()
    #     if line:
    #         print("parent read:", line.strip())

    # 关闭读端
    p.stdout.close()

    with pytest.raises(subprocess.TimeoutExpired):
        rc = p.wait(timeout=5)
        assert rc != 0


def test_pipe_keep_read():
    p = subprocess.Popen(
        ["uv", "run", Path(__file__).parent / "child.py", "keep-write"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    count = 0
    # 一直读取
    for line in p.stdout:
        count += 1
        if count > 6:
            break
        print("parent read:", line.strip())

    # 关闭读端
    p.stdout.close()

    with pytest.raises(ValueError):
        next(p.stdout)

    with pytest.raises(subprocess.TimeoutExpired):
        rc = p.wait(timeout=5)
        assert rc != 0


def test_pipe_partial_read():
    p = subprocess.Popen(
        ["uv", "run", Path(__file__).parent / "child.py", "write"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    # 读取一点内容
    print("parent read:", p.stdout.readline().strip())

    # 关闭读端
    p.stdout.close()

    rc = p.wait()
    assert rc != 0

import logging
import subprocess
import sys
from pathlib import Path
from typing import List

import psutil
import pytest
from pydantic import Field

from ipa.cli.model import BaseCommandArgs, BaseStartConfig
from ipa.cli.proxy import CommandProxy
from ipa.cli.seaweedfs import SeaweedfsCommandArgs, SeaweedfsProxy, SeaweedfsStartConfig
from ipa.data_type.process import ProcessKillingConfig

logging.basicConfig(level=logging.INFO)


def test_ls_proxy():
    class LsCommandArgs(BaseCommandArgs):
        path: str = Field(default=".", description="要列出的目录路径")

        def build(self, command: str) -> List[str]:
            return [command, self.path]

    proxy = CommandProxy[LsCommandArgs, BaseStartConfig](
        "ls",
        command_args=LsCommandArgs(path="/e/src"),
        start_config=BaseStartConfig(background=True),
    )

    x = proxy.start()
    if x is None:
        return

    assert proxy.process is not None
    assert proxy.is_running()

    out = list(proxy.read())
    print("stdout:", out)
    assert out is not None

    assert proxy.is_running()
    with pytest.raises(psutil.NoSuchProcess):
        proxy.process.status()

    ok = proxy.stop()
    print("stopped:", ok)
    assert ok and not proxy.is_running()


def test_seaweedfs_proxy():
    logger = logging.getLogger("SeaweedfsProxy")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler(sys.stdout))
    binary_root = Path("E:\\app\\seaweedfs_windows_amd64-4.07")
    binary = binary_root / "weed.exe"

    if not binary.exists():
        logger.warning(f"可执行文件不存在: {binary},跳过此测试")
        return
    weed = SeaweedfsProxy(
        binary,
        command_args=SeaweedfsCommandArgs(
            mini=True,
            dir=binary_root / "mini-data",
            s3_config=binary_root / "s3.json",
        ),
        logger=logger,
    )
    weed.start(SeaweedfsStartConfig(background=True))

    for line in weed.read(until=lambda x, count: count > 100):
        if not line:
            continue
        print(line)

    with pytest.raises(psutil.TimeoutExpired):
        weed.process.wait(15)

    weed.restart()

    with pytest.raises(subprocess.TimeoutExpired):
        stdout, stderr = weed.read_all(timeout=15)
        print("stdout:", stdout)
        print("stderr:", stderr)

    weed.stop(ProcessKillingConfig(force=True, max_try=None))

    assert not weed.is_running()

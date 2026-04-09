import atexit
import logging
import subprocess
from pathlib import Path
from typing import (
    IO,
    Any,
    Callable,
    Generic,
    List,
    Literal,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

import psutil

from ..data_type.process import ProcessKillingConfig
from ..system import kill_process
from .model import BaseStartConfig, CommandArgsType, StartConfigType


class CommandProxy(Generic[CommandArgsType, StartConfigType]):
    """
    命令行代理接口
    """

    def __init__(
        self,
        binary: Union[str, Path],
        command_args: Optional[CommandArgsType] = None,
        start_config: Optional[StartConfigType] = BaseStartConfig(),
        stop_config: Optional[ProcessKillingConfig] = ProcessKillingConfig(),
        logger: logging.Logger = None,
        **kwargs,
    ):
        """
        Args:
            binary (Union[str, Path]): 可以是一个具体的命令例如ls，也可以是一个可执行文件的路径
        """
        self.binary = binary

        if isinstance(self.binary, Path):
            self.binary = self.binary.absolute()
            self.validate_binary_exists()

        self._popen: Optional[subprocess.Popen] = None
        self._process: Optional[psutil.Process] = None

        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.start_config = start_config
        self.stop_config = stop_config
        self.command_args = command_args

    @property
    def process(self) -> Optional[psutil.Process]:
        """
        Popen所启动的进程对象
        """
        pid = self._popen.pid if self._popen else None
        if self._process is None and pid:
            try:
                self._process = psutil.Process(pid)
            except psutil.NoSuchProcess:
                self._process = None
        return self._process

    def validate_binary_exists(self) -> None:
        """
        校验可执行文件是否存在
        """
        if not self.binary.exists():
            raise FileNotFoundError(f"可执行文件不存在: {self.binary}")

    @property
    def command(self) -> List[str]:
        """命令行参数"""
        return list(
            map(
                str,
                (
                    self.command_args.build(self.binary)
                    if self.command_args
                    else [self.binary]
                ),
            )
        )

    def start(
        self, start_config: Optional[StartConfigType] = None
    ) -> Optional[subprocess.Popen]:
        """启动可执行文件"""

        if self.is_running():
            self.logger.info(f"可执行文件 {self.binary} 已运行，无需重复启动")
            return self._popen

        # 使用提供的配置或默认配置
        if start_config:
            self.start_config = start_config
        else:
            start_config = self.start_config

        # 构建命令行
        cmd = self.command
        self.logger.info(f"启动命令: {' '.join(cmd)}")
        # 构建跨平台的 subprocess 参数
        popen_kwargs = start_config.popen_kwargs if start_config else {}

        try:
            # 启动进程
            self._popen = subprocess.Popen(cmd, **popen_kwargs)
            if start_config.stop_at_exit:
                atexit.register(self.stop)
            # 超时检查
            if start_config and start_config.timeout:
                return_code = self._popen.wait(timeout=start_config.timeout)
                if self._popen.returncode != 0:
                    raise RuntimeError(f"启动失败，返回码: {self._popen.returncode}")
            self.logger.info(f"启动成功，PID: {self._popen.pid}")
            return self._popen
        except Exception as e:
            self.logger.error(f"启动失败: {str(e)}")
            self._popen = None
            return None

    def stop(
        self, stop_config: Optional[ProcessKillingConfig] = None
    ) -> Optional[bool]:
        """终止可执行文件

        Returns:
            bool: 是否成功终止,如果进程不存在则返回None
        """
        # if not self.subprocess:
        #     self.logger.warning(f"可执行文件 {self.binary} 未启动，无需终止")
        #     return None

        if not self.is_running():
            self.logger.info(f"可执行文件 {self.binary} 不在运行中，无需终止")
            return True

        if stop_config:
            self.stop_config = stop_config
        else:
            stop_config = self.stop_config

        _, alive = kill_process([self.process], stop_config)
        ok = not alive
        if ok:
            self._process = None
            self.logger.info(f"可执行文件 {self.binary} 已终止，PID: {self.pid}")
        return ok

    def restart(
        self,
        start_config: Optional[StartConfigType] = None,
        stop_config: Optional[ProcessKillingConfig] = None,
    ):
        """重启可执行文件"""
        ok = self.stop(stop_config)
        assert ok, f"终止进程失败，PID: {self.pid}"
        return self.start(start_config=start_config)

    @property
    def pid(self) -> Optional[int]:
        """进程ID"""
        return self._popen.pid if self._popen else None

    def is_running(self) -> bool:
        """检查是否运行"""
        if self.process is None:
            return False
        assert (
            self.process.pid == self.pid
        ), f"进程ID不匹配，期望: {self.pid}, 实际: {self.process.pid}"
        return self.process.is_running()

    def read(
        self,
        _from: Literal["stdout", "stderr"] = "stdout",
        until: Union[Callable[[Any, int], bool], None] = None,
        auto_close: bool = True,
    ):
        """持续读取标准输出"""
        if not self.process:
            return None
        count = 0
        stream: IO = getattr(self._popen, _from, self._popen.stdout)
        for x in stream:
            if until and until(x, count):
                break
            yield x
            count += 1
        if auto_close:
            stream.close()

    def read_all(self, timeout: Optional[float] = None, **kwargs) -> Tuple[str, str]:
        """
        基于communicate方法读取所有输出
        """
        if not self._popen:
            return None
        stdout, stderr = self._popen.communicate(
            timeout=timeout, input=kwargs.get("input", None)
        )
        if self._popen.returncode != 0:
            self.logger.warning(f"命令执行失败，返回码: {self._popen.returncode}")

        # 是否设置了text=True
        if self._popen.universal_newlines:
            return stdout, stderr

        return (stdout.decode(self._popen.encoding) if stdout is not None else None), (
            stderr.decode(self._popen.encoding) if stderr is not None else None
        )


if __name__ == "__main__":
    pass

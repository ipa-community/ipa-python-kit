from typing import Any, Callable, Optional, Union

import psutil
from pydantic import BaseModel, Field


class ProcessFindingConfig(BaseModel):
    """
    进程查找配置
    """

    pid: Optional[int] = None
    name: Optional[str] = None
    port: Optional[int] = None
    process_filter: Optional[Callable[[psutil.Process], bool]] = None

    @property
    def final_process_filter(self):
        """
        会综合考虑 pid, name, port, filter 等条件
        """

        def _filter(p: psutil.Process) -> bool:
            if self.pid and p.pid != self.pid:
                return False
            if self.name and p.name() != self.name:
                return False
            if self.port and self.port not in [
                conn.laddr.port for conn in p.net_connections(kind="inet")
            ]:
                return False
            if self.process_filter and not self.process_filter(p):
                return False
            return True

        return _filter


class ProcessKillingConfig(BaseModel):
    """
    杀进程的配置
    """

    force: bool = Field(
        default=False, description="是否强制终止进程，默认 False 表示不强制终止"
    )
    timeout: Union[float, None] = Field(
        default=None, description="超时时间（秒），默认 None 表示无限等待"
    )
    max_try: Optional[int] = Field(
        default=1, description="最大尝试次数，默认 1 次，为None表示无限重试"
    )
    on_terminate: Optional[Callable[[psutil.Process], Any]] = Field(
        default=None, description="进程终止回调函数"
    )


class ProcessFindingAndKillingConfig(ProcessFindingConfig, ProcessKillingConfig):
    """
    进程查找和杀进程配置
    """

    pass

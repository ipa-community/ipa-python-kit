import subprocess
import sys
from abc import abstractmethod
from typing import Any, Dict, List, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

model_config = ConfigDict(
    extra="allow", coerce_numbers_to_str=True, arbitrary_types_allowed=True
)


class BaseCommandArgs(BaseModel):
    """命令行参数"""

    model_config = model_config

    @abstractmethod
    def build(self, command: str) -> List[str]:
        """转换为命令行参数"""
        raise NotImplementedError()


CommandArgsType = TypeVar("CommandArgsType", bound=BaseCommandArgs)


class BaseStartConfig(BaseModel):
    """基础启动配置"""

    model_config = model_config

    background: bool = Field(default=True, description="是否后台运行")
    capture_output: bool = Field(default=True, description="是否捕获 stdout/stderr")
    encoding: str = Field(default="utf-8", description="输出编码格式")
    timeout: Optional[int] = Field(default=None, description="启动超时时间（秒）")
    sudo: bool = Field(default=False, description="是否用 sudo 启动")

    extra_popen_kwargs: Optional[Dict[str, Any]] = Field(
        default=None, description="subprocess.Popen 额外参数"
    )

    stop_at_exit: bool = Field(default=True, description="是否在主程序退出时停止此进程")

    def build_background_kwargs(self) -> Dict[str, Any]:
        """
        构建跨平台的后台运行参数
        """
        kwargs = {}
        if sys.platform.startswith("win"):
            kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
        else:
            kwargs["start_new_session"] = True

        # kwargs["creationflags"] |= subprocess.CREATE_NO_WINDOW
        return kwargs

    @property
    def popen_kwargs(self) -> Dict[str, Any]:
        """subprocess.Popen 参数"""
        # 构建跨平台的 subprocess 参数
        popen_kwargs = {
            "shell": False,
            "encoding": self.encoding,
            "text": True,
            "bufsize": 1,
        }

        # 后台运行参数
        if self.background:
            popen_kwargs.update(self.build_background_kwargs())

        # 捕获输出,stdout和stderr合并
        if self.capture_output:
            popen_kwargs["stdout"] = subprocess.PIPE
            popen_kwargs["stderr"] = subprocess.STDOUT

        popen_kwargs.update(self.extra_popen_kwargs or {})
        return popen_kwargs


StartConfigType = TypeVar("StartConfigType", bound=BaseStartConfig)

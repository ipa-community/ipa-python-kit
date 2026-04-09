from pathlib import Path
from typing import Optional, Union

from .model import BaseCommandArgs, BaseStartConfig
from .proxy import CommandProxy


class SeaweedfsCommandArgs(BaseCommandArgs):
    mini: bool = False
    server: bool = False
    s3: bool = True
    s3_config: Union[str, Path] = None
    dir: Union[str, Path] = "."

    def build(self, binary: Path):
        command = [binary.resolve().as_posix()]
        if self.mini:
            command.append("mini")
        if self.server:
            command.append("server")
        command.append(f"-dir={Path(self.dir).resolve().as_posix()}")
        if self.s3:
            command.append("-s3")
        if self.s3_config:
            assert Path(
                self.s3_config
            ).exists(), f"s3_config file {self.s3_config} not exists"
            command.append(f"-s3.config={Path(self.s3_config).resolve().as_posix()}")
        return command


class SeaweedfsStartConfig(BaseStartConfig):
    pass


class SeaweedfsProxy(CommandProxy[SeaweedfsCommandArgs, SeaweedfsStartConfig]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

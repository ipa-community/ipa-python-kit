import sys
import time

from typer import Typer

cmd = Typer()


@cmd.command()
def write(big_write: bool = False):
    try:
        sys.stdout.write("first\n")
        sys.stdout.flush()
        time.sleep(1)  # 等父进程有机会关闭读端
        sys.stdout.write("second\n")
        sys.stdout.flush()
        print("wrote second" * 100000 if big_write else "wrote second", file=sys.stderr)
    except Exception as e:
        print("exception", e)
        print("exception:", repr(e), file=sys.stderr)


@cmd.command()
def keep_write(big_write: bool = False):
    while True:
        write(big_write=big_write)


if __name__ == "__main__":
    cmd()

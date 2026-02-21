import os
import shutil
import subprocess


def find_executable(name: str) -> str | None:
    return shutil.which(name)


def run_subprocess(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, check=True)


def exec_replace(args: list[str]) -> None:
    os.execvp(args[0], args)

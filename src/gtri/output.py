from rich.console import Console

_console = Console(stderr=True)
_stdout_console = Console()


def print_error(msg: str) -> None:
    _console.print(f"[bold red]gtri:[/bold red] {msg}")


def print_info(msg: str) -> None:
    _stdout_console.print(f"[dim]{msg}[/dim]")


def print_command(cmd: str) -> None:
    _stdout_console.print(f"[bold green]$[/bold green] {cmd}")

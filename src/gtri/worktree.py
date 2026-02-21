from dataclasses import dataclass


@dataclass(frozen=True)
class Worktree:
    path: str
    branch: str
    status: str


def parse_porcelain(raw: str) -> tuple[Worktree, ...]:
    worktrees = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        path, branch, status = parts[0], parts[1], parts[2]
        if not branch:
            continue
        worktrees.append(Worktree(path=path, branch=branch, status=status))
    return tuple(worktrees)

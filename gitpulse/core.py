"""Core logic: find repositories and read their recent commits."""

from __future__ import annotations

import datetime as dt
import subprocess
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Commit:
    sha: str
    author: str
    timestamp: dt.datetime
    subject: str


@dataclass
class RepoActivity:
    path: Path
    commits: list[Commit] = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def count(self) -> int:
        return len(self.commits)


def find_repos(root: Path, max_depth: int = 3) -> list[Path]:
    """Return directories under ``root`` that contain a ``.git`` entry.

    Does not descend into a repository once found, and skips hidden directories.
    """
    root = root.expanduser().resolve()
    found: list[Path] = []

    def walk(directory: Path, depth: int) -> None:
        if (directory / ".git").exists():
            found.append(directory)
            return
        if depth >= max_depth:
            return
        try:
            children = sorted(p for p in directory.iterdir() if p.is_dir())
        except (PermissionError, OSError):
            return
        for child in children:
            if child.name.startswith("."):
                continue
            walk(child, depth + 1)

    walk(root, 0)
    return found


def parse_log(output: str) -> list[Commit]:
    """Parse output produced by ``git log --pretty=format:%H%x1f%an%x1f%aI%x1f%s``."""
    commits: list[Commit] = []
    for line in output.splitlines():
        if not line.strip():
            continue
        parts = line.split("\x1f")
        if len(parts) != 4:
            continue
        sha, author, iso_time, subject = parts
        commits.append(
            Commit(
                sha=sha,
                author=author,
                timestamp=dt.datetime.fromisoformat(iso_time),
                subject=subject,
            )
        )
    return commits


def read_commits(repo: Path, since: dt.datetime, author: str | None = None) -> list[Commit]:
    """Read commits in ``repo`` made at or after ``since`` (optionally by ``author``)."""
    cmd = [
        "git",
        "-C",
        str(repo),
        "log",
        "--all",
        f"--since={since.isoformat()}",
        "--pretty=format:%H%x1f%an%x1f%aI%x1f%s",
    ]
    if author:
        cmd.append(f"--author={author}")
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        return []
    return parse_log(result.stdout)


def collect(
    root: Path,
    days: int,
    author: str | None = None,
    now: dt.datetime | None = None,
    max_depth: int = 3,
) -> list[RepoActivity]:
    """Collect activity for every repo under ``root``; only repos with commits are returned."""
    now = now or dt.datetime.now(dt.timezone.utc)
    since = now - dt.timedelta(days=days)
    activities = []
    for repo in find_repos(root, max_depth=max_depth):
        commits = read_commits(repo, since, author=author)
        if commits:
            activities.append(RepoActivity(path=repo, commits=commits))
    activities.sort(key=lambda a: a.count, reverse=True)
    return activities


def daily_counts(activities: list[RepoActivity]) -> Counter:
    """Count commits per calendar day (local date of the commit's own timezone)."""
    counter: Counter = Counter()
    for activity in activities:
        for commit in activity.commits:
            counter[commit.timestamp.date()] += 1
    return counter

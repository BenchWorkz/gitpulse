"""Command-line entry point: ``gitpulse [ROOT] [--days N] [--author NAME]``."""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

from . import __version__
from .core import collect
from .report import render


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gitpulse",
        description="Summarize recent commit activity across local git repositories.",
    )
    parser.add_argument("root", nargs="?", default=".", type=Path, help="folder to scan (default: .)")
    parser.add_argument("-d", "--days", type=int, default=7, help="look-back window in days (default: 7)")
    parser.add_argument("-a", "--author", help="only count commits whose author matches this text")
    parser.add_argument("--max-depth", type=int, default=3, help="how deep to search for repos (default: 3)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.days < 1:
        print("error: --days must be at least 1", file=sys.stderr)
        return 2
    root = args.root.expanduser()
    if not root.is_dir():
        print(f"error: not a directory: {root}", file=sys.stderr)
        return 2
    now = dt.datetime.now(dt.timezone.utc)
    activities = collect(root, days=args.days, author=args.author, now=now, max_depth=args.max_depth)
    print(render(activities, days=args.days, now=now))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

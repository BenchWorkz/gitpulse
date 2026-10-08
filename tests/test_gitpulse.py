import datetime as dt
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from gitpulse.core import collect, find_repos, parse_log
from gitpulse.report import sparkline


def git(repo: Path, *args: str, date: str | None = None) -> None:
    env = dict(os.environ, GIT_AUTHOR_NAME="Tester", GIT_AUTHOR_EMAIL="t@example.com",
               GIT_COMMITTER_NAME="Tester", GIT_COMMITTER_EMAIL="t@example.com")
    if date:
        env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = date
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, env=env)


class GitpulseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def make_repo(self, name: str, *, date: str | None = None) -> Path:
        repo = self.tmp / name
        repo.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        (repo / "file.txt").write_text(name)
        git(repo, "add", ".")
        git(repo, "commit", "-q", "-m", f"init {name}", date=date)
        return repo

    def test_find_repos_respects_depth_and_skips_hidden(self):
        self.make_repo("top")
        self.make_repo("group/nested")
        self.make_repo("a/b/c/deep")
        (self.tmp / ".hidden").mkdir()
        subprocess.run(["git", "init", "-q", str(self.tmp / ".hidden" / "x")], check=True)
        names = sorted(p.name for p in find_repos(self.tmp, max_depth=2))
        self.assertEqual(names, ["nested", "top"])

    def test_collect_counts_recent_commits_only(self):
        now = dt.datetime.now(dt.timezone.utc)
        recent = now.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        old = (now - dt.timedelta(days=60)).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        self.make_repo("fresh", date=recent)
        self.make_repo("stale", date=old)
        activities = collect(self.tmp, days=7, now=now)
        self.assertEqual([a.name for a in activities], ["fresh"])
        self.assertEqual(activities[0].count, 1)

    def test_parse_log_ignores_malformed_lines(self):
        bad = "abc\x1fAda\x1f2024-01-01T00:00:00+00:00\nnot a valid line\n"
        self.assertEqual(parse_log(bad), [])
        good = "abc\x1fAda\x1f2024-01-01T00:00:00+00:00\x1fhello"
        commits = parse_log(good)
        self.assertEqual(len(commits), 1)
        self.assertEqual(commits[0].subject, "hello")

    def test_sparkline(self):
        self.assertEqual(sparkline([]), "")
        self.assertEqual(sparkline([0, 0]), "  ")
        self.assertEqual(sparkline([0, 8])[-1], "█")


if __name__ == "__main__":
    unittest.main()

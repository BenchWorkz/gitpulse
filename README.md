# gitpulse

A tiny, dependency-free CLI that scans a folder for git repositories and shows
how active you've been across them over the last few days.

```
$ gitpulse ~/code --days 14
gitpulse report: last 14 day(s), as of 2026-10-08
23 commit(s) across 4 repo(s)

activity: ▁▁█▃▁▁▂▅▁▁▁▁▂▇

  api-server   12  last: Fix pagination off-by-one
  website       6  last: Update hero copy
  cli-tools     4  last: Add --json flag
  notes         1  last: Weekly journal
```

## Features

- Recursively finds repos (configurable depth, skips hidden folders)
- Counts commits across all branches within a time window
- Filter to a single author with `--author`
- Daily activity sparkline, sorted per-repo summary
- No third-party dependencies, Python 3.10+

## Install

```bash
git clone https://github.com/<your-username>/gitpulse.git
cd gitpulse
pip install .
```

Or run without installing: `python -m gitpulse ~/code`

## Usage

```bash
gitpulse                      # scan current directory, last 7 days
gitpulse ~/code -d 30         # last 30 days
gitpulse ~/code -a "Jane"     # only commits by authors matching "Jane"
gitpulse ~/code --max-depth 5 # search deeper
```

## Development

```bash
python -m unittest discover -s tests -t . -v
```

## Roadmap

- `--json` output for scripts
- Per-repo last-activity date
- Streak counter

Contributions welcome. Open an issue first for larger changes.

## License

MIT

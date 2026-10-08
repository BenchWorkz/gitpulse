"""Text rendering for gitpulse output."""

from __future__ import annotations

import datetime as dt

from .core import RepoActivity, daily_counts

BAR_CHARS = " ▁▂▃▄▅▆▇█"


def sparkline(values: list[int]) -> str:
    """Render integers as a unicode sparkline (empty string for no values)."""
    if not values:
        return ""
    top = max(values)
    if top == 0:
        return BAR_CHARS[0] * len(values)
    steps = len(BAR_CHARS) - 1
    return "".join(BAR_CHARS[round(v / top * steps)] for v in values)


def render(activities: list[RepoActivity], days: int, now: dt.datetime) -> str:
    total = sum(a.count for a in activities)
    lines = [
        f"gitpulse report: last {days} day(s), as of {now:%Y-%m-%d}",
        f"{total} commit(s) across {len(activities)} repo(s)",
        "",
    ]
    if not activities:
        lines.append("No commits found. Try a larger --days value or a different root.")
        return "\n".join(lines)

    counts = daily_counts(activities)
    series = []
    for offset in range(days - 1, -1, -1):
        day = (now - dt.timedelta(days=offset)).date()
        series.append(counts.get(day, 0))
    lines.append(f"activity: {sparkline(series)}")
    lines.append("")

    width = max(len(a.name) for a in activities)
    for activity in activities:
        latest = activity.commits[0]
        lines.append(
            f"  {activity.name:<{width}}  {activity.count:>4}  last: {latest.subject[:60]}"
        )
    return "\n".join(lines)

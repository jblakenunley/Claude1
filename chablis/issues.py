#!/usr/bin/env python3
"""Chablis issue-health collector: Day 4 evidence. Stdlib plus the `gh` CLI.

  issues.py [--asof YYYY-MM-DD] [--days 90] OWNER/REPO [OWNER/REPO ...]

Reads GitHub issue search only (`gh api -X GET search/issues`): counts, never
repo-scoped endpoints, so it works for repos a session was not granted. Prints one
JSON object per repo. All counts are issues only (is:issue); a pull request is not an
issue, and the REST `open_issues_count` the scout stores includes open PRs.

Per repo:
  open, closed          lifetime issue counts; open_share = open / (open + closed)
  opened, closed_in     issues created / closed in the last --days days (ending --asof)
  flow                  closed_in / opened  (>1: the backlog is shrinking)
  no_comment            issues created in the window that have zero comments, and share
  resolution            median days created->closed over a sample of up to 100 issues
                        closed in the window, most recently updated first. BACKLOG-
                        SENSITIVE: a sweep of old issues makes it huge (see Day 4 log);
                        do not read it as responsiveness.
  cohort                issues created in the --days days BEFORE the window, so each has
                        had at least --days days to resolve: up to 500 newest of them.
                        no_comment_share, closed_share, closed_7d / closed_30d (share of
                        the cohort closed within 7 / 30 days), median_days_closed (among
                        closed), not_planned_share (among closed). This is the measure
                        that does not move when a maintainer sweeps old issues.
First-response time is not collected: it needs each issue's comments, which search
does not return. `no_comment` is the nearest search-only proxy; it counts bot comments.
"""
import json, statistics, subprocess, sys, time
from datetime import date, datetime, timedelta

PAUSE = 2.2  # search allows ~30 requests a minute


def search(q, per_page=1, page=1, sort="updated"):
    for attempt in range(4):
        r = subprocess.run(["gh", "api", "-X", "GET", "search/issues", "-f", "q=" + q, "-f", f"per_page={per_page}",
                            "-f", f"page={page}", "-f", f"sort={sort}", "-f", "order=desc"], capture_output=True, text=True)
        time.sleep(PAUSE)
        if r.returncode == 0:
            return json.loads(r.stdout)
        if "rate limit" in (r.stdout + r.stderr).lower():
            time.sleep(30 * (attempt + 1))
            continue
        raise RuntimeError((r.stdout or r.stderr).strip()[:300])
    raise RuntimeError("rate limited")


def count(q):
    return search(q)["total_count"]


def days(a, b):
    f = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
    return (f(b) - f(a)).total_seconds() / 86400


def cohort(base, start, end):
    """Up to 500 newest issues created in [start, end), with their outcomes."""
    q, items, total = f"{base} created:{start}..{end}", [], 0
    for page in range(1, 6):
        res = search(q, per_page=100, page=page, sort="created")
        total = res["total_count"]
        items += res["items"]
        if len(items) >= total or not res["items"]:
            break
    closed = [i for i in items if i.get("closed_at")]
    d = [days(i["created_at"], i["closed_at"]) for i in closed]
    n = len(items)
    share = lambda k, of: round(k / of, 2) if of else None
    return {"created_total": total, "n": n, "sample_complete": n == total,
            "no_comment_share": share(sum(i["comments"] == 0 for i in items), n),
            "closed_share": share(len(closed), n),
            "closed_7d": share(sum(x <= 7 for x in d), n), "closed_30d": share(sum(x <= 30 for x in d), n),
            "median_days_closed": round(statistics.median(d), 1) if d else None,
            "not_planned_share": share(sum(i.get("state_reason") == "not_planned" for i in closed), len(closed))}


def collect(repo, asof, window):
    since = (asof - timedelta(days=window)).isoformat()
    base = f"repo:{repo} is:issue"
    m = {"repo": repo, "asof": asof.isoformat(), "window_days": window, "since": since}
    m["open"], m["closed"] = count(base + " is:open"), count(base + " is:closed")
    m["open_share"] = round(m["open"] / (m["open"] + m["closed"]), 3) if m["open"] + m["closed"] else None
    m["open_prs"] = count(f"repo:{repo} is:pr is:open")
    m["opened"] = count(f"{base} created:>={since}")
    sample = search(f"{base} is:closed closed:>={since}", per_page=100)
    m["closed_in"] = sample["total_count"]
    m["flow"] = round(m["closed_in"] / m["opened"], 2) if m["opened"] else None
    m["no_comment"] = count(f"{base} created:>={since} comments:0")
    m["no_comment_share"] = round(m["no_comment"] / m["opened"], 3) if m["opened"] else None
    items = [i for i in sample["items"] if i.get("closed_at")]
    d = [days(i["created_at"], i["closed_at"]) for i in items]
    m["resolution"] = {
        "sample": len(items), "sample_complete": len(items) == m["closed_in"],
        "median_days": round(statistics.median(d), 1) if d else None,
        "within_7d_share": round(sum(x <= 7 for x in d) / len(d), 2) if d else None,
        "not_planned_share": round(sum(i.get("state_reason") == "not_planned" for i in items) / len(items), 2) if items else None,
        "oldest_closed_in_sample": min(i["closed_at"] for i in items)[:10] if items else None,
    }
    m["cohort_range"] = [(asof - timedelta(days=2 * window)).isoformat(), since]
    m["cohort"] = cohort(base, *m["cohort_range"])
    return m


def main(argv):
    asof, window, repos = date.today(), 90, []
    it = iter(argv)
    for a in it:
        if a == "--asof":
            asof = date.fromisoformat(next(it))
        elif a == "--days":
            window = int(next(it))
        else:
            repos.append(a)
    if not repos:
        sys.exit(__doc__)
    for r in repos:
        try:
            print(json.dumps(collect(r, asof, window)), flush=True)
        except Exception as e:  # one repo failing must not hide the rest
            print(json.dumps({"repo": r, "error": str(e)}), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])

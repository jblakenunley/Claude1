#!/usr/bin/env python3
"""Chablis Upkeep scorer: Doctrine section 6, Upkeep bands v1. Stdlib plus git.

  upkeep.py [--asof YYYY-MM-DD] OWNER/REPO [OWNER/REPO ...]

Clones each repo bare and treeless (commits and tags only, a few MB) into a temp
directory and scores Upkeep from git history alone. No API key, no API quota.

Bands (all windows end at --asof; humans only, bots excluded, authors merged by email):
  L  liveness: days since last human commit on the default branch
       <=30 -> 3, <=90 -> 2, <=365 -> 1, else 0
  R  release:  latest full-version release tag and distinct release days in 365 d
       age<=90 and >=4 days -> 3; age<=180 and >=2 -> 2; age<=365 -> 1; else 0
  B  bus:      CHAOSS Contributor Absence Factor (fewest humans making >=50% of the
       last 365 d of commits). With >=20 human commits and AF = 1, deduct 1.
  Upkeep = max(0, min(L, R) - deduction), except L=3 with R=0, which is null (not scored:
  the repo is live but ships no release tag, so its release channel is unread).
  An archived repo is 0 (hard stop; read the
  flag from the scout, git cannot see it).
"""
import collections, json, re, subprocess, sys, tempfile
from datetime import date, datetime, timedelta, timezone

BOT = re.compile(r"\[bot\]|dependabot|github-actions|renovate|pre-commit-ci|^copilot$|copilot-swe-agent", re.I)
REL = re.compile(r"^(?:.+-)?[vV]?\d+\.\d+(?:\.\d+)*$")  # 4.7.0, v2.0.1, openbb-core-v2.0.1; not v7, not rc/beta


def git(g, *a):
    return subprocess.run(["git", "--git-dir", g, *a], capture_output=True, text=True, check=True).stdout


def ident(email):
    e = email.lower().strip()
    m = re.match(r"^\d+\+(.+)@users\.noreply\.github\.com$", e)
    return "gh:" + m.group(1) if m else e


def bands(m):
    d = m["days_since_last_human_commit"]
    L = 3 if d is not None and d <= 30 else 2 if d is not None and d <= 90 else 1 if d is not None and d <= 365 else 0
    age, days = m["latest_release_age"], m["release_days_365d"]
    R = 0 if age is None else 3 if age <= 90 and days >= 4 else 2 if age <= 180 and days >= 2 else 1 if age <= 365 else 0
    w = m["w365"]
    deduct = 1 if w["commits_human"] >= 20 and w["absence_factor"] == 1 else 0
    # v1.1 (2026-11-25): live commits (L3) with no release tag in 365 d (R0) is "release channel unread", not 0.
    up = None if (L == 3 and R == 0) else max(0, min(L, R) - deduct)
    return {"L": L, "R": R, "bus_deduction": deduct, "upkeep": up,
            "bus_scored": w["commits_human"] >= 20}


def analyse(repo, g, asof):
    m = {"repo": repo, "asof": asof.isoformat()}
    cut365 = asof - timedelta(days=365)
    rows = []
    for l in git(g, "log", "HEAD", "--since=" + cut365.isoformat(), "--format=%cI\t%aE\t%aN").splitlines():
        d, e, n = l.split("\t")
        rows.append((datetime.fromisoformat(d).astimezone(timezone.utc).date(), e, n))
    human = [r for r in rows if not (BOT.search(r[1]) or BOT.search(r[2]))]
    lh = None
    for l in git(g, "log", "HEAD", "-n", "2000", "--format=%cI\t%aE\t%aN").splitlines():
        d, e, n = l.split("\t")
        if not (BOT.search(e) or BOT.search(n)):
            lh = d[:10]
            break
    m["last_human_commit"] = lh
    m["days_since_last_human_commit"] = (asof - date.fromisoformat(lh)).days if lh else None
    for w in (90, 365):
        cut = asof - timedelta(days=w)
        sel = [r for r in human if r[0] >= cut]
        c = collections.Counter(ident(r[1]) for r in sel)
        nm = collections.defaultdict(collections.Counter)
        for r in sel:
            nm[ident(r[1])][r[2]] += 1
        n, cum, af = len(sel), 0, 0
        for _, v in c.most_common():
            cum += v
            af += 1
            if cum * 2 >= n:
                break
        top = c.most_common(3)
        m[f"w{w}"] = {"commits_all": len([r for r in rows if r[0] >= cut]), "commits_human": n,
                      "human_authors": len(c), "absence_factor": af if n else None,
                      "top1_share": round(top[0][1] / n, 3) if n else None,
                      "top2_share": round(sum(v for _, v in top[:2]) / n, 3) if n else None,
                      "top3": [(nm[k].most_common(1)[0][0], v) for k, v in top]}
    rel = sorted(((date.fromisoformat(d), t) for d, t in
                  (l.split("\t") for l in git(g, "for-each-ref", "--format=%(creatordate:short)\t%(refname:short)",
                                              "refs/tags").splitlines()) if REL.match(t)), reverse=True)
    m["latest_release_tag"] = [rel[0][1], rel[0][0].isoformat()] if rel else None
    m["latest_release_age"] = (asof - rel[0][0]).days if rel else None
    m["release_days_365d"] = len({d for d, _ in rel if d >= cut365})
    m["release_days_90d"] = len({d for d, _ in rel if d >= asof - timedelta(days=90)})
    m["bands"] = bands(m)
    return m


def main(argv):
    asof = datetime.now(timezone.utc).date()
    if argv[:1] == ["--asof"]:
        asof, argv = date.fromisoformat(argv[1]), argv[2:]
    out = []
    with tempfile.TemporaryDirectory() as tmp:
        for repo in argv:
            g = f"{tmp}/{repo.replace('/', '_')}.git"
            subprocess.run(["git", "clone", "--bare", "--filter=tree:0", "--quiet",
                            f"https://github.com/{repo}.git", g], check=True)
            out.append(analyse(repo, g, asof))
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main(sys.argv[1:])

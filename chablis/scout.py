#!/usr/bin/env python3
"""Chablis scout: collects tool-quality signals for the watchlist. No model.

Commands
  pins DIR                      audit GitHub Actions in DIR's workflows for tag-pinning
  run --watchlist F --out F     pull signals for every repo in the watchlist (needs network;
                                runs on GitHub Actions via chablis-scout.yml, uses GITHUB_TOKEN if set)
  selftest                      offline checks of the parsing and scoring logic

Stdlib only, by house convention. Every signal carries its source URL and retrieval time.
"""
import json, os, re, sys, time, urllib.error, urllib.request
from datetime import datetime, timedelta, timezone

UA = "chablis-scout/1.0 (+https://github.com/jblakenunley/claude1)"
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
USES_RE = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)")


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------- pins ----------

def audit_pins(text, path="<text>"):
    """Return one finding per `uses:` line: pinned to a SHA, a tag/branch, or local/docker."""
    out = []
    for n, line in enumerate(text.splitlines(), 1):
        m = USES_RE.match(line)
        if not m:
            continue
        ref = m.group(1)
        if ref.startswith("./") or ref.startswith("docker://"):
            kind = "local-or-docker"
        elif "@" not in ref:
            kind = "unpinned"
        else:
            kind = "sha" if SHA_RE.match(ref.split("@", 1)[1]) else "tag-or-branch"
        first_party = ref.startswith("actions/") or ref.startswith("github/")
        out.append({"file": path, "line": n, "uses": ref, "pin": kind, "first_party": first_party})
    return out


def cmd_pins(d):
    findings = []
    for root, _, files in os.walk(d):
        for f in sorted(files):
            if f.endswith((".yml", ".yaml")):
                p = os.path.join(root, f)
                with open(p, encoding="utf-8") as fh:
                    findings += audit_pins(fh.read(), p)
    for x in findings:
        flag = "OK " if x["pin"] in ("sha", "local-or-docker") else "PIN"
        print(f"{flag} {x['file']}:{x['line']}  {x['uses']}  ({x['pin']}, {'first-party' if x['first_party'] else 'third-party'})")
    bad = [x for x in findings if x["pin"] in ("tag-or-branch", "unpinned")]
    print(f"\n{len(findings)} uses, {len(bad)} not pinned to a SHA")
    return 1 if bad else 0


# ---------- network ----------

def get(url, token=None):
    """GET JSON. Returns (data, headers, error). Honors Retry-After once on 403/429."""
    h = {"User-Agent": UA, "Accept": "application/vnd.github+json"}
    if token and "api.github.com" in url:
        h["Authorization"] = f"Bearer {token}"
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=30) as r:
                return json.loads(r.read().decode() or "null"), dict(r.headers), None
        except urllib.error.HTTPError as e:
            if e.code in (403, 429) and attempt == 1 and e.headers.get("Retry-After"):
                time.sleep(min(int(e.headers["Retry-After"]), 60))
                continue
            return None, dict(e.headers or {}), f"HTTP {e.code}"
        except Exception as e:  # network errors are recorded, never fatal
            return None, {}, f"{type(e).__name__}: {e}"
    return None, {}, "retry exhausted"


def last_page(link_header):
    """Count from a GitHub Link header (per_page=1 trick). None if no pagination."""
    m = re.search(r'[?&]page=(\d+)>; rel="last"', link_header or "")
    return int(m.group(1)) if m else None


def count_via_link(url, token):
    data, h, err = get(url, token)
    if err:
        return None, err
    n = last_page(h.get("Link") or h.get("link"))
    return (n if n is not None else len(data or [])), None


def signals(full_name, token=None):
    """All raw signals for one repo. Scores are assigned by Chablis, not here."""
    api = f"https://api.github.com/repos/{full_name}"
    s = {"repo": full_name, "retrieved_at": now(), "errors": {}}
    repo, _, err = get(api, token)
    if err:
        s["errors"]["repo"] = err
        return s
    s.update({
        "stars": repo.get("stargazers_count"),
        "forks": repo.get("forks_count"),
        "open_issues": repo.get("open_issues_count"),
        "archived": repo.get("archived"),
        "pushed_at": repo.get("pushed_at"),
        "license": (repo.get("license") or {}).get("spdx_id"),
        "default_branch": repo.get("default_branch"),
    })
    rel, _, err = get(f"{api}/releases/latest", token)
    s["latest_release"] = {"tag": rel.get("tag_name"), "published_at": rel.get("published_at")} if rel else None
    if err and err != "HTTP 404":
        s["errors"]["release"] = err
    since = (datetime.now(timezone.utc) - timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%SZ")
    s["commits_90d"], err = count_via_link(f"{api}/commits?since={since}&per_page=1", token)
    if err:
        s["errors"]["commits"] = err
    s["contributors"], err = count_via_link(f"{api}/contributors?per_page=1&anon=1", token)
    if err:
        s["errors"]["contributors"] = err
    sc, _, err = get(f"https://api.securityscorecards.dev/projects/github.com/{full_name}")
    if sc:
        s["scorecard"] = {"score": sc.get("score"), "date": sc.get("date"),
                          "checks": {c["name"]: c.get("score") for c in sc.get("checks", [])}}
    else:
        s["scorecard"] = None
        s["errors"]["scorecard"] = err
    s["sources"] = [api, f"https://api.securityscorecards.dev/projects/github.com/{full_name}"]
    return s


def cmd_run(watchlist, out):
    with open(watchlist, encoding="utf-8") as fh:
        wl = json.load(fh)
    token = os.environ.get("GITHUB_TOKEN")
    rows = []
    for item in wl["repos"]:
        rows.append({**signals(item["repo"], token), "category": item.get("category")})
        time.sleep(0.5)  # politeness
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump({"generated_at": now(), "count": len(rows), "repos": rows}, fh, indent=2)
    errs = sum(1 for r in rows if r["errors"])
    print(f"wrote {out}: {len(rows)} repos, {errs} with at least one error")
    return 0


# ---------- selftest ----------

def cmd_selftest():
    wf = """
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa  # test fixture, not a real SHA
      - uses: someone/thing@main
      - uses: ./local-action
      - uses: someone/unpinned
    """
    f = audit_pins(wf)
    assert [x["pin"] for x in f] == ["tag-or-branch", "sha", "tag-or-branch", "local-or-docker", "unpinned"], f
    assert f[0]["first_party"] and not f[2]["first_party"]
    link = '<https://api.github.com/x?per_page=1&page=2>; rel="next", <https://api.github.com/x?per_page=1&page=347>; rel="last"'
    assert last_page(link) == 347
    assert last_page("") is None
    with open(os.path.join(os.path.dirname(__file__), "watchlist.json"), encoding="utf-8") as fh:
        wl = json.load(fh)
    assert all("/" in r["repo"] and r.get("category") for r in wl["repos"]), "watchlist malformed"
    print(f"selftest ok ({len(wl['repos'])} watchlist repos)")
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["pins"] and len(a) == 2:
        sys.exit(cmd_pins(a[1]))
    if a[:1] == ["run"] and "--watchlist" in a and "--out" in a:
        sys.exit(cmd_run(a[a.index("--watchlist") + 1], a[a.index("--out") + 1]))
    if a[:1] == ["selftest"]:
        sys.exit(cmd_selftest())
    print(__doc__)
    sys.exit(2)

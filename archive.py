#!/usr/bin/env python3
"""
RECORD ARCHIVE
A private research archive over a single professional subject.

Design constraints (see nunley-archive-spec.md):
  - Document-level retrieval. No chunking, ever.
  - Access tier is required on every document. RESTRICTED is refused at the gate.
  - Everything is one SQLite file. Copy it to back it up.
  - Zero external dependencies for the core. Python 3.9+ and stdlib only.

Usage:
    python3 archive.py init
    python3 archive.py seed seed_cases.csv
    python3 archive.py add --file opinion.txt --tier public --type opinion \
                           --title "Blackthorne v. Bellush" --citation "61 S.W.3d 439"
    python3 archive.py search "fraudulent transfer"
    python3 archive.py show opinion-2001-blackthorne-v-bellush
    python3 archive.py stats
    python3 archive.py context "TUFTA injunction" > brief.txt
"""

import argparse
import csv
import json
import os
import re
import sqlite3
import sys
import unicodedata
from datetime import date, datetime
from pathlib import Path

DB_PATH = os.environ.get("ARCHIVE_DB", "archive.db")

# --------------------------------------------------------------------------
# Controlled vocabularies
# --------------------------------------------------------------------------

TIERS = ("public", "family", "RESTRICTED")

DOC_TYPES = (
    "opinion", "brief", "petition", "motion", "order", "judgment",
    "transcript", "deposition", "cle_paper", "news", "obituary",
    "correspondence", "interview", "directory", "photo", "other",
)

DATE_PRECISION = ("exact", "month", "year", "estimated", "unknown")
VERIFICATION = ("verified", "unverified", "contradicted")

# Firm/employer name -> approximate active years. CONFIGURE PER ENGAGEMENT.
# Partnership names change as partners join and leave. Build this table from
# case captions and letterhead, then use it to date undated documents.
# This is the single most useful field when processing an unsorted box of paper.
#
# Example:
#   ("Smith, Jones & Alvarez", 1988, 1994),
#   ("Smith & Alvarez",        1994, 2001),
FIRM_ERAS = [
    # ("Firm name as it appears on captions", start_year, end_year),
]

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS documents (
    doc_id              TEXT PRIMARY KEY,
    title               TEXT NOT NULL,
    doc_type            TEXT NOT NULL,

    -- ACCESS CONTROL. Required. Enforced in add_document().
    access_tier         TEXT NOT NULL,
    privilege_reviewed  INTEGER NOT NULL DEFAULT 0,
    privilege_note      TEXT,

    -- Legal context
    case_style          TEXT,
    citation            TEXT,
    cause_number        TEXT,
    court               TEXT,
    county              TEXT,
    judge               TEXT,
    panel               TEXT,          -- JSON list

    -- His role
    subject_role         TEXT,
    represented         TEXT,
    co_counsel          TEXT,          -- JSON list
    opposing_counsel    TEXT,          -- JSON list
    firm_caption        TEXT,

    -- Time
    doc_date            TEXT,          -- ISO 8601
    date_precision      TEXT DEFAULT 'unknown',

    -- Provenance
    source_url          TEXT,
    physical_source     TEXT,
    date_acquired       TEXT,
    ocr_applied         INTEGER DEFAULT 0,
    ocr_confidence      REAL,
    original_path       TEXT,          -- path to the untouched scan

    -- Research state
    verification_status TEXT DEFAULT 'unverified',
    subject_tags        TEXT,          -- JSON list
    notes               TEXT,

    -- Content
    summary             TEXT,
    full_text           TEXT,
    token_estimate      INTEGER,

    created_at          TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tier    ON documents(access_tier);
CREATE INDEX IF NOT EXISTS idx_type    ON documents(doc_type);
CREATE INDEX IF NOT EXISTS idx_date    ON documents(doc_date);
CREATE INDEX IF NOT EXISTS idx_county  ON documents(county);
CREATE INDEX IF NOT EXISTS idx_verif   ON documents(verification_status);

-- Full-text index. Weighted: title and summary matter more than raw body.
CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
    doc_id UNINDEXED,
    title,
    case_style,
    summary,
    full_text,
    subject_tags,
    tokenize = 'porter unicode61'
);

-- Quarantine. Anything tier=RESTRICTED lands here and is never indexed.
CREATE TABLE IF NOT EXISTS quarantine (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    attempted_at TEXT NOT NULL,
    title        TEXT,
    source       TEXT,
    reason       TEXT NOT NULL
);

-- Append-only research log.
CREATE TABLE IF NOT EXISTS findings (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    doc_id     TEXT,
    claim      TEXT NOT NULL,
    status     TEXT NOT NULL DEFAULT 'unverified',
    note       TEXT,
    FOREIGN KEY(doc_id) REFERENCES documents(doc_id)
);
"""


# --------------------------------------------------------------------------
# Infrastructure
# --------------------------------------------------------------------------

def connect(path=None):
    conn = sqlite3.connect(path or DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def cmd_init(args):
    conn = connect()
    conn.executescript(SCHEMA)
    conn.commit()
    print(f"Initialized {DB_PATH}")
    print("Back this up by copying the file. That is the whole procedure.")


def slugify(text, maxlen=60):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text[:maxlen]


def make_doc_id(doc_type, doc_date, title):
    year = ""
    if doc_date:
        m = re.search(r"(\d{4})", str(doc_date))
        if m:
            year = m.group(1) + "-"
    return f"{doc_type}-{year}{slugify(title)}"


def estimate_tokens(text):
    """Rough. Legal prose runs denser than the usual 4-chars-per-token."""
    return int(len(text) / 3.7) if text else 0


def as_json_list(value):
    if not value:
        return "[]"
    if isinstance(value, list):
        return json.dumps(value)
    parts = [p.strip() for p in str(value).split(";") if p.strip()]
    return json.dumps(parts)


def from_json_list(value):
    try:
        return json.loads(value) if value else []
    except (json.JSONDecodeError, TypeError):
        return []


def infer_era(firm_caption):
    """Given a firm caption, return the approximate active range."""
    if not firm_caption:
        return None
    norm = firm_caption.lower().replace(",", "").replace(".", "")
    for name, start, end in FIRM_ERAS:
        if name.lower().replace(",", "").replace(".", "") in norm:
            return (start, end)
    return None


# --------------------------------------------------------------------------
# The privilege gate
# --------------------------------------------------------------------------

class PrivilegeError(Exception):
    pass


def check_tier(tier, title="(untitled)", source=""):
    """
    The gate. Nothing enters the index without an explicit tier, and
    RESTRICTED never enters at all.
    """
    if tier is None or tier == "":
        raise PrivilegeError(
            "No access_tier supplied. Every document must be classified "
            "before ingestion. Use --tier public|family|RESTRICTED."
        )
    if tier not in TIERS:
        raise PrivilegeError(f"Unknown tier {tier!r}. Must be one of {TIERS}.")
    if tier == "RESTRICTED":
        conn = connect()
        conn.execute(
            "INSERT INTO quarantine (attempted_at, title, source, reason) "
            "VALUES (?,?,?,?)",
            (datetime.now().isoformat(), title, source,
             "Marked RESTRICTED. Privileged or unreviewed client material.")
        )
        conn.commit()
        raise PrivilegeError(
            f"REFUSED: {title!r} is marked RESTRICTED and was logged to "
            "quarantine, not indexed.\n"
            "Client files are confidential under Tex. Disciplinary Rule 1.05. "
            "That duty survives both the client's death and the lawyer's. "
            "Resolve authority in writing before reclassifying."
        )
    return tier


# --------------------------------------------------------------------------
# Ingestion
# --------------------------------------------------------------------------

def add_document(conn, **f):
    tier = check_tier(f.get("access_tier"), f.get("title", ""), f.get("source_url", ""))

    full_text = f.get("full_text") or ""
    doc_type = f.get("doc_type") or "other"
    if doc_type not in DOC_TYPES:
        raise ValueError(f"Unknown doc_type {doc_type!r}. Must be one of {DOC_TYPES}.")

    doc_id = f.get("doc_id") or make_doc_id(doc_type, f.get("doc_date"), f.get("title", "untitled"))

    # If this doc_id already exists, merge: supplied fields win, existing
    # fields survive. Otherwise attaching full text to a seeded stub would
    # blank out the metadata the seed carefully established.
    existing = conn.execute("SELECT * FROM documents WHERE doc_id=?", (doc_id,)).fetchone()
    if existing:
        prior = dict(existing)
        def keep(key, new):
            return new if new not in (None, "", "[]", "other", "unknown") else prior.get(key)
    else:
        prior = {}
        def keep(key, new):
            return new

    row = {
        "doc_id": doc_id,
        "title": keep("title", f.get("title")) or "(untitled)",
        "doc_type": keep("doc_type", doc_type) or "other",
        "access_tier": tier,
        "privilege_reviewed": int(bool(f.get("privilege_reviewed", prior.get("privilege_reviewed", 0)))),
        "privilege_note": keep("privilege_note", f.get("privilege_note")),
        "case_style": keep("case_style", f.get("case_style")),
        "citation": keep("citation", f.get("citation")),
        "cause_number": keep("cause_number", f.get("cause_number")),
        "court": keep("court", f.get("court")),
        "county": keep("county", f.get("county")),
        "judge": keep("judge", f.get("judge")),
        "panel": keep("panel", as_json_list(f.get("panel"))),
        "subject_role": keep("subject_role", f.get("subject_role")),
        "represented": keep("represented", f.get("represented")),
        "co_counsel": keep("co_counsel", as_json_list(f.get("co_counsel"))),
        "opposing_counsel": keep("opposing_counsel", as_json_list(f.get("opposing_counsel"))),
        "firm_caption": keep("firm_caption", f.get("firm_caption")),
        "doc_date": keep("doc_date", f.get("doc_date")),
        "date_precision": keep("date_precision", f.get("date_precision")) or "unknown",
        "source_url": keep("source_url", f.get("source_url")),
        "physical_source": keep("physical_source", f.get("physical_source")),
        "date_acquired": prior.get("date_acquired") or f.get("date_acquired") or date.today().isoformat(),
        "ocr_applied": int(bool(f.get("ocr_applied", prior.get("ocr_applied", 0)))),
        "ocr_confidence": keep("ocr_confidence", f.get("ocr_confidence")),
        "original_path": keep("original_path", f.get("original_path")),
        "verification_status": keep("verification_status", f.get("verification_status")) or "unverified",
        "subject_tags": keep("subject_tags", as_json_list(f.get("subject_tags"))),
        "notes": keep("notes", f.get("notes")),
        "summary": keep("summary", f.get("summary")),
        "full_text": full_text or prior.get("full_text") or "",
        "token_estimate": estimate_tokens(full_text or prior.get("full_text") or ""),
        "created_at": prior.get("created_at") or datetime.now().isoformat(),
    }

    cols = ",".join(row.keys())
    marks = ",".join("?" * len(row))
    conn.execute(f"INSERT OR REPLACE INTO documents ({cols}) VALUES ({marks})",
                 list(row.values()))

    conn.execute("DELETE FROM documents_fts WHERE doc_id = ?", (doc_id,))
    conn.execute(
        "INSERT INTO documents_fts (doc_id,title,case_style,summary,full_text,subject_tags) "
        "VALUES (?,?,?,?,?,?)",
        (doc_id, row["title"], row["case_style"] or "", row["summary"] or "",
         full_text, " ".join(from_json_list(row["subject_tags"])))
    )
    conn.commit()
    return doc_id


def cmd_add(args):
    conn = connect()
    text = ""
    if args.file:
        p = Path(args.file)
        if not p.exists():
            sys.exit(f"No such file: {p}")
        text = p.read_text(encoding="utf-8", errors="replace")

    try:
        doc_id = add_document(
            conn,
            doc_id=args.id,
            title=args.title or (Path(args.file).stem if args.file else "untitled"),
            doc_type=args.type,
            access_tier=args.tier,
            privilege_reviewed=args.reviewed,
            case_style=args.case_style,
            citation=args.citation,
            cause_number=args.cause,
            court=args.court,
            county=args.county,
            judge=args.judge,
            subject_role=args.role,
            firm_caption=args.firm,
            doc_date=args.date,
            source_url=args.url,
            original_path=args.file,
            subject_tags=args.tags,
            summary=args.summary,
            full_text=text,
        )
    except PrivilegeError as e:
        sys.exit(f"\n{e}\n")

    row = conn.execute("SELECT token_estimate, firm_caption FROM documents WHERE doc_id=?",
                       (doc_id,)).fetchone()
    print(f"Added {doc_id}  (~{row['token_estimate']:,} tokens)")

    era = infer_era(row["firm_caption"])
    if era and not args.date:
        print(f"  Firm caption dates this to approximately {era[0]}-{era[1]}.")


def cmd_seed(args):
    """Load pre-researched case metadata from CSV."""
    conn = connect()
    added, refused = 0, 0
    with open(args.csvfile, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                add_document(conn, **{k: (v or None) for k, v in r.items()})
                added += 1
            except PrivilegeError as e:
                print(f"REFUSED: {r.get('title')}", file=sys.stderr)
                refused += 1
    print(f"Seeded {added} documents. {refused} refused.")
    print("These are metadata stubs. Retrieve the full opinion text and re-add "
          "with --file to make them searchable on content.")


# --------------------------------------------------------------------------
# Retrieval -- whole documents, never fragments
# --------------------------------------------------------------------------

def search(conn, query, limit=5, doc_type=None, county=None, tier=None,
           year_from=None, year_to=None):
    sql = """
        SELECT d.*, bm25(documents_fts) AS score
        FROM documents_fts
        JOIN documents d ON d.doc_id = documents_fts.doc_id
        WHERE documents_fts MATCH ?
    """
    params = [query]
    if doc_type:
        sql += " AND d.doc_type = ?"; params.append(doc_type)
    if county:
        sql += " AND d.county = ?"; params.append(county)
    if tier:
        sql += " AND d.access_tier = ?"; params.append(tier)
    if year_from:
        sql += " AND d.doc_date >= ?"; params.append(f"{year_from}-01-01")
    if year_to:
        sql += " AND d.doc_date <= ?"; params.append(f"{year_to}-12-31")
    sql += " ORDER BY score LIMIT ?"
    params.append(limit)

    try:
        return conn.execute(sql, params).fetchall()
    except sqlite3.OperationalError as e:
        sys.exit(f"Query error: {e}\nFTS5 syntax: quote phrases, use OR / NOT / NEAR().")


def fmt_row(r, verbose=False):
    bits = [f"\n\033[1m{r['title']}\033[0m", f"  id       {r['doc_id']}"]
    if r["citation"]:    bits.append(f"  cite     {r['citation']}")
    if r["case_style"]:  bits.append(f"  style    {r['case_style']}")
    if r["court"]:       bits.append(f"  court    {r['court']}")
    if r["cause_number"]:bits.append(f"  cause    {r['cause_number']}")
    if r["doc_date"]:    bits.append(f"  date     {r['doc_date']} ({r['date_precision']})")
    if r["subject_role"]: bits.append(f"  role     {r['subject_role']}")
    if r["firm_caption"]:bits.append(f"  firm     {r['firm_caption']}")
    bits.append(f"  tier     {r['access_tier']}   verification: {r['verification_status']}")
    if r["token_estimate"]:
        bits.append(f"  size     ~{r['token_estimate']:,} tokens")
    if verbose and r["summary"]:
        bits.append(f"\n  {r['summary']}")
    return "\n".join(bits)


def cmd_search(args):
    conn = connect()
    rows = search(conn, args.query, limit=args.limit, doc_type=args.type,
                  county=args.county, year_from=args.year_from, year_to=args.year_to)
    if not rows:
        print("No matches.")
        print("The archive does not contain an answer. It will not invent one.")
        return
    print(f"{len(rows)} document(s):")
    for r in rows:
        print(fmt_row(r, verbose=True))


def cmd_context(args):
    """
    Assemble whole documents into a context block for a model.
    This is the no-chunking retrieval path: entire documents or nothing.
    """
    conn = connect()
    rows = search(conn, args.query, limit=args.limit)
    if not rows:
        print("No matching documents.", file=sys.stderr)
        return

    budget = args.budget
    used, included, skipped = 0, [], []
    for r in rows:
        t = r["token_estimate"] or 0
        if used + t > budget:
            skipped.append((r["doc_id"], t))
            continue
        included.append(r)
        used += t

    out = []
    out.append("The following are complete documents from the record archive.")
    out.append("Answer only from these documents. Cite doc_id for every factual claim.")
    out.append("If they do not contain the answer, say so. Do not supplement from")
    out.append("general knowledge. Where documents conflict, present the conflict.\n")

    for r in included:
        out.append("=" * 70)
        out.append(f"doc_id: {r['doc_id']}")
        for k in ("title", "citation", "case_style", "court", "cause_number",
                  "doc_date", "subject_role", "verification_status"):
            if r[k]:
                out.append(f"{k}: {r[k]}")
        out.append("=" * 70)
        out.append(r["full_text"] or "(no text -- metadata stub only)")
        out.append("")

    print("\n".join(out))
    print(f"\n[{len(included)} documents, ~{used:,} tokens]", file=sys.stderr)
    for doc_id, t in skipped:
        print(f"[skipped {doc_id} -- ~{t:,} tokens, over budget. "
              f"Use `show` for a targeted read.]", file=sys.stderr)


def cmd_show(args):
    conn = connect()
    r = conn.execute("SELECT * FROM documents WHERE doc_id=?", (args.doc_id,)).fetchone()
    if not r:
        sys.exit(f"No document {args.doc_id!r}")
    print(fmt_row(r, verbose=True))
    for label, key in (("panel", "panel"), ("co-counsel", "co_counsel"),
                       ("opposing", "opposing_counsel"), ("tags", "subject_tags")):
        vals = from_json_list(r[key])
        if vals:
            print(f"  {label:<12} {', '.join(vals)}")
    if r["source_url"]:
        print(f"  source       {r['source_url']}")
    if r["notes"]:
        print(f"\n  notes: {r['notes']}")
    if args.text and r["full_text"]:
        print("\n" + "-" * 70 + "\n")
        print(r["full_text"])


def cmd_list(args):
    conn = connect()
    sql = "SELECT * FROM documents"
    params = []
    if args.type:
        sql += " WHERE doc_type = ?"; params.append(args.type)
    sql += " ORDER BY COALESCE(doc_date, '9999'), title"
    for r in conn.execute(sql, params):
        stub = "" if r["full_text"] else "  [metadata only]"
        print(f"{(r['doc_date'] or '????')[:10]}  {r['doc_type']:<12} {r['title']}{stub}")


def cmd_stats(args):
    conn = connect()
    total = conn.execute("SELECT COUNT(*) c FROM documents").fetchone()["c"]
    if not total:
        print("Archive is empty. Run `init` then `seed`.")
        return
    toks = conn.execute("SELECT COALESCE(SUM(token_estimate),0) t FROM documents").fetchone()["t"]
    stubs = conn.execute("SELECT COUNT(*) c FROM documents WHERE full_text IS NULL OR full_text=''").fetchone()["c"]
    quar = conn.execute("SELECT COUNT(*) c FROM quarantine").fetchone()["c"]

    print(f"Documents:        {total}")
    print(f"Metadata-only:    {stubs}  (need full text retrieved)")
    print(f"Total text:       ~{toks:,} tokens")
    print(f"Quarantined:      {quar}")

    print("\nBy type:")
    for r in conn.execute("SELECT doc_type, COUNT(*) c FROM documents GROUP BY doc_type ORDER BY c DESC"):
        print(f"  {r['doc_type']:<14} {r['c']}")
    print("\nBy tier:")
    for r in conn.execute("SELECT access_tier, COUNT(*) c FROM documents GROUP BY access_tier"):
        print(f"  {r['access_tier']:<14} {r['c']}")
    print("\nBy verification:")
    for r in conn.execute("SELECT verification_status, COUNT(*) c FROM documents GROUP BY verification_status"):
        print(f"  {r['verification_status']:<14} {r['c']}")

    if toks and toks < 150_000:
        print(f"\nNote: entire corpus is ~{toks:,} tokens -- it fits in a single")
        print("context window. Retrieval is a convenience, not yet a necessity.")


def cmd_export(args):
    conn = connect()
    rows = [dict(r) for r in conn.execute("SELECT * FROM documents")]
    for r in rows:
        r.pop("full_text", None)
    out = Path(args.out)
    if out.suffix == ".json":
        out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    else:
        if rows:
            with open(out, "w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
                w.writeheader(); w.writerows(rows)
    print(f"Exported {len(rows)} records to {out}")


def cmd_quarantine(args):
    conn = connect()
    rows = conn.execute("SELECT * FROM quarantine ORDER BY attempted_at DESC").fetchall()
    if not rows:
        print("Quarantine is empty.")
        return
    for r in rows:
        print(f"{r['attempted_at'][:10]}  {r['title']}\n    {r['reason']}\n")


# --------------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(description="Nunley Archive")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init").set_defaults(func=cmd_init)

    s = sub.add_parser("seed"); s.add_argument("csvfile"); s.set_defaults(func=cmd_seed)

    a = sub.add_parser("add")
    a.add_argument("--file"); a.add_argument("--title")
    a.add_argument("--id", help="target an existing doc_id -- use this to attach "
                                "full text to a seeded metadata stub")
    a.add_argument("--type", default="other", choices=DOC_TYPES)
    a.add_argument("--tier", required=True, choices=TIERS,
                   help="REQUIRED. RESTRICTED is refused and logged.")
    a.add_argument("--reviewed", action="store_true", help="privilege reviewed by a human")
    a.add_argument("--case-style"); a.add_argument("--citation"); a.add_argument("--cause")
    a.add_argument("--court"); a.add_argument("--county"); a.add_argument("--judge")
    a.add_argument("--role"); a.add_argument("--firm"); a.add_argument("--date")
    a.add_argument("--url"); a.add_argument("--tags"); a.add_argument("--summary")
    a.set_defaults(func=cmd_add)

    s = sub.add_parser("search"); s.add_argument("query")
    s.add_argument("--limit", type=int, default=5)
    s.add_argument("--type", choices=DOC_TYPES); s.add_argument("--county")
    s.add_argument("--year-from"); s.add_argument("--year-to")
    s.set_defaults(func=cmd_search)

    s = sub.add_parser("context", help="emit whole documents as a model context block")
    s.add_argument("query"); s.add_argument("--limit", type=int, default=5)
    s.add_argument("--budget", type=int, default=150_000)
    s.set_defaults(func=cmd_context)

    s = sub.add_parser("show"); s.add_argument("doc_id")
    s.add_argument("--text", action="store_true"); s.set_defaults(func=cmd_show)

    s = sub.add_parser("list"); s.add_argument("--type", choices=DOC_TYPES)
    s.set_defaults(func=cmd_list)

    sub.add_parser("stats").set_defaults(func=cmd_stats)
    sub.add_parser("quarantine").set_defaults(func=cmd_quarantine)

    s = sub.add_parser("export"); s.add_argument("--out", default="archive_export.csv")
    s.set_defaults(func=cmd_export)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

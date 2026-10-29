#!/usr/bin/env python3
"""Import an Enpass JSON export into passage.

Usage:
    enpass2passage.py [--dry-run] [--force] export.json

Entry layout:
    login     <domain>/<email or username>
    password  <title>/<login>
    note      notes/<title>

Archived items get the same path under archived/, for example
archived/<domain>/<email or username>.

Login and password entries:
    <password or "<no password>">
    username: <email or username>
    url: <scheme://host>          (one line per url)
    notes:                        (only if the item has a note)

    <note>

Note entries contain only the note text.

Set PASSAGE to use a different passage executable.
"""

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from collections import Counter
from urllib.parse import urlsplit

PASSAGE = shlex.split(os.environ.get("PASSAGE", "passage"))
NO_PASSWORD = "<no password>"

# Field types that are written to the entry. Any other non-empty field
# produces a warning so that no data is lost silently.
KNOWN_FIELDS = {"username", "email", "password", "url", "section"}

# Item categories that are imported. Other categories, such as identity
# and creditcard, are skipped.
CATEGORIES = {"login", "password", "note"}


def sanitize(name):
    """Turn a title such as "Note (ABC)" into "note_abc"."""
    name = re.sub(r"[^a-z0-9.@+-]+", "_", name.strip().lower())
    return name.strip("_.") or "unnamed"


def parse_url(url):
    url = url.strip()
    if not url:
        return None
    if "://" not in url:
        return urlsplit("//" + url)
    return urlsplit(url)


def url_base(url):
    """https://xxx.yyy.zzz.com/abc -> https://xxx.yyy.zzz.com"""
    parts = parse_url(url)
    if parts is None or not parts.hostname:
        return url.strip()
    host = parts.netloc.rsplit("@", 1)[-1]
    return f"{parts.scheme}://{host}" if parts.scheme else host


def url_domain(url):
    """https://xxx.yyy.zzz.com/abc -> xxx.yyy.zzz.com"""
    parts = parse_url(url)
    if parts is None or not parts.hostname:
        return None
    return parts.hostname.lower().rstrip(".")


def fields_of(item, kind):
    return [
        f["value"].strip()
        for f in item.get("fields", [])
        if not f.get("deleted") and f.get("type") == kind and f.get("value", "").strip()
    ]


def first(item, kind):
    values = fields_of(item, kind)
    return values[0] if values else ""


def warn_unknown_fields(item, path):
    for f in item.get("fields", []):
        if f.get("deleted") or f.get("type") in KNOWN_FIELDS:
            continue
        if f.get("value", "").strip():
            print(
                f"warning: {path}: field '{f.get('label')}' ({f.get('type')}) is not imported",
                file=sys.stderr,
            )


def render_secret(item, user):
    lines = [first(item, "password") or NO_PASSWORD]
    if user:
        lines.append(f"username: {user}")
    for url in fields_of(item, "url"):
        lines.append(f"url: {url_base(url)}")
    note = item.get("note", "").strip()
    if note:
        lines += ["notes:", "", note]
    return "\n".join(lines) + "\n"


def convert(item):
    """Return (path, content) for one Enpass item."""
    category = item.get("category")
    title = item.get("title", "")
    user = first(item, "email") or first(item, "username")

    if category == "login":
        domain = None
        for url in fields_of(item, "url") + [title]:
            domain = url_domain(url) if "." in url else None
            if domain:
                break
        folder = domain or sanitize(title)
        return f"{folder}/{sanitize(user) if user else 'login'}", render_secret(
            item, user
        )

    if category == "password":
        return (
            f"{sanitize(title)}/{sanitize(user) if user else 'password'}",
            render_secret(item, user),
        )

    if category == "note":
        return f"notes/{sanitize(title)}", item.get("note", "").strip() + "\n"


def unique(path, used):
    candidate, n = path, 2
    while candidate in used:
        candidate = f"{path}_{n}"
        n += 1
    used.add(candidate)
    return candidate


def insert(path, content, force):
    cmd = PASSAGE + ["insert", "--multiline"] + (["--force"] if force else []) + [path]
    subprocess.run(cmd, input=content, text=True, check=True, stdout=subprocess.DEVNULL)


def main():
    parser = argparse.ArgumentParser(
        description="Import an Enpass JSON export into passage."
    )
    parser.add_argument("export", help="Enpass JSON export file")
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="print the entries instead of inserting them",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="overwrite existing passage entries without asking",
    )
    args = parser.parse_args()

    with open(args.export, encoding="utf-8") as fp:
        items = json.load(fp)["items"]

    used = set()
    count = 0
    skipped = Counter()
    for item in items:
        if item.get("trashed"):
            continue
        if item.get("category") not in CATEGORIES:
            skipped[item.get("category")] += 1
            continue
        path, content = convert(item)
        if item.get("archived") == 1:
            path = f"archived/{path}"
        path = unique(path, used)
        warn_unknown_fields(item, path)
        if args.dry_run:
            print(f"==> {path}\n{content}")
        else:
            insert(path, content, args.force)
            print(f"imported {path}")
        count += 1

    print(f"{count} entries {'found' if args.dry_run else 'imported'}", file=sys.stderr)
    for category, n in sorted(skipped.items()):
        print(f"skipped {n} {category} item(s)", file=sys.stderr)


if __name__ == "__main__":
    main()

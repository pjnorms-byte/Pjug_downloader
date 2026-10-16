"""Scans the games/ folder and writes games/games.json for pjug.

Run:  python make_games.py
A game is either:
  - a single .html file directly inside games/
  - a folder inside games/ that has an index.html (or exactly one .html file)
Names come from the page <title>, or the file/folder name. To rename a game or add a
description, edit games/games.json by hand; your edits are kept on the next run.
"""
import json
import os
import re
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
GAMES = os.path.join(ROOT, "games")
OUT = os.path.join(GAMES, "games.json")
GENERIC = {"", "index", "untitled", "document", "home", "game", "untitled document"}


def pretty(s):
    return re.sub(r"[-_]+", " ", s).strip().title()


def title_of(path, fallback):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            head = f.read(8192)
        m = re.search(r"<title[^>]*>(.*?)</title>", head, re.I | re.S)
        if m:
            t = re.sub(r"\s+", " ", m.group(1)).strip()
            if t.lower() not in GENERIC and len(t) <= 40:
                return t
    except OSError:
        pass
    return fallback


def find():
    found = []
    for name in sorted(os.listdir(GAMES), key=str.lower):
        if name.startswith(".") or name == "games.json":
            continue
        p = os.path.join(GAMES, name)
        if os.path.isdir(p):
            if os.path.isfile(os.path.join(p, "index.html")):
                entry = "index.html"
            else:
                htmls = [f for f in os.listdir(p) if f.lower().endswith(".html")]
                if len(htmls) != 1:
                    print("skipped (no index.html):", name)
                    continue
                entry = htmls[0]
            found.append((name + "/" + entry, os.path.join(p, entry), pretty(name)))
        elif name.lower().endswith(".html"):
            found.append((name, p, pretty(os.path.splitext(name)[0])))
    return found


def main():
    old = {}
    try:
        with open(OUT, encoding="utf-8") as f:
            old = {e["path"]: e for e in json.load(f) if isinstance(e, dict) and "path" in e}
    except Exception:
        pass
    out = []
    for path, file, fallback in find():
        q = quote(path, safe="/")
        prev = old.get(q, {})
        out.append({
            "name": prev.get("name") or title_of(file, fallback),
            "desc": prev.get("desc", ""),
            "path": q,
        })
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Wrote %d games to games/games.json" % len(out))


if __name__ == "__main__":
    main()

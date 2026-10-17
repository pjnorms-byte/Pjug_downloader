"""Scans the pjug-files folder recursively and writes pjug-files/games.json.

Existing files are preserved when importing UGS files. Existing names and descriptions
in games.json are retained for matching paths; newly discovered HTML games are added.
"""
import json
import os
import re
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))


def find_dir():
    for name in sorted(os.listdir(ROOT)):
        if os.path.isdir(os.path.join(ROOT, name)) and name.lower().replace(" ", "-") == "pjug-files":
            return os.path.join(ROOT, name)
    old = os.path.join(ROOT, "games")
    if os.path.isdir(old):
        return old
    os.makedirs(os.path.join(ROOT, "pjug-files"), exist_ok=True)
    return os.path.join(ROOT, "pjug-files")


GAMES = find_dir()
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
            if t.lower() not in GENERIC and len(t) <= 80:
                return t
    except OSError:
        pass
    return fallback


def find():
    found = []
    for root, dirs, files in os.walk(GAMES):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        for name in sorted(files, key=str.lower):
            if name.startswith(".") or name.lower() == "games.json" or not name.lower().endswith(".html"):
                continue
            full = os.path.join(root, name)
            rel = os.path.relpath(full, GAMES).replace(os.sep, "/")
            found.append((rel, full, pretty(os.path.splitext(name)[0])))
    found.sort(key=lambda item: item[0].lower())
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
    for path, entry in old.items():
        if path.lower().startswith(("http://", "https://")):
            out.append(entry)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Wrote %d games to %s" % (len(out), OUT))


if __name__ == "__main__":
    main()

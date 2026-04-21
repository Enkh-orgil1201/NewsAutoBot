import hashlib
import json
import os
import re
from config import POSTED_FILE


def load_posted() -> set:
    if not os.path.exists(POSTED_FILE):
        return set()
    try:
        with open(POSTED_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()


def save_posted(posted_ids: set) -> None:
    with open(POSTED_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(posted_ids), f, ensure_ascii=False, indent=2)


def mark_posted(*ids: str) -> None:
    posted = load_posted()
    for i in ids:
        if i:
            posted.add(i)
    save_posted(posted)


def title_fingerprint(title: str) -> str:
    norm = re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()
    return "title:" + hashlib.md5(norm.encode("utf-8")).hexdigest()[:16]

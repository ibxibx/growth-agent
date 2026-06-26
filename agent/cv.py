"""
cv.py — extract a candidate's skills from raw CV text.

Keeps it dependency-free: matches the same canonical skill vocabulary the market
module uses, by word boundary, against the CV text. Works on plain text pasted
or read from a .txt/.md file. (PDF/DOCX extraction can be layered on later.)
"""
import re

from .market import CANONICAL_SKILLS


def skills_from_cv_text(text: str) -> list[str]:
    """Return the canonical skills mentioned anywhere in the CV text."""
    low = text.lower()
    found = []
    for skill in (s.lower() for s in CANONICAL_SKILLS):
        if re.search(rf"(?<![a-z]){re.escape(skill)}(?![a-z])", low):
            found.append(skill)
    return found


def read_cv_file(path: str) -> str:
    """Read CV text from a .txt or .md file. Returns '' on failure."""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except OSError:
        return ""


def merge_skills(profile_skills: list[str], cv_skills: list[str]) -> list[str]:
    """Union of profile keywords and CV-extracted skills, lowercased, deduped."""
    seen, out = set(), []
    for s in [*(profile_skills or []), *(cv_skills or [])]:
        sl = s.lower().strip()
        if sl and sl not in seen:
            seen.add(sl)
            out.append(sl)
    return out

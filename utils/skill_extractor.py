# utils/skill_extractor.py
# FULLY FIXED VERSION
#
# ROOT CAUSE OF THE BUG (why only 3 skills were detected):
#
#   1. The old SKILLS_DB was missing almost all cybersecurity skills
#      (no: bash, burp suite, incident response, vulnerability assessment,
#       ids, ips, iso 27001, nmap, metasploit, wireshark, etc.)
#
#   2. The skill "c" (the programming language) was matching INSIDE other
#      words because plain substring matching has no word boundaries.
#      Example: "c" matched inside "sec", "inc", "network", "practice" etc.
#      → inflating Skill Match % to 75% for everyone
#
#   3. Multi-word skills like "network security", "burp suite",
#      "incident response" were not found because they were missing from DB
#
# FIXES APPLIED:
#   - Rebuilt SKILLS_DB with 200+ skills across 12 categories
#   - All cybersecurity skills are now fully covered
#   - Word-boundary regex (\b) used for all skills — no false partial matches
#   - Special handling for short ambiguous skills ("c", "r", "go")
#   - extract_skills() runs on RAW text (not preprocessed) for accuracy

import re

# ─────────────────────────────────────────────────────────────────────────────
# SKILLS DATABASE — 200+ skills across 12 categories
# SORTED longest-first so multi-word skills are matched before single words
# ─────────────────────────────────────────────────────────────────────────────

import json
import os

# ─────────────────────────────────────────────────────────────────────────────
# LOAD SKILLS DATABASE from external JSON
# ─────────────────────────────────────────────────────────────────────────────
_skills_path = os.path.join(os.path.dirname(__file__), "skills.json")

try:
    with open(_skills_path, "r", encoding="utf-8") as f:
        _data = json.load(f)
        SKILLS_DB = _data.get("SKILLS_DB", [])
        SHORT_SKILLS = set(_data.get("SHORT_SKILLS", []))
except Exception as e:
    print(f"Warning: Could not load skills.json ({e}). Falling back to empty defaults.")
    SKILLS_DB = []
    SHORT_SKILLS = set()


def _skill_found(skill: str, text_lower: str) -> bool:
    """
    Check if a skill is present in text using safe word-boundary matching.

    For most skills: use \b word boundaries via regex.
    For short/ambiguous skills (c, r, go): require surrounding whitespace
    or punctuation to prevent matching inside longer words.
    """
    if skill in SHORT_SKILLS:
        # Extra strict: must be preceded and followed by non-alphanumeric chars
        pattern = r'(?<![a-zA-Z0-9])' + re.escape(skill) + r'(?![a-zA-Z0-9])'
    else:
        pattern = r'\b' + re.escape(skill) + r'\b'

    return bool(re.search(pattern, text_lower))


def extract_skills(text: str) -> list:
    """
    Extract all recognised skills from raw resume or JD text.

    IMPORTANT: Always call this with RAW (unprocessed) text —
    the preprocessor removes special characters which breaks
    multi-word and symbol skills like 'ssl/tls', 'burp suite', 'c++'.

    Returns:
        Sorted list of matched skill strings (lowercase).
    """
    if not text or not isinstance(text, str):
        return []

    text_lower = text.lower()
    found = set()

    for skill in SKILLS_DB:
        if _skill_found(skill, text_lower):
            found.add(skill)

    return sorted(list(found))


def get_skill_match(jd_skills: list, resume_skills: list):
    """
    Compare skills found in job description vs skills found in resume.

    Args:
        jd_skills     : list from extract_skills(raw_jd_text)
        resume_skills : list from extract_skills(raw_resume_text)

    Returns:
        matched  (list)  — skills present in BOTH
        missing  (list)  — skills in JD but NOT in resume
        score    (float) — % of JD skills the candidate has (0.0–100.0)
    """
    if not jd_skills:
        return [], [], 0.0

    jd_set     = set(jd_skills)
    resume_set = set(resume_skills)

    matched = sorted(list(jd_set.intersection(resume_set)))
    missing = sorted(list(jd_set.difference(resume_set)))
    score   = round(len(matched) / len(jd_set) * 100, 1)

    return matched, missing, score
"""Communication tone contract for ACC. Caveman-strict is default everywhere."""
from __future__ import annotations
import re

FILLER = [
    "I have successfully",
    "I have completed",
    "has been successfully",
    "has been updated",
    "I would like to",
    "please note that",
    "it is worth noting",
    "in order to",
    "as you can see",
    "I am happy to",
    "I will now",
    "let me",
    "certainly",
]

CAVEMAN_REPLACEMENTS = {
    "implemented": "done",
    "completed": "done",
    "successfully": "",
    "I will proceed to": "",
    "please find": "here",
    "utilize": "use",
    "regarding": "about",
    "however": "but",
    "therefore": "so",
    "additionally": "also",
}

JARGON_PLAIN = {
    "tenant isolation": "keeping each user's data separate",
    "row level security": "who-can-see-what rules",
    "rls": "who-can-see-what rules",
    "rbac": "who-can-do-what rules",
    "idempotent": "safe to run twice",
    "regression": "an old bug came back",
    "monkeypatch": "quick temporary patch",
    "refactor": "tidy the code",
    "middleware": "in-between step",
}


def plain_words(text: str) -> str:
    """Swap developer jargon for plain words. Longest keys first."""
    result = text
    for term in sorted(JARGON_PLAIN, key=len, reverse=True):
        result = re.sub(
            r"\b" + re.escape(term) + r"\b",
            JARGON_PLAIN[term],
            result,
            flags=re.IGNORECASE,
        )
    return result


def apply_tone(text: str, mode: str | None = None) -> str:
    mode = (mode or "caveman-strict").strip().lower()
    if mode == "normal":
        return text
    result = text
    for filler in FILLER:
        result = re.sub(re.escape(filler), "", result, flags=re.IGNORECASE)
    for word, replacement in CAVEMAN_REPLACEMENTS.items():
        result = re.sub(r"\b" + re.escape(word) + r"\b", replacement, result, flags=re.IGNORECASE)
    result = re.sub(r" {2,}", " ", result).strip()
    result = plain_words(result)
    if mode == "caveman-strict":
        sentences = [s for s in result.split(". ") if s.strip()]
        if len(sentences) > 2 and len(result) > 240:
            result = ". ".join(sentences[:2]).rstrip(".") + "."
    return result or text


def skill_banner(skill_name: str, mode: str | None = None) -> str:
    name = skill_name.capitalize()
    return f"{name}: ready."

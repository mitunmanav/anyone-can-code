#!/usr/bin/env python3
"""Soft tips: cheap vs strong Codex models (Luna / Terra / Sol).

Honest limit: ACC cannot force the Codex model picker. User chooses
in Desktop UI, CLI `/model` / `-m`, or config.toml.

Prices are a local snapshot (API short context, post 2026-07-30 cut).
Always re-check official pricing URLs before budgeting spend.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

# Snapshot as of research 2026-08-03. Source: OpenAI API pricing page.
PRICES_AS_OF = "2026-08-03"
PRICING_URL = "https://developers.openai.com/api/docs/pricing"
CODEX_MODELS_URL = "https://developers.openai.com/codex/models"
GPT56_URL = "https://openai.com/index/gpt-5-6/"
PRICE_CUT_URL = (
    "https://openai.com/index/advancing-the-price-performance-frontier-with-gpt-5-6/"
)

HONESTY = (
    "ACC cannot force Codex model picker. "
    "You pick model in Desktop UI, CLI /model or -m, or config.toml."
)

# API short-context $ per 1M tokens (input / output).
TIERS: dict[str, dict[str, Any]] = {
    "luna": {
        "tier": "luna",
        "label": "Luna",
        "model_id": "gpt-5.6-luna",
        "role": "cheap / fast / clear repeatable work",
        "input_per_1m": 0.20,
        "output_per_1m": 1.20,
        "when": "rename, lint, format, classify, extract, structured summary",
    },
    "terra": {
        "tier": "terra",
        "label": "Terra",
        "model_id": "gpt-5.6-terra",
        "role": "everyday balance (workhorse)",
        "input_per_1m": 2.00,
        "output_per_1m": 12.00,
        "when": "normal feature, bug fix, everyday code",
    },
    "sol": {
        "tier": "sol",
        "label": "Sol",
        "model_id": "gpt-5.6-sol",
        "role": "strong / hard / open-ended",
        "input_per_1m": 5.00,
        "output_per_1m": 30.00,
        "when": "architecture, security, deep research, ambiguous hard work",
    },
}

# Stronger signal wins: sol > luna > terra default.
_LUNA_KW = re.compile(
    r"\b("
    r"micro|rename|lint|format|classify|extract|summar(y|ize)|"
    r"boilerplate|typo|indent|css\s*only|trivial|repeatable|"
    r"batch\s*label|cheap|fast\s*only"
    r")\b",
    re.I,
)
_SOL_KW = re.compile(
    r"\b("
    r"architect(ure)?|security|audit|research|ambiguous|"
    r"hard|complex|redesign|migrate\s*all|threat|cyber|"
    r"open[- ]ended|deep\s*dive|flagship|max\s*effort"
    r")\b",
    re.I,
)
_TERRA_KW = re.compile(
    r"\b("
    r"feature|bug|fix|implement|everyday|refactor|"
    r"test|hook|skill|api|endpoint|ui\s*change"
    r")\b",
    re.I,
)


def classify_task(task: str) -> str:
    """Map free text → luna | terra | sol. Soft keyword rules only."""
    text = (task or "").strip()
    if not text:
        return "terra"
    # Sol first: hard work should not silently downgrade.
    if _SOL_KW.search(text):
        return "sol"
    if _LUNA_KW.search(text):
        return "luna"
    if _TERRA_KW.search(text):
        return "terra"
    return "terra"


def tier_catalog() -> list[dict[str, Any]]:
    return [dict(TIERS[k]) for k in ("luna", "terra", "sol")]


def recommend(task: str) -> dict[str, Any]:
    """Soft recommendation for a task description."""
    tier_key = classify_task(task)
    meta = TIERS[tier_key]
    tip = (
        f"Soft tip: pick {meta['label']} ({meta['model_id']}) in Codex model UI "
        f"or `codex -m {meta['model_id']}`. "
        f"Role: {meta['role']}. "
        f"API snapshot ${meta['input_per_1m']}/${meta['output_per_1m']} per 1M in/out "
        f"(as of {PRICES_AS_OF}; re-check {PRICING_URL})."
    )
    return {
        "tier": meta["tier"],
        "label": meta["label"],
        "model_id": meta["model_id"],
        "role": meta["role"],
        "when": meta["when"],
        "task": (task or "").strip(),
        "tip": tip,
        "honesty": HONESTY,
        "prices": {
            "input_per_1m": meta["input_per_1m"],
            "output_per_1m": meta["output_per_1m"],
            "currency": "USD",
            "context": "api_short",
        },
        "as_of": PRICES_AS_OF,
        "urls": {
            "pricing": PRICING_URL,
            "codex_models": CODEX_MODELS_URL,
            "gpt56": GPT56_URL,
            "price_cut": PRICE_CUT_URL,
        },
    }


def format_card(task: str) -> str:
    rec = recommend(task)
    lines = [
        "WHERE: cost-guard",
        f"TIER: {rec['label']} ({rec['model_id']})",
        f"ROLE: {rec['role']}",
        f"PRICE: ${rec['prices']['input_per_1m']}/${rec['prices']['output_per_1m']} per 1M in/out (API short · {rec['as_of']})",
        f"TIP: {rec['tip']}",
        f"HONESTY: {rec['honesty']}",
        "NEXT: user picks model · optional $usage for token disk status",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Soft Codex model tier tips (Luna/Terra/Sol). Cannot force picker."
    )
    parser.add_argument(
        "task",
        nargs="*",
        help="Task description words (default: empty → Terra)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of card text",
    )
    parser.add_argument(
        "--catalog",
        action="store_true",
        help="List all tiers (ignore task classification)",
    )
    args = parser.parse_args(argv)
    task = " ".join(args.task).strip()

    if args.catalog:
        payload: dict[str, Any] = {
            "as_of": PRICES_AS_OF,
            "honesty": HONESTY,
            "urls": {
                "pricing": PRICING_URL,
                "codex_models": CODEX_MODELS_URL,
            },
            "tiers": tier_catalog(),
        }
        if args.json:
            print(json.dumps(payload, indent=2 if sys.stdout.isatty() else None))
        else:
            for t in payload["tiers"]:
                print(
                    f"{t['label']:5} {t['model_id']:14} "
                    f"${t['input_per_1m']}/${t['output_per_1m']}  {t['role']}"
                )
            print(HONESTY)
        return 0

    rec = recommend(task)
    if args.json:
        print(json.dumps(rec, indent=2 if sys.stdout.isatty() else None))
    else:
        print(format_card(task))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

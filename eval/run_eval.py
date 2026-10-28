#!/usr/bin/env python3
"""Evaluate SpringGuard (+ optional OCR) against gold bugs."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from spring_guard import scan  # noqa: E402


def hit(bug: dict, findings: list[dict]) -> bool:
    file_key = bug["file_contains"].lower()
    keys = [k.lower() for k in bug["rule_any"]]
    for f in findings:
        blob = " ".join(
            str(f.get(x, "")) for x in ("file", "rule", "message", "evidence", "id")
        ).lower()
        if file_key not in blob and file_key not in str(f.get("file", "")).lower():
            continue
        if any(k in blob for k in keys):
            return True
    return False


def main() -> None:
    gold = json.loads((ROOT / "eval" / "gold.json").read_text(encoding="utf-8"))
    project = ROOT / gold["project"]
    guard = scan(project)["findings"]

    merged_path = ROOT / "out" / "merged.json"
    ocr_findings = []
    if merged_path.exists():
        merged = json.loads(merged_path.read_text(encoding="utf-8"))
        ocr_findings = [f for f in merged.get("findings", []) if f.get("source") == "open-code-review"]

    modes = {
        "spring_guard": guard,
        "ocr_only": ocr_findings,
        "hybrid": guard + ocr_findings,
    }
    report = {"cases": len(gold["bugs"]), "modes": {}}
    for name, findings in modes.items():
        tp = sum(1 for b in gold["bugs"] if hit(b, findings))
        recall = tp / len(gold["bugs"]) if gold["bugs"] else 0
        report["modes"][name] = {
            "findings": len(findings),
            "tp": tp,
            "recall": round(recall, 4),
            "missed": [b["id"] for b in gold["bugs"] if not hit(b, findings)],
        }
    out = ROOT / "eval" / "results.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()

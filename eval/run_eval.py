#!/usr/bin/env python3
"""Evaluate SpringGuard (+ optional OCR): Recall on buggy, Precision via clean + unmatched."""

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


def finding_matches_gold(finding: dict, bugs: list[dict]) -> bool:
    return any(hit(b, [finding]) for b in bugs)


def mode_metrics(name: str, findings: list[dict], bugs: list[dict]) -> dict:
    tp = sum(1 for b in bugs if hit(b, findings))
    recall = tp / len(bugs) if bugs else 0.0
    matched = sum(1 for f in findings if finding_matches_gold(f, bugs))
    unmatched = len(findings) - matched
    # finding-level precision on buggy set: matched findings / all findings
    precision = matched / len(findings) if findings else 1.0
    return {
        "findings": len(findings),
        "tp": tp,
        "recall": round(recall, 4),
        "missed": [b["id"] for b in bugs if not hit(b, findings)],
        "matched_findings": matched,
        "unmatched_findings": unmatched,
        "precision": round(precision, 4),
    }


def main() -> None:
    gold = json.loads((ROOT / "eval" / "gold.json").read_text(encoding="utf-8"))
    bugs = gold["bugs"]
    buggy_project = ROOT / gold["project"]
    clean_project = ROOT / gold.get("clean_project", "samples/spring-clean")

    guard_buggy = scan(buggy_project)["findings"]
    guard_clean = scan(clean_project)["findings"]

    merged_path = ROOT / "out" / "merged.json"
    ocr_findings = []
    if merged_path.exists():
        merged = json.loads(merged_path.read_text(encoding="utf-8"))
        ocr_findings = [
            f
            for f in merged.get("findings", [])
            if f.get("source") == "open-code-review"
        ]

    modes = {
        "spring_guard": guard_buggy,
        "ocr_only": ocr_findings,
        "hybrid": guard_buggy + ocr_findings,
    }

    report = {
        "cases": len(bugs),
        "projects": {
            "buggy": str(gold["project"]),
            "clean": str(gold.get("clean_project", "samples/spring-clean")),
        },
        "modes": {},
        "clean": {
            "findings": len(guard_clean),
            "false_positives": len(guard_clean),
            "precision": 1.0 if not guard_clean else 0.0,
            "rules": sorted({f.get("rule", "") for f in guard_clean}),
        },
    }

    for name, findings in modes.items():
        m = mode_metrics(name, findings, bugs)
        # combine clean FPs into an overall precision for guard-like modes
        if name == "spring_guard":
            fp = m["unmatched_findings"] + len(guard_clean)
            tp_f = m["matched_findings"]
            overall_p = tp_f / (tp_f + fp) if (tp_f + fp) else 1.0
            m["precision_with_clean"] = round(overall_p, 4)
        report["modes"][name] = m

    out = ROOT / "eval" / "results.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Run SpringGuard + Open Code Review, merge outputs for demo/eval."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from spring_guard import scan  # noqa: E402


def run_ocr(project: Path, out_json: Path, mode: str = "scan") -> dict:
    ocr = shutil.which("ocr")
    if not ocr:
        return {"ok": False, "error": "ocr 未安装：npm i -g @alibaba-group/open-code-review"}
    out_json.parent.mkdir(parents=True, exist_ok=True)
    rule = ROOT / ".opencodereview" / "rule.json"
    common = [
        "--repo",
        str(project),
        "--format",
        "json",
        "--output",
        str(out_json),
        "--audience",
        "agent",
        "--provider",
        "ollama",
        "--model",
        "qwen3.5:4b",
        "--timeout",
        "3",  # minutes; local small models are slow — demo uses Guard as primary
    ]
    if rule.exists():
        common.extend(["--rule", str(rule)])
    if mode == "review":
        cmd = [ocr, "review", *common]
    else:
        # path relative to repo: scan Java sources
        cmd = [ocr, "scan", *common, "--path", "src"]
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60 * 25)
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": "ocr 超时", "elapsed_sec": time.time() - t0}
    elapsed = time.time() - t0
    payload = None
    if out_json.exists():
        try:
            payload = json.loads(out_json.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            payload = None
    return {
        "ok": proc.returncode == 0 and payload is not None,
        "returncode": proc.returncode,
        "elapsed_sec": round(elapsed, 2),
        "stdout_tail": (proc.stdout or "")[-2000:],
        "stderr_tail": (proc.stderr or "")[-2000:],
        "result": payload,
        "cmd": cmd,
    }


def normalize_ocr_findings(ocr_payload) -> list[dict]:
    if not ocr_payload:
        return []
    # OCR JSON shape may vary by version; best-effort extraction
    items = []
    if isinstance(ocr_payload, list):
        raw = ocr_payload
    elif isinstance(ocr_payload, dict):
        raw = (
            ocr_payload.get("comments")
            or ocr_payload.get("findings")
            or ocr_payload.get("results")
            or ocr_payload.get("issues")
            or []
        )
        if isinstance(raw, dict):
            raw = raw.get("items") or raw.get("comments") or []
    else:
        raw = []
    for i, it in enumerate(raw):
        if not isinstance(it, dict):
            continue
        items.append(
            {
                "id": it.get("id") or f"ocr-{i}",
                "severity": (it.get("severity") or it.get("level") or "medium"),
                "rule": it.get("rule") or it.get("category") or "ocr",
                "file": it.get("file") or it.get("path") or it.get("filename") or "",
                "line": it.get("line") or it.get("startLine") or it.get("line_number") or 0,
                "message": it.get("message") or it.get("body") or it.get("comment") or json.dumps(it, ensure_ascii=False)[:300],
                "evidence": it.get("evidence") or it.get("snippet") or "",
                "source": "open-code-review",
            }
        )
    return items


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=str(ROOT / "samples" / "spring-buggy"))
    ap.add_argument("--out-dir", default=str(ROOT / "out"))
    ap.add_argument("--skip-ocr", action="store_true")
    ap.add_argument("--ocr-mode", choices=["scan", "review"], default="scan")
    args = ap.parse_args()

    project = Path(args.project).resolve()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    guard = scan(project)
    (out_dir / "spring_guard.json").write_text(
        json.dumps(guard, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    ocr_meta = {"ok": False, "skipped": True}
    ocr_findings: list[dict] = []
    if not args.skip_ocr:
        ocr_meta = run_ocr(project, out_dir / "ocr_raw.json", mode=args.ocr_mode)
        ocr_meta.pop("cmd", None)
        ocr_findings = normalize_ocr_findings(ocr_meta.get("result"))
        (out_dir / "ocr_findings.json").write_text(
            json.dumps(ocr_findings, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    merged = {
        "project": str(project),
        "spring_guard": guard["summary"],
        "ocr": {
            "ok": ocr_meta.get("ok"),
            "elapsed_sec": ocr_meta.get("elapsed_sec"),
            "error": ocr_meta.get("error"),
            "findings": len(ocr_findings),
        },
        "findings": guard["findings"] + ocr_findings,
    }
    (out_dir / "merged.json").write_text(
        json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps({
        "guard_findings": guard["summary"]["count"],
        "ocr_ok": ocr_meta.get("ok"),
        "ocr_findings": len(ocr_findings),
        "merged": str(out_dir / "merged.json"),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

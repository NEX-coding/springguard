#!/usr/bin/env python3
"""SpringGuard — deterministic Spring smell detector (team-owned).

Complements alibaba/open-code-review with cheap, reproducible static checks
that do not depend on an LLM.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Finding:
    id: str
    severity: str
    rule: str
    file: str
    line: int
    message: str
    evidence: str
    source: str = "spring-guard"


def _iter_java(root: Path):
    for p in sorted(root.rglob("*.java")):
        if any(part in {"target", ".git", "build"} for part in p.parts):
            continue
        yield p


def scan_file(path: Path, root: Path) -> list[Finding]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    rel = str(path.relative_to(root))
    name = path.name
    findings: list[Finding] = []

    def add(fid: str, sev: str, rule: str, line: int, msg: str, ev: str):
        findings.append(
            Finding(
                id=fid,
                severity=sev,
                rule=rule,
                file=rel,
                line=line,
                message=msg,
                evidence=ev.strip(),
            )
        )

    def code_only(chunk: str) -> str:
        # 去掉 // 注释，避免注释里的 @Valid 干扰判定
        out = []
        for ln in chunk.splitlines():
            out.append(ln.split("//", 1)[0])
        return "\n".join(out)

    # Controller: @RequestBody without @Valid/@Validated nearby
    if name.endswith("Controller.java"):
        for i, line in enumerate(lines, 1):
            code_line = code_only(line)
            if "@RequestBody" in code_line and "@Valid" not in code_line and "@Validated" not in code_line:
                window = code_only("\n".join(lines[max(0, i - 3) : i + 2]))
                if "@Valid" not in window and "@Validated" not in window:
                    add(
                        f"{rel}:{i}:missing-valid",
                        "high",
                        "spring.controller.missing_valid",
                        i,
                        "@RequestBody 入参缺少 @Valid/@Validated",
                        line,
                    )
            # Map/Optional 取值后直接调用实例方法（常见 NPE）
            if re.search(r'\.get\s*\([^)]*\)\s*\.\s*\w+\s*\(', code_line):
                add(
                    f"{rel}:{i}:npe-chain",
                    "medium",
                    "spring.controller.npe_risk",
                    i,
                    "可能对可空返回值直接链式调用，存在 NPE 风险",
                    line,
                )
            if re.search(r'\b\w+\.toLowerCase\s*\(', code_line) or re.search(r'\b\w+\.trim\s*\(', code_line):
                # 若近期有 Map.get 赋值到同名变量，标为风险
                prev = "\n".join(lines[max(0, i - 6) : i])
                m = re.search(r'\b(\w+)\s*=\s*\w+\.get\s*\(', prev)
                use = re.search(r'\b(\w+)\.(toLowerCase|trim)\s*\(', code_line)
                if m and use and m.group(1) == use.group(1):
                    add(
                        f"{rel}:{i}:npe-chain",
                        "medium",
                        "spring.controller.npe_risk",
                        i,
                        "变量来自 Map.get 后未判空即调用方法，存在 NPE 风险",
                        line,
                    )

    # Service: @Transactional + this.xxx(
    if name.endswith("Service.java"):
        has_tx = any("@Transactional" in ln for ln in lines)
        if has_tx:
            for i, line in enumerate(lines, 1):
                if re.search(r"\bthis\.\w+\(", line):
                    add(
                        f"{rel}:{i}:tx-self-invocation",
                        "high",
                        "spring.service.tx_self_invocation",
                        i,
                        "@Transactional 方法内 this.xxx() 自调用，可能导致事务代理失效",
                        line,
                    )
                if "catch" in line:
                    # look ahead for empty swallow
                    block = "\n".join(lines[i - 1 : min(len(lines), i + 6)])
                    if "print" in block.lower() and "throw" not in block:
                        add(
                            f"{rel}:{i}:tx-swallow",
                            "medium",
                            "spring.service.tx_swallow_exception",
                            i,
                            "事务方法中捕获异常后可能吞掉，影响回滚语义",
                            block[:200],
                        )

        for i, line in enumerate(lines, 1):
            if '"' in line and ("SELECT" in line.upper() or "LIKE" in line.upper() or "+" in line):
                if "LIKE" in line.upper() and "+" in line:
                    add(
                        f"{rel}:{i}:sql-concat",
                        "critical",
                        "spring.sql.string_concat",
                        i,
                        "疑似用字符串拼接构造 SQL/条件，存在注入风险",
                        line,
                    )

    # Mapper: ${} in annotation
    if any(name.endswith(suf) for suf in ("Mapper.java", "Repository.java", "Dao.java")):
        for i, line in enumerate(lines, 1):
            if "${" in line:
                add(
                    f"{rel}:{i}:mybatis-dollar",
                    "critical",
                    "spring.mybatis.dollar_injection",
                    i,
                    "MyBatis 注解使用 ${}，易导致 SQL 注入",
                    line,
                )

    return findings


def scan(root: Path) -> dict:
    root = root.resolve()
    all_findings: list[Finding] = []
    files = 0
    for p in _iter_java(root):
        files += 1
        all_findings.extend(scan_file(p, root))
    by_sev: dict[str, int] = {}
    for f in all_findings:
        by_sev[f.severity] = by_sev.get(f.severity, 0) + 1
    return {
        "tool": "spring-guard",
        "project": str(root),
        "files_scanned": files,
        "findings": [asdict(f) for f in all_findings],
        "summary": {"count": len(all_findings), "by_severity": by_sev},
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="SpringGuard deterministic scanner")
    ap.add_argument("--project", required=True)
    ap.add_argument("--out", default="-")
    args = ap.parse_args()
    result = scan(Path(args.project))
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out == "-":
        print(text)
    else:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out} ({result['summary']['count']} findings)")


if __name__ == "__main__":
    main()

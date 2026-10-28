#!/usr/bin/env python3
"""SpringGuard web app — usable by others on the same machine/LAN.

Endpoints:
  GET  /                 UI
  POST /api/scan/sample  scan built-in spring-buggy
  POST /api/scan/upload  multipart zip of a Spring/Java project
  GET  /api/eval         gold-set eval results (recomputed)
  GET  /api/health
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import traceback
import zipfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
SAMPLE = ROOT / "samples" / "spring-buggy"
sys.path.insert(0, str(ROOT / "scripts"))
from spring_guard import scan  # noqa: E402

MAX_UPLOAD = 50 * 1024 * 1024  # 50MB


def _json(handler: SimpleHTTPRequestHandler, code: int, payload: dict):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def _run_eval() -> dict:
    import importlib.util

    guard = scan(SAMPLE)
    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    (out / "spring_guard.json").write_text(
        json.dumps(guard, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "merged.json").write_text(
        json.dumps(
            {
                "findings": guard["findings"],
                "spring_guard": {"count": guard["summary"]["count"]},
                "ocr": {"findings": 0},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    spec = importlib.util.spec_from_file_location(
        "run_eval", ROOT / "eval" / "run_eval.py"
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    mod.main()
    return json.loads((ROOT / "eval" / "results.json").read_text(encoding="utf-8"))


def _pick_project_root(dest: Path) -> Path:
    """Prefer folder that contains src/main/java or the most *.java files."""
    java_files = [p for p in dest.rglob("*.java") if "__MACOSX" not in p.parts]
    if not java_files:
        return dest
    for p in java_files:
        try:
            rel = p.relative_to(dest)
        except ValueError:
            continue
        if "src" in rel.parts:
            idx = rel.parts.index("src")
            return dest.joinpath(*rel.parts[:idx]) if idx > 0 else dest
    counts: dict[Path, int] = {}
    for p in java_files:
        counts[p.parent] = counts.get(p.parent, 0) + 1
    best = max(counts, key=counts.get)
    cur = best
    for _ in range(6):
        if (cur / "src").is_dir() or (cur / "pom.xml").exists() or (cur / "build.gradle").exists():
            return cur
        if cur == dest or cur.parent == cur:
            break
        cur = cur.parent
    return dest


def _safe_extract(zf: zipfile.ZipFile, dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    for info in zf.infolist():
        name = info.filename
        if name.startswith("/") or ".." in Path(name).parts:
            continue
        target = dest / name
        if info.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)
    kids = [p for p in dest.iterdir() if p.name != "__MACOSX"]
    root = kids[0] if len(kids) == 1 and kids[0].is_dir() else dest
    return _pick_project_root(root)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB), **kwargs)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/health":
            return _json(self, 200, {"ok": True, "tool": "springguard"})
        if path == "/api/eval":
            try:
                data = _run_eval()
                return _json(self, 200, data)
            except Exception as e:
                return _json(self, 500, {"error": str(e), "trace": traceback.format_exc()})
        if path in ("/", "/index.html"):
            self.path = "/index.html"
        return super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            if path == "/api/scan/sample":
                result = scan(SAMPLE)
                # persist for page refresh
                out = ROOT / "out"
                out.mkdir(exist_ok=True)
                (out / "spring_guard.json").write_text(
                    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                return _json(self, 200, result)

            if path == "/api/scan/upload":
                length = int(self.headers.get("Content-Length") or 0)
                if length <= 0 or length > MAX_UPLOAD:
                    return _json(
                        self,
                        400,
                        {"error": f"上传大小需在 1B–{MAX_UPLOAD // (1024*1024)}MB"},
                    )
                ctype = self.headers.get("Content-Type", "")
                body = self.rfile.read(length)
                with tempfile.TemporaryDirectory(prefix="sg-upload-") as td:
                    td_path = Path(td)
                    zip_path = td_path / "project.zip"
                    # multipart or raw zip
                    if "multipart/form-data" in ctype:
                        # crude multipart parse for field "file"
                        boundary = ctype.split("boundary=")[-1].strip()
                        parts = body.split(("--" + boundary).encode())
                        raw = None
                        for part in parts:
                            if b"filename=" not in part:
                                continue
                            idx = part.find(b"\r\n\r\n")
                            if idx < 0:
                                continue
                            raw = part[idx + 4 :]
                            if raw.endswith(b"\r\n"):
                                raw = raw[:-2]
                            break
                        if raw is None:
                            return _json(self, 400, {"error": "未找到上传文件字段 file"})
                        zip_path.write_bytes(raw)
                    else:
                        zip_path.write_bytes(body)

                    if not zipfile.is_zipfile(zip_path):
                        return _json(self, 400, {"error": "请上传 .zip 压缩包"})
                    extract_to = td_path / "src"
                    with zipfile.ZipFile(zip_path) as zf:
                        project = _safe_extract(zf, extract_to)
                    java_files = list(project.rglob("*.java"))
                    if not java_files:
                        return _json(
                            self,
                            400,
                            {"error": "压缩包内未找到 .java 文件，请上传 Spring/Java 工程"},
                        )
                    result = scan(project)
                    result["upload"] = {
                        "java_files": len(java_files),
                        "project_name": project.name,
                    }
                    return _json(self, 200, result)

            return _json(self, 404, {"error": "unknown api"})
        except Exception as e:
            return _json(self, 500, {"error": str(e), "trace": traceback.format_exc()})


def main():
    host = "0.0.0.0"
    port = 5193
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"SpringGuard 已启动，其他人可访问：")
    print(f"  本机  http://127.0.0.1:{port}/")
    print(f"  局域网 http://<你的IP>:{port}/")
    print(f"功能：扫描官方样例 / 上传 ZIP 扫描自己的 Spring 工程")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()

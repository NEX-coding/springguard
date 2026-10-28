#!/usr/bin/env bash
# 从 Markdown / HTML 导出比赛用 PDF（依赖本机 Google Chrome + pandoc）
set -euo pipefail
DOCS="$(cd "$(dirname "$0")" && pwd)"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
mkdir -p "$DOCS/_print"

pandoc "$DOCS/TECH_REPORT.md" -t html5 -o "$DOCS/_print/TECH_REPORT.html" --standalone --metadata title="SpringGuard 技术报告"
python3 - <<'PY'
from pathlib import Path
p = Path("/Users/royalchirs/code/比赛/ai+开源/springguard/docs/_print/TECH_REPORT.html")
html = p.read_text(encoding="utf-8")
css = """
<style>
@page { size: A4; margin: 16mm; }
body { font-family: "PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif; font-size: 10.5pt; line-height: 1.55; }
h1 { font-size: 18pt; } h2 { font-size: 13.5pt; border-bottom: 1px solid #ccc; padding-bottom: 3pt; }
h3 { font-size: 11.5pt; } table { border-collapse: collapse; width: 100%; font-size: 9.5pt; }
th, td { border: 1px solid #bbb; padding: 4pt 6pt; } th { background: #eef6f2; }
pre { background: #f4f6f8; padding: 8pt; font-size: 8.5pt; white-space: pre-wrap; }
blockquote { border-left: 3px solid #3d9a7a; padding-left: 10pt; background: #f7f7f7; }
</style>
"""
p.write_text(html.replace("</head>", css + "</head>"), encoding="utf-8")
PY

"$CHROME" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$DOCS/TECH_REPORT.pdf" \
  "file://$DOCS/_print/TECH_REPORT.html" 2>/dev/null

# 资源清单
pandoc "$DOCS/开源及第三方资源使用清单.md" -t html5 -o "$DOCS/_print/清单.html" --standalone
python3 - <<'PY'
from pathlib import Path
p = Path("/Users/royalchirs/code/比赛/ai+开源/springguard/docs/_print/清单.html")
css = '<style>@page{size:A4;margin:16mm}body{font-family:"PingFang SC",sans-serif;font-size:10.5pt}table{border-collapse:collapse;width:100%;font-size:9pt}th,td{border:1px solid #bbb;padding:4px}</style>'
html = p.read_text(encoding="utf-8").replace("</head>", css + "</head>")
p.write_text(html, encoding="utf-8")
PY
"$CHROME" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$DOCS/开源及第三方资源使用清单.pdf" \
  "file://$DOCS/_print/清单.html" 2>/dev/null

# PPT：优先用 PPT_print.html；若需像素级幻灯，可再跑 slides 截图流程
"$CHROME" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$DOCS/PPT.pdf" \
  "file://$DOCS/PPT_print.html" 2>/dev/null

ls -lh "$DOCS/TECH_REPORT.pdf" "$DOCS/PPT.pdf" "$DOCS/开源及第三方资源使用清单.pdf"

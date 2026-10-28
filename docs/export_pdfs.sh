#!/usr/bin/env bash
# 导出技术报告 / 资源清单 / 答辩 PPT 为提交用 PDF
set -euo pipefail
DOCS="$(cd "$(dirname "$0")" && pwd)"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
mkdir -p "$DOCS/_print"

export_md_pdf() {
  local md="$1" out_pdf="$2" title="$3"
  local html="$DOCS/_print/$(basename "$out_pdf" .pdf).html"
  pandoc "$md" -t html5 -o "$html" --standalone --metadata title="$title"
  python3 - "$html" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
html = p.read_text(encoding="utf-8")
css = """
<style>
@page { size: A4; margin: 16mm 15mm; }
body {
  font-family: "PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  font-size: 10.5pt; line-height: 1.55; color: #1a1a1a; max-width: 100%;
}
h1 { font-size: 18pt; margin: 0 0 10pt; }
h2 { font-size: 13.5pt; margin: 16pt 0 8pt; border-bottom: 1px solid #ccc; padding-bottom: 3pt; page-break-after: avoid; }
h3 { font-size: 11.5pt; margin: 12pt 0 6pt; page-break-after: avoid; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; margin: 8pt 0; }
th, td { border: 1px solid #bbb; padding: 4pt 6pt; vertical-align: top; }
th { background: #f3f5f7; }
pre { background: #f4f6f8; padding: 8pt; font-size: 8.5pt; white-space: pre-wrap; border: 1px solid #ddd; }
code { font-size: 9pt; }
blockquote { border-left: 3px solid #b91c1c; padding: 6pt 10pt; background: #fafafa; color: #333; }
a { color: #b91c1c; }
</style>
"""
if "</head>" in html:
    html = html.replace("</head>", css + "</head>", 1)
else:
    html = css + html
p.write_text(html, encoding="utf-8")
PY
  "$CHROME" --headless --disable-gpu --no-pdf-header-footer \
    --print-to-pdf="$out_pdf" "file://$html" 2>/dev/null
}

export_md_pdf "$DOCS/TECH_REPORT.md" "$DOCS/TECH_REPORT.pdf" "SpringGuard 技术报告"
export_md_pdf "$DOCS/开源及第三方资源使用清单.md" "$DOCS/开源及第三方资源使用清单.pdf" "开源及第三方资源使用清单"

# PPT：按页截图再合成，保证每页完整
python3 - <<'PY'
import re
from pathlib import Path
src = Path("/Users/royalchirs/code/比赛/ai+开源/springguard/docs/PPT_print.html").read_text(encoding="utf-8")
style = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
style = style.replace("width: 100vw;\n    height: 100vh;", "width: 1280px;\n    height: 720px;")
style += "\nhtml,body{margin:0;width:1280px;height:720px;overflow:hidden;}\n.slide{page-break-after:auto;min-height:720px;height:720px;width:1280px;}\n"
sections = re.findall(r'(<section class="slide[^"]*">.*?</section>)', src, re.S)
outdir = Path("/Users/royalchirs/code/比赛/ai+开源/springguard/docs/_print/slides")
outdir.mkdir(parents=True, exist_ok=True)
for i, sec in enumerate(sections, 1):
    doc = f"<!DOCTYPE html><html><head><meta charset=utf-8><style>{style}</style></head><body>{sec}</body></html>"
    (outdir / f"slide_{i:02d}.html").write_text(doc, encoding="utf-8")
print(f"slides {len(sections)}")
Path("/Users/royalchirs/code/比赛/ai+开源/springguard/docs/_print/slide_count.txt").write_text(str(len(sections)), encoding="utf-8")
PY

COUNT=$(cat "$DOCS/_print/slide_count.txt")
for i in $(seq -w 1 "$COUNT"); do
  "$CHROME" --headless --disable-gpu --window-size=1280,720 \
    --screenshot="$DOCS/_print/slides/slide_$i.png" \
    "file://$DOCS/_print/slides/slide_$i.html" 2>/dev/null
done

python3 - <<'PY'
from pathlib import Path
slides = sorted(Path("/Users/royalchirs/code/比赛/ai+开源/springguard/docs/_print/slides").glob("slide_*.png"))
imgs = "\n".join(f'<div class="p"><img src="{p.name}"/></div>' for p in slides)
html = f"""<!DOCTYPE html><html><head><meta charset=utf-8>
<style>
@page {{ size: 1280px 720px; margin: 0; }}
body {{ margin: 0; }}
.p {{ page-break-after: always; width: 1280px; height: 720px; }}
.p:last-child {{ page-break-after: auto; }}
img {{ width: 1280px; height: 720px; display: block; }}
</style></head><body>{imgs}</body></html>"""
Path("/Users/royalchirs/code/比赛/ai+开源/springguard/docs/_print/slides/deck.html").write_text(html, encoding="utf-8")
print("deck", len(slides))
PY

"$CHROME" --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$DOCS/PPT.pdf" \
  "file://$DOCS/_print/slides/deck.html" 2>/dev/null

ls -lh "$DOCS/TECH_REPORT.pdf" "$DOCS/开源及第三方资源使用清单.pdf" "$DOCS/PPT.pdf"

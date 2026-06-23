# Build a side-by-side HTML report from the three results_<engine>.json files.
# Usage: python compare_report.py   ->  report_compare.html

import json
import html

ENGINES = ["tesseract", "paddle", "easyocr"]
LABELS = {"tesseract": "Tesseract", "paddle": "PaddleOCR", "easyocr": "EasyOCR"}
VIDEO = "test_dangal_video.mp4"

data = {}
for e in ENGINES:
    with open(f"results_{e}.json", encoding="utf-8") as f:
        data[e] = json.load(f)

n = len(data[ENGINES[0]])
counts = {e: sum(1 for r in data[e] if r["status"] == "OK") for e in ENGINES}


def cell(rec):
    sub = html.escape(rec["subtitle"]) or "<span class='empty'>—</span>"
    cls = "ok" if rec["status"] == "OK" else "review"
    return f"<td class='{cls}'><div class='sub'>{sub}</div><div class='score'>{rec['score']:.2f}</div></td>"


rows = []
base = data[ENGINES[0]]
for i in range(n):
    seg = base[i]
    time = f"{seg['start']:.1f}s"
    audio = html.escape(seg["audio"]) or "—"
    cells = "".join(cell(data[e][i]) for e in ENGINES)
    rows.append(
        f"<tr><td class='time'>{time}</td><td class='audio'>{audio}</td>{cells}</tr>"
    )

summary = " &nbsp;·&nbsp; ".join(
    f"<b>{LABELS[e]}</b> {counts[e]} OK / {n - counts[e]} REVIEW" for e in ENGINES
)

head_cells = "".join(f"<th>{LABELS[e]}<br><small>(subtitle / score)</small></th>" for e in ENGINES)

doc = f"""<!doctype html>
<html lang="hi"><head><meta charset="utf-8">
<title>OCR comparison — {VIDEO}</title>
<style>
  body {{ font-family: 'Noto Sans Devanagari', 'Nirmala UI', system-ui, sans-serif;
         margin: 24px; color: #1a1a1a; }}
  h1 {{ font-size: 20px; margin: 0 0 4px; }}
  .meta {{ color: #555; margin-bottom: 16px; font-size: 14px; }}
  .summary {{ background: #f4f6f8; border: 1px solid #e0e4e8; border-radius: 8px;
             padding: 10px 14px; margin-bottom: 18px; font-size: 14px; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
  th, td {{ border: 1px solid #e2e2e2; padding: 8px 10px; vertical-align: top; text-align: left; }}
  th {{ background: #2b3a4a; color: #fff; font-weight: 600; }}
  td.time {{ color: #777; white-space: nowrap; font-variant-numeric: tabular-nums; }}
  td.audio {{ background: #fafafa; min-width: 220px; }}
  td.ok {{ background: #e7f6ec; }}
  td.review {{ background: #fff; }}
  .sub {{ }}
  .score {{ color: #888; font-size: 12px; margin-top: 3px; font-variant-numeric: tabular-nums; }}
  .empty {{ color: #bbb; }}
  tr:hover td {{ outline: 1px solid #cfd8e0; }}
</style></head>
<body>
  <h1>OCR engine comparison</h1>
  <div class="meta">Video: {VIDEO} &nbsp;·&nbsp; {n} segments &nbsp;·&nbsp; shared Whisper transcription, same pipeline, only the OCR engine differs.</div>
  <div class="summary">{summary}</div>
  <table>
    <thead><tr><th>Time</th><th>Audio (Whisper)</th>{head_cells}</tr></thead>
    <tbody>
      {"".join(rows)}
    </tbody>
  </table>
</body></html>"""

with open("report_compare.html", "w", encoding="utf-8") as f:
    f.write(doc)

print("wrote report_compare.html")
for e in ENGINES:
    print(f"  {LABELS[e]}: {counts[e]} OK / {n - counts[e]} REVIEW")

# Proof that the tool flags real mismatches.
# Takes segments that currently MATCH (audio == burned-in subtitle), then
# simulates a wrong subtitle and shows the score collapse + flag.
# Usage: python mismatch_demo.py  ->  mismatch_demo.html

import json
import re
import html
from rapidfuzz import fuzz

OK_THRESHOLD = 0.6


def normalize(text):
    text = re.sub(r'[^\w\s]', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def score(audio, sub):
    return fuzz.token_set_ratio(normalize(audio), normalize(sub)) / 100


with open("results_easyocr.json", encoding="utf-8") as f:
    results = json.load(f)

# real matching segments (the tool currently says OK)
matches = [r for r in results if r["status"] == "OK" and r["subtitle"].strip()][:4]

# simulate a wrong burned-in subtitle by using a DIFFERENT line in its place
rows = []
for i, r in enumerate(matches):
    wrong_sub = matches[(i + 1) % len(matches)]["subtitle"]
    real_score = r["score"]
    bad_score = score(r["audio"], wrong_sub)
    rows.append({
        "time": r["start"],
        "audio": r["audio"],
        "real_sub": r["subtitle"],
        "real_score": real_score,
        "wrong_sub": wrong_sub,
        "bad_score": bad_score,
        "real_status": "OK" if real_score >= OK_THRESHOLD else "FLAGGED",
        "bad_status": "OK" if bad_score >= OK_THRESHOLD else "FLAGGED",
    })

print(f"{'time':>8} | {'real score':>10} | {'wrong score':>11} | result")
print("-" * 60)
for r in rows:
    print(f"{r['time']:>7.1f}s | {r['real_score']:>10.2f} | {r['bad_score']:>11.2f} | "
          f"{r['real_status']} -> {r['bad_status']}")


def badge(status):
    cls = "ok" if status == "OK" else "flag"
    return f"<span class='badge {cls}'>{status}</span>"


body_rows = "".join(
    f"<tr><td class='time'>{r['time']:.1f}s</td>"
    f"<td class='audio'>{html.escape(r['audio'])}</td>"
    f"<td class='ok'>{html.escape(r['real_sub'])}<div class='s'>{r['real_score']:.2f} {badge(r['real_status'])}</div></td>"
    f"<td class='flag'>{html.escape(r['wrong_sub'])}<div class='s'>{r['bad_score']:.2f} {badge(r['bad_status'])}</div></td></tr>"
    for r in rows
)

doc = f"""<!doctype html>
<html lang="hi"><head><meta charset="utf-8">
<title>Mismatch detection — proof</title>
<style>
  body {{ font-family: 'Noto Sans Devanagari', 'Nirmala UI', system-ui, sans-serif; margin: 24px; color:#1a1a1a; }}
  h1 {{ font-size: 20px; margin-bottom: 4px; }}
  .meta {{ color:#555; font-size:14px; margin-bottom:16px; }}
  table {{ border-collapse: collapse; width:100%; font-size:14px; }}
  th,td {{ border:1px solid #e2e2e2; padding:8px 10px; vertical-align:top; }}
  th {{ background:#2b3a4a; color:#fff; }}
  td.time {{ color:#777; white-space:nowrap; }}
  td.audio {{ background:#fafafa; }}
  td.ok {{ background:#e7f6ec; }}
  td.flag {{ background:#ffe1e1; }}
  .s {{ font-size:12px; color:#555; margin-top:4px; }}
  .badge {{ padding:1px 7px; border-radius:4px; font-weight:600; font-size:11px; }}
  .badge.ok {{ background:#cdebd6; color:#1d6b38; }}
  .badge.flag {{ background:#f6c6c6; color:#a11; }}
</style></head>
<body>
  <h1>Mismatch detection — proof</h1>
  <div class="meta">Same audio. Left = the real burned-in subtitle (matches → OK). Right = a wrong subtitle swapped in → score collapses → <b>FLAGGED</b>. This is the tool catching a mismatch.</div>
  <table>
    <thead><tr><th>Time</th><th>Audio (Whisper)</th><th>Real subtitle</th><th>Wrong subtitle (simulated)</th></tr></thead>
    <tbody>{body_rows}</tbody>
  </table>
</body></html>"""

with open("mismatch_demo.html", "w", encoding="utf-8") as f:
    f.write(doc)
print("\nwrote mismatch_demo.html")

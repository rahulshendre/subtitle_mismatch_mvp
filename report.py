
import whisper
import cv2
import pytesseract
import re
from rapidfuzz import fuzz
import os

os.makedirs("frames", exist_ok=True)


def normalize(text):
    text = re.sub(r'[^\w\s]', '', text)
    return re.sub(r'\s+', ' ', text).strip()


video = cv2.VideoCapture("test_vid_kan_2.mp4")
fps = video.get(cv2.CAP_PROP_FPS)

print("Transcribing audio...")
model = whisper.load_model("medium")
result = model.transcribe("test_vid_kan_2.mp4", language="kn")
segments = [s for s in result["segments"] if (s["end"] - s["start"]) >= 0.7]
print(f"Found {len(segments)} segments\n")

results = []

for i, seg in enumerate(segments):
    start = seg["start"]
    end = seg["end"]
    audio_text = seg["text"].strip()
    midpoint = (start + end) / 2

    frame_number = int(midpoint * fps)
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    success, frame = video.read()

    if not success:
        continue

    height = frame.shape[0]
    subtitle_region = frame[int(height * 0.80):, :]
    img_path = f"frames/segment_{i+1}_{start:.1f}s.png"
    cv2.imwrite(img_path, subtitle_region)

    gray = cv2.cvtColor(subtitle_region, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    ocr_text = pytesseract.image_to_string(thresh, lang='kan').strip()
    score = fuzz.token_set_ratio(normalize(audio_text), normalize(ocr_text)) / 100
    status = "OK" if score >= 0.4 else "REVIEW"

    results.append({
        "start": start,
        "end": end,
        "audio": audio_text,
        "subtitle": ocr_text,
        "score": score,
        "status": status,
        "img": img_path
    })

video.release()

# Generate HTML report
ok_count = sum(1 for r in results if r["status"] == "OK")
review_count = sum(1 for r in results if r["status"] == "REVIEW")

rows = ""
for r in results:
    color = "#e6f4ea" if r["status"] == "OK" else "#fce8e6"
    badge = "#1a7f37" if r["status"] == "OK" else "#c0392b"
    rows += f"""
    <tr style="background:{color}">
        <td>{r['start']:.1f}s → {r['end']:.1f}s</td>
        <td>{r['audio']}</td>
        <td>{r['subtitle'] or '—'}</td>
        <td><img src="{r['img']}" style="height:40px;border-radius:4px;"></td>
        <td>{r['score']:.2f}</td>
        <td><span style="background:{badge};color:white;padding:2px 10px;border-radius:12px;font-size:12px">{r['status']}</span></td>
    </tr>"""

html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Subtitle Mismatch Report</title>
    <style>
        body {{ font-family: sans-serif; padding: 2rem; background: #f9f9f9; }}
        h1 {{ color: #222; }}
        .summary {{ display: flex; gap: 1rem; margin-bottom: 1.5rem; }}
        .card {{ background: white; border-radius: 8px; padding: 1rem 1.5rem; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }}
        .card h2 {{ margin: 0; font-size: 2rem; }}
        .card p {{ margin: 0; color: #666; font-size: 13px; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }}
        th {{ background: #333; color: white; padding: 10px 14px; text-align: left; font-size: 13px; }}
        td {{ padding: 10px 14px; font-size: 13px; border-bottom: 1px solid #eee; vertical-align: middle; }}
    </style>
</head>
<body>
    <h1>Subtitle Mismatch Report</h1>
    <div class="summary">
        <div class="card"><h2>{len(results)}</h2><p>Total segments</p></div>
        <div class="card"><h2 style="color:#1a7f37">{ok_count}</h2><p>OK</p></div>
        <div class="card"><h2 style="color:#c0392b">{review_count}</h2><p>Needs Review</p></div>
    </div>
    <table>
        <tr>
            <th>Timestamp</th>
            <th>Audio Text</th>
            <th>Subtitle OCR</th>
            <th>Frame</th>
            <th>Score</th>
            <th>Status</th>
        </tr>
        {rows}
    </table>
</body>
</html>"""

with open("report.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Report saved as report.html — {ok_count} OK, {review_count} REVIEW")
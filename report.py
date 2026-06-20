import whisper
import cv2
import re
import json
import os
from rapidfuzz import fuzz
from paddleocr import PaddleOCR

os.makedirs("frames", exist_ok=True)

ocr = PaddleOCR(use_angle_cls=True, lang='hi')


def normalize(text):
    # remove punctuation and whitespace before we compare

    text = re.sub(r'[^\w\s]', '', text)
    return re.sub(r'\s+', ' ', text).strip()


video = cv2.VideoCapture("test_vid.mp4")
fps = video.get(cv2.CAP_PROP_FPS)

# skip transcription if segments.json is already there, whisper takes almost 1 to 2 min on small model
if os.path.exists("segments.json"):
    with open("segments.json", "r", encoding="utf-8") as f:
        all_segments = json.load(f)
    print("Loaded segments from segments.json")
else:
    print("Transcribing audio...")
    model = whisper.load_model("small")
    result = model.transcribe("test_vid.mp4", language="hi", temperature=0)
    all_segments = result["segments"]
    with open("segments.json", "w", encoding="utf-8") as f:
        json.dump(all_segments, f, ensure_ascii=False, indent=2)

# for this pipeline, drop segments shorter than 1.5s, too short for a readable subtitle and whisper hallucinates on them
#however, this needs to be solved in the final project
segments = [s for s in all_segments if (s["end"] - s["start"]) >= 1.5]
print(f"Found {len(segments)} segments\n")

results = []

for i, seg in enumerate(segments):
    start = seg["start"]
    end = seg["end"]
    audio_text = seg["text"].strip()

    # midpoint gives the most stable subtitle frame, start and end frame might have transitions
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

    result = ocr.ocr(subtitle_region, cls=True)
    lines = result[0] if result and result[0] else []
    ocr_text = ' '.join(line[1][0] for line in lines).strip()

    # token_set_ratio handles word-order drift and also partial OCR matches better than simple ratio
    score = fuzz.token_set_ratio(normalize(audio_text), normalize(ocr_text)) / 100
    status = "OK" if score >= 0.6 else "REVIEW"

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

# generate HTML report
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
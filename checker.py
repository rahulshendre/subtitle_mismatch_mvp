import whisper
import cv2
import easyocr
import re
import json
import os
from rapidfuzz import fuzz

VIDEO = "test_dangal_video.mp4"
WHISPER_MODEL = "medium"
WHISPER_LANG = "hi"
MIN_SEGMENT_DURATION = 1.5
CONF_THRESH = 0.4

os.makedirs("frames", exist_ok=True)

reader = easyocr.Reader(['hi'], gpu=False, verbose=False)
video = cv2.VideoCapture(VIDEO)
fps = video.get(cv2.CAP_PROP_FPS)


def normalize(text):
    text = re.sub(r'[^\w\s]', '', text)
    return re.sub(r'\s+', ' ', text).strip()


if os.path.exists("segments.json"):
    with open("segments.json", "r", encoding="utf-8") as f:
        all_segments = json.load(f)
    print("Loaded segments from segments.json")
else:
    print(f"Transcribing with Whisper {WHISPER_MODEL}...")
    model = whisper.load_model(WHISPER_MODEL)
    result = model.transcribe(VIDEO, language=WHISPER_LANG, temperature=0)
    all_segments = result["segments"]
    with open("segments.json", "w", encoding="utf-8") as f:
        json.dump(all_segments, f, ensure_ascii=False, indent=2)

def dedup_hallucinations(segs, max_repeats=2):
    counts = {}
    out = []
    for s in segs:
        t = s["text"].strip()
        counts[t] = counts.get(t, 0) + 1
        if counts[t] <= max_repeats:
            out.append(s)
    return out

raw = [
    s for s in all_segments
    if (s["end"] - s["start"]) >= MIN_SEGMENT_DURATION
    and s.get("no_speech_prob", 0) < 0.6
]
segments = dedup_hallucinations(raw)
print(f"Found {len(segments)} segments\n")

results = []

for i, seg in enumerate(segments):
    start = seg["start"]
    end = seg["end"]
    audio_text = seg["text"].strip()

    # sample 3 frames across segment to avoid missing subtitle at edges
    sample_offsets = [0.25, 0.5, 0.75]
    sample_times = [start + (end - start) * o for o in sample_offsets]

    best_text = ""
    best_score = 0.0
    best_bbox = None
    best_frame = None

    audio_norm = normalize(audio_text)

    for t in sample_times:
        video.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps))
        ok, frame = video.read()
        if not ok:
            continue

        h, w = frame.shape[:2]

        for bbox, text, conf in reader.readtext(frame):
            if conf < CONF_THRESH:
                continue
            box_w = bbox[1][0] - bbox[0][0]
            if box_w < 0.2 * w:
                continue
            score = fuzz.token_set_ratio(audio_norm, normalize(text)) / 100
            if score > best_score:
                best_score = score
                best_text = text
                best_bbox = bbox
                best_frame = frame

    status = "OK" if best_score >= 0.6 else "REVIEW"

    if best_frame is not None:
        debug_frame = best_frame.copy()
        if best_bbox is not None:
            pts = [(int(p[0]), int(p[1])) for p in best_bbox]
            cv2.polylines(debug_frame, [__import__('numpy').array(pts)], True, (0, 255, 0), 2)
        cv2.imwrite(f"frames/segment_{i+1}_{start:.1f}s.png", debug_frame)

    results.append({
        "start": start,
        "end": end,
        "audio": audio_text,
        "subtitle": best_text,
        "score": best_score,
        "status": status
    })

    print(f"{start:.1f}s → {end:.1f}s")
    print(f"  Audio   : {audio_text}")
    print(f"  Subtitle: {best_text}")
    print(f"  Score   : {best_score:.2f} — {status}\n")

video.release()

with open("results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"Done. {len(results)} segments. Frames in /frames, results in results.json")

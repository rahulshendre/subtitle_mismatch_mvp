import whisper
import cv2
import pytesseract
import re
import json
import os
from rapidfuzz import fuzz

os.makedirs("frames", exist_ok=True)


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

    cv2.imwrite(f"frames/segment_{i+1}_{start:.1f}s.png", subtitle_region)

    # binarize before OCR, improves Devanagari accuracy on compressed video frames
    gray = cv2.cvtColor(subtitle_region, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    ocr_text = pytesseract.image_to_string(thresh, lang='hin').strip()

    # token_set_ratio handles word-order drift and also partial OCR matches better than simple ratio
    score = fuzz.token_set_ratio(normalize(audio_text), normalize(ocr_text)) / 100
    status = "OK" if score >= 0.6 else "REVIEW"

    results.append({
        "start": start,
        "end": end,
        "audio": audio_text,
        "subtitle": ocr_text,
        "score": score,
        "status": status
    })

    print(f"{start:.1f}s → {end:.1f}s")
    print(f"  Audio   : {audio_text}")
    print(f"  Subtitle: {ocr_text}")
    print(f"  Score   : {score:.2f} — {status}\n")

video.release()
print(f"Done. Frames saved in /frames folder.")
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


video = cv2.VideoCapture("test_vid.mp4")
fps = video.get(cv2.CAP_PROP_FPS)

print("Transcribing audio...")
model = whisper.load_model("small")
result = model.transcribe("test_vid.mp4", language="hi", temperature=0)
segments = [s for s in result["segments"] if (s["end"] - s["start"]) >= 1.5]
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

    cv2.imwrite(f"frames/segment_{i+1}_{start:.1f}s.png", subtitle_region)

    gray = cv2.cvtColor(subtitle_region, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    ocr_text = pytesseract.image_to_string(thresh, lang='hin').strip()

    score = fuzz.token_set_ratio(normalize(audio_text), normalize(ocr_text)) / 100
    status = "OK" if score >= 0.5 else "REVIEW"

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
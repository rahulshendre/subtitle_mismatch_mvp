import whisper
import cv2
import pytesseract
from rapidfuzz import fuzz
import os

os.makedirs("frames", exist_ok=True)

video = cv2.VideoCapture("test_vid.mp4")
fps = video.get(cv2.CAP_PROP_FPS)

print("Transcribing audio...")
model = whisper.load_model("small")
result = model.transcribe("test_vid.mp4", language="hi")
segments = result["segments"]
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

    ocr_text = pytesseract.image_to_string(subtitle_region, lang='hin').strip()

    score = fuzz.ratio(audio_text, ocr_text) / 100
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
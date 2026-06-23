import cv2
import pytesseract
import easyocr
from paddleocr import PaddleOCR
import os
import json
from datetime import datetime

VIDEO = "test_dangal_video.mp4"
SAMPLE_EVERY = 5  # seconds
Y_TOP = 0.72
Y_BOT = 0.80
CONF_THRESH = 0.5

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
OUT_DIR = f"ocr_runs/{RUN_ID}"
FRAMES_DIR = f"{OUT_DIR}/frames"
os.makedirs(FRAMES_DIR, exist_ok=True)

video = cv2.VideoCapture(VIDEO)
fps = video.get(cv2.CAP_PROP_FPS)
total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
duration = total_frames / fps

easy = easyocr.Reader(['hi'], gpu=False, verbose=False)
paddle = PaddleOCR(lang='hi', use_textline_orientation=False)

header = f"{'Time':>8} | {'Tesseract':<40} | {'PaddleOCR':<40} | {'EasyOCR':<40}"
divider = "-" * 140
print(header)
print(divider)

log_lines = [header, divider]
log_records = []

t = 0
while t < duration:
    frame_no = int(t * fps)
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
    ok, frame = video.read()
    if not ok:
        t += SAMPLE_EVERY
        continue

    h, w = frame.shape[:2]
    crop = frame[int(h * Y_TOP):int(h * Y_BOT), :]

    cv2.imwrite(f"{FRAMES_DIR}/{t:.0f}s.png", crop)

    # Tesseract
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    tess = pytesseract.image_to_string(thresh, lang='hin').strip().replace('\n', ' ')

    # PaddleOCR
    paddle_result = paddle.predict(crop)
    paddle_text = ""
    if paddle_result:
        res = paddle_result[0]
        texts = res.get('rec_texts', [])
        scores = res.get('rec_scores', [])
        polys = res.get('rec_polys', [])
        words = []
        for txt, sc, poly in zip(texts, scores, polys):
            if sc >= CONF_THRESH:
                x = poly[0][0]
                words.append((x, txt))
        words.sort(key=lambda x: x[0])
        paddle_text = " ".join(w for _, w in words)

    # EasyOCR
    easy_result = easy.readtext(crop)
    easy_words = [
        (bbox[0][0], text)
        for bbox, text, conf in easy_result
        if conf >= CONF_THRESH
    ]
    easy_words.sort(key=lambda x: x[0])
    easy_text = " ".join(t2 for _, t2 in easy_words)

    line = f"{t:>7.1f}s | {tess[:40]:<40} | {paddle_text[:40]:<40} | {easy_text[:40]:<40}"
    print(line)
    log_lines.append(line)
    log_records.append({
        "time": t,
        "tesseract": tess,
        "paddleocr": paddle_text,
        "easyocr": easy_text,
    })

    t += SAMPLE_EVERY

video.release()

with open(f"{OUT_DIR}/log.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(log_lines))

with open(f"{OUT_DIR}/log.json", "w", encoding="utf-8") as f:
    json.dump(log_records, f, ensure_ascii=False, indent=2)

print(f"\nSaved to {OUT_DIR}/")

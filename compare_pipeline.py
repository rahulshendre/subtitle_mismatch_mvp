# Compare OCR engines on the same pipeline. All read the shared Whisper
# segments (segments.json) so only the OCR step changes.
# Usage: python compare_pipeline.py --engine easyocr|tesseract|paddle

import argparse
import cv2
import re
import json
import os
from rapidfuzz import fuzz

VIDEO = "test_dangal_video.mp4"
WHISPER_MODEL = "medium"
WHISPER_LANG = "hi"
MIN_SEGMENT_DURATION = 1.5
NO_SPEECH_MAX = 0.6
MIN_BOX_WIDTH_FRAC = 0.2   # detection must span >=20% of frame width
OK_THRESHOLD = 0.6
SAMPLE_OFFSETS = [0.25, 0.5, 0.75]


def normalize(text):
    text = re.sub(r'[^\w\s]', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def dedup_hallucinations(segs, max_repeats=2):
    counts = {}
    out = []
    for s in segs:
        t = s["text"].strip()
        counts[t] = counts.get(t, 0) + 1
        if counts[t] <= max_repeats:
            out.append(s)
    return out


def load_segments():
    if os.path.exists("segments.json"):
        with open("segments.json", "r", encoding="utf-8") as f:
            all_segments = json.load(f)
        print("Loaded shared Whisper segments from segments.json")
    else:
        import whisper
        print(f"No cache — transcribing once with Whisper {WHISPER_MODEL}...")
        model = whisper.load_model(WHISPER_MODEL)
        result = model.transcribe(VIDEO, language=WHISPER_LANG, temperature=0)
        all_segments = result["segments"]
        with open("segments.json", "w", encoding="utf-8") as f:
            json.dump(all_segments, f, ensure_ascii=False, indent=2)
    raw = [
        s for s in all_segments
        if (s["end"] - s["start"]) >= MIN_SEGMENT_DURATION
        and s.get("no_speech_prob", 0) < NO_SPEECH_MAX
    ]
    return dedup_hallucinations(raw)


# --- engine adapters: each returns a list of (text, width_fraction) per frame ---

def make_detector(engine):
    if engine == "easyocr":
        import easyocr
        reader = easyocr.Reader(['hi'], gpu=False, verbose=False)

        def detect(frame):
            h, w = frame.shape[:2]
            out = []
            for bbox, text, conf in reader.readtext(frame):
                width = bbox[1][0] - bbox[0][0]
                out.append((text, width / w))
            return out
        return detect

    if engine == "paddle":
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(lang='hi', use_textline_orientation=False)

        def detect(frame):
            h, w = frame.shape[:2]
            out = []
            result = ocr.predict(frame)
            if result:
                res = result[0]
                texts = res.get('rec_texts', [])
                polys = res.get('rec_polys', [])
                for txt, poly in zip(texts, polys):
                    xs = [p[0] for p in poly]
                    width = max(xs) - min(xs)
                    out.append((txt, width / w))
            return out
        return detect

    if engine == "tesseract":
        import pytesseract
        from pytesseract import Output

        def detect(frame):
            h, w = frame.shape[:2]
            data = pytesseract.image_to_data(frame, lang='hin', output_type=Output.DICT)
            lines = {}
            for i in range(len(data['text'])):
                txt = data['text'][i].strip()
                if not txt:
                    continue
                key = (data['block_num'][i], data['par_num'][i], data['line_num'][i])
                left = data['left'][i]
                right = left + data['width'][i]
                lines.setdefault(key, []).append((left, right, txt))
            out = []
            for words in lines.values():
                text = ' '.join(t for _, _, t in words)
                x0 = min(l for l, _, _ in words)
                x1 = max(r for _, r, _ in words)
                out.append((text, (x1 - x0) / w))
            return out
        return detect

    raise ValueError(f"unknown engine: {engine}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", required=True, choices=["easyocr", "paddle", "tesseract"])
    args = ap.parse_args()
    engine = args.engine

    segments = load_segments()
    print(f"[{engine}] {len(segments)} segments\n")

    detect = make_detector(engine)
    video = cv2.VideoCapture(VIDEO)
    fps = video.get(cv2.CAP_PROP_FPS)

    results = []
    for seg in segments:
        start, end = seg["start"], seg["end"]
        audio_text = seg["text"].strip()
        audio_norm = normalize(audio_text)

        best_text, best_score = "", 0.0
        for o in SAMPLE_OFFSETS:
            t = start + (end - start) * o
            video.set(cv2.CAP_PROP_POS_FRAMES, int(t * fps))
            ok, frame = video.read()
            if not ok:
                continue
            for text, width_frac in detect(frame):
                if width_frac < MIN_BOX_WIDTH_FRAC:
                    continue
                score = fuzz.token_set_ratio(audio_norm, normalize(text)) / 100
                if score > best_score:
                    best_score, best_text = score, text

        status = "OK" if best_score >= OK_THRESHOLD else "REVIEW"
        results.append({
            "start": start, "end": end,
            "audio": audio_text, "subtitle": best_text,
            "score": best_score, "status": status,
        })
        print(f"{start:.1f}s  {best_score:.2f}  {status}  | {best_text[:50]}")

    video.release()

    out_path = f"results_{engine}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    ok = sum(1 for r in results if r["status"] == "OK")
    print(f"\n[{engine}] done. {ok} OK / {len(results) - ok} REVIEW → {out_path}")


if __name__ == "__main__":
    main()

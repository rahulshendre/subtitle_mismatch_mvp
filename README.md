# Burn-in Subtitle Checker

Detects mismatches between spoken audio and burned-in subtitles in video files.

Built as a prototype for [PlanetRead](https://planetread.org) C4GT DMP 2026.

## Video used

[![Video used](https://img.youtube.com/vi/PmM5Fy3RLkc/hqdefault.jpg)](https://www.youtube.com/watch?v=PmM5Fy3RLkc)

[![YouTube — source clip](https://img.shields.io/badge/YouTube-Play-FF0000?style=flat-square&logo=youtube&logoColor=white)](https://www.youtube.com/watch?v=PmM5Fy3RLkc)

## Demo video

[![Demo video](https://img.youtube.com/vi/G06-LdzV9PU/hqdefault.jpg)](https://youtu.be/G06-LdzV9PU)

[![YouTube — demo](https://img.shields.io/badge/YouTube-Play-FF0000?style=flat-square&logo=youtube&logoColor=white)](https://youtu.be/G06-LdzV9PU)

## Pipeline

1. Transcribes audio with Whisper (`small` model, Hindi, `temperature=0`)
2. Filters segments shorter than 1.5s (too short for a readable subtitle; Whisper hallucinates on these)
3. Seeks to midpoint of each segment (avoids subtitle transition frames) and crops bottom 20% of frame
4. Reads subtitle text with PaddleOCR (Hindi) — replaced Tesseract for better accuracy on compressed video frames
5. Compares audio text vs OCR text using RapidFuzz `token_set_ratio` (handles word-order drift and partial matches)
6. Flags segments below 0.6 similarity as `REVIEW`; above as `OK`

## Language support

Check other languages by switching branches.

- Hindi: best supported right now.
- Kannada: supported, but ASR is noisy and mismatch scores are less stable.
- Marathi: supported, but early segments misread and OCR alignment is drifting 

Work in progress...


## Screenshots

### Subtitle region crop

![Subtitle Crop](assets/subtitle_crop.png)

### Terminal output

![Terminal Output](assets/terminal_output.png)

### HTML report

![HTML Report](assets/report.png)

## Setup

Requires **Python 3.9+**. No system-level OCR engine needed — PaddleOCR bundles its own models.

### Python dependencies

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
pip install openai-whisper opencv-python paddlepaddle paddleocr rapidfuzz
```

**Windows:** `python -m venv venv`, then `venv\Scripts\activate`, then the same `pip install` line above.

> **Note:** First run will download PaddleOCR Hindi model weights (~100 MB). Subsequent runs use the cache.

## Usage

```bash
python3 transcribe.py   # transcribe audio
python3 ocr_frame.py    # test OCR on one frame
python3 checker.py      # run full pipeline
python3 report.py       # generate HTML report
```

On Windows use `python` instead of `python3` if that is how Python is installed.

## Author

Rahul Shendre — [GitHub](https://github.com/rahulshendre) · [LinkedIn](https://www.linkedin.com/in/rahul-shendre/)

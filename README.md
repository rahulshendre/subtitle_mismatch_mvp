# Burn-in Subtitle Checker

Automatic checker for mismatches between spoken audio and burned-in subtitles in video files.

Built as a prototype for [PlanetRead](https://planetread.org) C4GT DMP 2026.

## Overview

The pipeline does four things:

1. Transcribes audio with Whisper.
2. Extracts subtitle frames with OpenCV.
3. Reads subtitle text with Tesseract OCR (Hindi and Kannada).
4. Compares speech vs subtitle text with RapidFuzz and flags low-score segments.

## Requirements

- Python 3.9+
- Tesseract OCR with language data (`hin`, `kan`)

## Setup

Install Tesseract:

```bash
# macOS
brew install tesseract tesseract-lang


Install Python dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install openai-whisper opencv-python pytesseract rapidfuzz
```

## Usage

```bash
# 1) transcribe audio
python3 transcribe.py

# 2) Validate OCR on one frame
python3 ocr_frame.py

# 3) Run mismatch checker
python3 checker.py

# 4) Generate HTML report
python3 report.py
```

## Output

The HTML report highlights segments that need manual review, including:

- Timestamp range
- Whisper text
- OCR subtitle text
- Similarity score
- Review status

## Project Files

- `transcribe.py` - Whisper transcription with timestamps
- `ocr_frame.py` - OCR on selected subtitle frame
- `checker.py` - Main comparison pipeline
- `report.py` - HTML report generator

## Notes

- OCR quality depends on subtitle clarity and frame quality.
- Segment timestamps from ASR and subtitle display timing may not align perfectly.

## Author

Rahul Shendre - [GitHub](https://github.com/rahulshendre) - [LinkedIn](https://www.linkedin.com/in/rahul-shendre/)

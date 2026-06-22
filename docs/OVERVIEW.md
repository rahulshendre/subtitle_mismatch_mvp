# Project Overview — Audio-Subtitle Mismatch Checker

A plain-language map of what this project is, what's been built, and what every branch contains.

> For active scope, meetings, and open questions, see [`PROJECT_LOG.md`](./PROJECT_LOG.md).
> For the long-term (parked) vision, see [`PROJECT_VISION.md`](./PROJECT_VISION.md).

---

## What this is

A **tool** (not a trained model) that checks whether the **burned-in subtitles** in a video match the **spoken audio**, and flags the parts that don't.

Built for PlanetRead (C4GT DMP 2026). Their content is Same-Language Subtitling — subtitles in the same language as the audio, for reading literacy. This tool is the quality-check for that.

It orchestrates **pre-trained** models + rules. Nothing is trained from scratch.

---

## How it works (the core idea)

```
video
  ↓  Whisper          → transcribe audio into timed segments
  ↓  OpenCV           → grab video frames at each segment's time
  ↓  OCR              → read the subtitle text burned into those frames
  ↓  fuzzy compare    → how close is the read subtitle to the spoken words?
  ↓  threshold        → close enough = OK, else = REVIEW (possible mismatch)
```

The OCR engine and matching strategy are what changed across branches as we learned what works.

---

## Timeline — two phases

**Phase 1 — MVP (30 Apr → 7 May, pre-DMP)**
First working prototype: Whisper + **Tesseract** OCR on a cropped subtitle band + RapidFuzz compare, with an HTML report. Worked well for videos that have a clean solid subtitle bar. Also spun off Kannada and Marathi language branches.

**Phase 2 — Smart pipeline (20 → 22 Jun, DMP)**
Real test footage (Dangal TV) has subtitles overlaid on the scene, **no clean bar** — Tesseract failed there. So we compared OCR engines and rebuilt the pipeline. This is the current line of work (`smart-pipeline` branch).

---

## Branch map

| Branch | What it is | ASR + OCR | Status |
|---|---|---|---|
| **`main`** | Baseline MVP, Hindi | Whisper + **Tesseract** (cropped band) | Stable prototype |
| **`smart-pipeline`** ⭐ | Current work — full rewrite for scene-overlaid subs | Whisper **medium** + **EasyOCR** full-frame + fuzzy match | **Active / best** |
| `by-easyocr` | Experiment: swap Tesseract → EasyOCR for busy backgrounds | Whisper + EasyOCR | Done — findings folded into smart-pipeline |
| `by-paddleocr` | Experiment: swap Tesseract → PaddleOCR v2 | Whisper + PaddleOCR v2 | Done — lost to EasyOCR for this footage |
| `feat/kannada` | Kannada language support | Whisper medium + Tesseract | Older spin-off, secondary |
| `feat/marathi` | Marathi language support | Whisper + Tesseract | Older spin-off, secondary |
| `ocr-compare` | Same point as `main` (staging for OCR comparison) | — | Inactive |

**OCR finding:** Tesseract wins on a clean solid subtitle bar; **EasyOCR** wins on busy/scene-overlaid text; PaddleOCR was weaker on this footage. (Details in memory + `by-easyocr` report.)

---

## Current state (`smart-pipeline`)

Pipeline: Whisper medium → filter segments (min duration, drop low-speech, dedup Whisper hallucination loops) → sample 3 frames per segment → EasyOCR on the full frame → fuzzy-match each text block against the audio → best match scored, `OK` if ≥ 0.6 else `REVIEW`.

On the Dangal test video: **7 OK / 26 REVIEW** across 33 segments.

**Known gaps:**
- Channel logo, ad bug, and a red disclaimer ticker leak into the subtitle field for no-dialogue stretches (false text). → next task: filter persistent non-subtitle text.
- "Empty" can mean two things the tool can't yet tell apart: *no subtitle there* vs *subtitle present but OCR missed it*.
- No real mismatch has been *proven* caught yet (the test video is mostly correct). Need a known-bad sample or a synthetic one.
- EasyOCR confidence is unreliable for Devanagari — the fuzzy score is the real signal, not OCR confidence.

---

## What's next

1. **Separate disclaimer/logo/chrome from real subtitles** (persistent-text filter) — the immediate goal from the mentor meeting.
2. Distinguish *absent* vs *missed* subtitle (a presence signal).
3. Prove one real mismatch gets flagged.
4. Evaluate Sarvam (ASR) and PaddleOCR as possible upgrades.

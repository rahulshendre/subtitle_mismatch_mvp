# EasyOCR Test — Dangal TV Video

**Video:** `test_dangal_video.mp4`  
**Duration:** 697s (~11.6 min) | **FPS:** ~30 | **Resolution:** 1610×912  
**Engine:** EasyOCR 1.7.2 | `lang='hi'` | CPU | `verbose=False`  
**Sampling:** Every 10s → 70 frames total

---

## Method

- Run EasyOCR on full frame
- Filter detections to **y = 68–83% of frame height** (subtitle zone)
- Keep only detections with **confidence > 0.4**
- Sort left-to-right, join as string

---

## Results Summary

| Metric | Value |
|---|---|
| Frames sampled | 70 |
| Frames with subtitle detected | 6 (8.6%) |
| Frames empty | 64 (91.4%) |
| Avg confidence (subtitle frames) | 0.61 |

> High empty rate is expected — subtitles appear intermittently, not every 10s.

---

## Detections

| Timestamp | Conf | Text | Notes |
|---|---|---|---|
| 0:01:10 | 0.46 | सचिन पाचाल नवीन अय्यर | Cast credits — false positive |
| 0:01:40 | 0.83 | 00 | Junk — likely timecode/logo artifact |
| 0:04:10 | 0.41 | प्ति चहाचारी | Show title "पति ब्रह्मचारी" — false positive |
| 0:07:40 | 0.59 | इसके खिलाफ केस की तैयारी की है\| | ✅ Correct subtitle |
| 0:07:50 | 0.81 | ओ सूरज! | ✅ Correct subtitle |
| 0:08:20 | 0.55 | वो मान जाऐंगी\| | ✅ Correct subtitle |

---

## Observations

**What works:**
- Full subtitle lines read correctly on busy scene backgrounds
- No missed words on confirmed subtitle frames (unlike PaddleOCR which dropped last 3 words)
- Confidence scores reliable — all true positives above 0.55

**Issues:**
- **False positives** from cast credits (0:01:10) and show title watermark (0:04:10) — both fall in the 68–83% y-zone
- `।` (Devanagari danda) read as `|` (pipe) — minor punctuation error
- "00" at 0:01:40 — numeric artifact slipping through conf > 0.4 filter

**Fixes to consider:**
- Raise confidence threshold to **0.5+** to cut junk like "00"
- Exclude frames where detected text is numeric-only or < 3 chars
- Narrow y-zone to **72–80%** to avoid catching upper watermarks/credits

---

## vs Tesseract & PaddleOCR

| Engine | Black bar subtitles | Scene-overlaid subtitles |
|---|---|---|
| Tesseract + binarize | ✅ Best | ❌ Fails |
| PaddleOCR v3 | ❌ Garbage | ⚠️ Partial (drops words) |
| **EasyOCR** | Not tested | ✅ Best |

# Demo — Whisper (ASR) vs EasyOCR on `test_dangal_video.mp4`

10 examples from the Dangal TV test video. The strongest proof both engines work:
**Whisper (from audio) and EasyOCR (from the burned-in subtitle) are two independent
reads — where they agree, both are right.**

Frames are in this folder (`demo/`).

---

## Part A — Both engines work (7 OK matches)

Whisper transcribes the audio, EasyOCR reads the on-screen subtitle, fuzzy-match scores how close. High score = two independent reads landed on the same Hindi.

| # | Time | Whisper (heard the audio) | EasyOCR (read the subtitle) | Score | Frame |
|---|---|---|---|---|---|
| 1 | 674s | कुछ दिन भी लग सकते हैं, कुछ महिने या फिर कुछ साल भी लग सकते हैं | कुछ दिन भी लगा सकते हैं | **1.00** | `ok_674s_score100.png` |
| 2 | 564s | माँ, मैं आपको गले से लगाना चाथी हूँ | माँ, मैं आपको गले से लगाना चाहती हूँ | **0.92** | `ok_564s_score92.png` |
| 3 | 695s | इश्याजी आपको मेरी बात सुदेगा | ईशा जी, आपको मेरी बात | **0.78** | `ok_695s_score78.png` |
| 4 | 570s | माँ, आपने सिने से लगा दीजियो | हमें अपने सीने से लगा लीजिएग | **0.78** | `ok_570s_score78.png` |
| 5 | 656s | दॉक्टर, यह हूँ है माँ कोख? | डॉक्टर, क्या हुआ है माँ को? | **0.73** | `ok_656s_score73.png` |
| 6 | 671s | कोमा के प्राजाए | कौमा के स्टेट में कुछ पतानईों | **0.62** | `ok_671s_score62.png` |
| 7 | 556s | यही लोरी काखर सुनाथी थी | तो आप मुझे यही लोरी गाकर | **0.62** | `ok_556s_score62.png` |

**Read this honestly:**
- Rows 1–2: near-perfect. Both engines nail it.
- Rows 3–5: both readable and clearly the same line; small word slips on each side (Whisper `चाथी`/`दॉक्टर`, OCR cuts a tail off).
- Rows 6–7: Whisper struggles (background music, the `प्राजाए` artifact), OCR still readable — fuzzy match still links them.

This is why we use **fuzzy matching, not exact match**: both ASR and OCR are imperfect, so we measure *closeness*, not equality.

---

## Part B — The limits (3 honest cases)

| Time | What's happening | Whisper | EasyOCR | Frame |
|---|---|---|---|---|
| 31s | Intro — **no dialogue subtitle**. Red disclaimer ticker + logo + ad on screen | background speech | grabbed the **ticker** (false text) | `gap_chrome_ticker_31s.png` |
| 638s | Hug scene — subtitle `माँ।` **is on screen**, tiny | `मा मा मा...` | **empty (missed it)** | `gap_ocr_missed_638s.png` |
| 602s | Close-up — **genuinely no subtitle** | `तीश्या` (one word) | empty (**correct**) | `gap_absent_602s.png` |

**The takeaway for the mentor:**
- Whisper is solid-but-imperfect on this Hindi TV audio (motivates trying **Sarvam**).
- EasyOCR reads scene-overlaid subtitles well when they're clear; misses tiny text.
- Two open problems → the next tasks: (1) filter chrome (logo/ticker/ad) out of the subtitle field, (2) tell "no subtitle" apart from "OCR missed it".

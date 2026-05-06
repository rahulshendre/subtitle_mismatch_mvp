# Report Analysis - What the REVIEW Segments Tell Us

This is an analysis of the two segments flagged as REVIEW in the Hindi run.
Not every REVIEW means a real subtitle error. Here's what actually happened.

---

## Segment 1 - 0.0s → 4.0s

| | Text |
|---|---|
| Audio (Whisper) | श्कूल का पहला दिन |
| Subtitle (OCR) | - (empty) |
| Score | 0.00 → REVIEW |

**What happened:** This is an intro frame. No burned-in subtitle exists here - it's just a title card. OCR returned nothing, so the score hit zero and the tool flagged it.

**Is this a real error?** No. The subtitle is genuinely absent at this timestamp.

**What this reveals:** The tool can't tell the difference between "subtitle exists but OCR failed to read it" and "no subtitle was ever there." Both look the same to the pipeline - empty OCR output.

---

## Segment 9 - 32.0s → 35.0s

| | Text |
|---|---|
| Audio (Whisper) | मांने मेरा हाथ और कस्किप पकलिया |
| Subtitle (OCR) | और कस के पकड़ लिया। |
| Score | 0.57 → REVIEW |

**What happened:** Whisper transcribed the full sentence. OCR only picked up the second half. Both are saying the same thing - "mom grabbed my hand tightly."

**Why did OCR miss the first half?** The frame was sampled at the midpoint of the 3-second segment. By that point, the subtitle had already advanced to the next line, so only the tail end of the sentence was visible in the frame.

**Is this a real error?** No. It's a timing alignment problem - single-frame sampling at midpoint doesn't always land on the right subtitle line.

## What a real mismatch looks like

A genuine subtitle error would show:
- OCR returns clear readable text
- Whisper returns clear audio text  
- Both are present but semantically different
- Score below threshold

Example: Audio says "वो कहाँ गई थी" but subtitle shows "वो कहाँ गया था" - same sentence, wrong gender. Score ~0.6, flagged correctly. That's the tool working as intended.

---

## Summary

Both REVIEW flags in this run are false positives. The content matched - the pipeline just couldn't confirm it due to:

1. **Missing subtitle at segment start** - tool has no way to detect intentionally blank frames.
2. **Midpoint frame sampling** - one frame per segment isn't enough when subtitles change mid-segment.


Currently these are known limitations, not bugs. A futue fix which could be implemented in future could be, sample multiple frames per segment and take the best OCR match, this should address both issues.

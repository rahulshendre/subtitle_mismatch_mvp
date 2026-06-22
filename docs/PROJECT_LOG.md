# Project Log — Audio-Subtitle Mismatch Flagging Tool

Living log: meetings, decisions, and open questions. Append newest entries at the top of each section.

---

## Links

- **Scope (source of truth):** [GitHub issue #3 — Lightweight Audio-Subtitle Mismatch Flagging Tool](https://github.com/PlanetRead/Burn-in-subtitle-checker/issues/3)
- **Drive (vid / demo / docs):** https://drive.google.com/drive/folders/137EKcINUYBXzhlHxDqyXCY3tT7rdRb6i
- **Future / north-star spec:** [`PROJECT_VISION.md`](./PROJECT_VISION.md) — broader burned-in *presence* detection. Parked; not the current build target.

---

## Scope (current)

Build a **lightweight** tool that flags **mismatches between spoken audio and burned-in subtitles**. Hindi first.

**It is a TOOL, not a model.** Pipeline orchestrating pre-trained ASR + OCR + rules. No model training. No training dataset — only a small *test* set to measure accuracy.

**Target video type (proposed, confirm with mentor):** PlanetRead-style Indian TV — single-line Hindi subtitle at the bottom, same-language, dialogue-synced (e.g. the Dangal test clip).

Out of current scope: generic "does this video have burned-in subs" presence detection (vision doc); subtitle-style parameters; other sub types — anime, karaoke, memes, lyrics videos, vertical reels, multi-track, mixed-language.

---

## Doc tiering

1. GitHub issue #3 = what we build (scope truth).
2. This file (`PROJECT_LOG.md`) = meetings, decisions, open questions.
3. `PROJECT_VISION.md` = long-term/future, parked.

---

## Questions for Mentor (next meeting)

Keep it short — only what needs his answer.

1. **Which videos exactly?** Confirm target = PlanetRead-style Indian TV with same-language Hindi subtitles. Any other type in scope right now?
2. **Sample videos?** Any to test on — bonus if some have *known* subtitle mistakes?
3. **Output** — single pass/fail per video, or a timestamped list of where subtitle ≠ audio?

---

## Open Questions

| # | Question | Status | Notes |
|---|---|---|---|
| Q1 | Is the disclaimer / logo / ad added at the last (broadcast) stage, separate from subtitles? | Answered | Yes — overlays (logo, ticker, disclaimer, ad bug) are composited at broadcast/playout; subtitles are baked into the program earlier. BUT in the delivered mp4 everything is flattened to pixels — no layers to peel. Separate them instead by **persistence** (recurs across many frames at a fixed spot = chrome) **+ audio correlation** (matches spoken words = real subtitle). Do not hardcode "disclaimer = intro only." |
| Q2 | Output format — binary flag, or rich per-segment report (audio / subtitle / score / status)? | Open | Current code emits per-segment JSON (start, end, audio, subtitle, score, status). |
| Q3 | How to distinguish "subtitle absent" vs "subtitle present but OCR missed it"? | Open | Both currently show as empty/REVIEW. Needs a presence signal. See failure case at 638s ("माँ।" present, OCR missed). |
| Q4 | Switch ASR Whisper → Sarvam? OCR EasyOCR → PaddleOCR? | Open / experiment | Mentor asked to try. A/B against current; keep winner. Prior data: EasyOCR > PaddleOCR for this scene-overlay style. |
| Q5 | What threshold / metric defines a real "mismatch" vs OCR/ASR noise? | Open | Currently fuzzy token_set_ratio, OK ≥ 0.6. No mismatch catch proven yet. |

---

## Decisions

- **2026-06-22** — Doc tiering set (above). Vision doc demoted to future. Build to issue #3.
- **2026-06-22** — Lowered `CONF_THRESH` 0.4 → 0.1 (EasyOCR Devanagari confidence unreliable; fuzzy match is the real discriminator).
- **2026-06-17** — Build a new, better pipeline on top of the existing one; explore better tech beyond the original doc's stack.

---

## Meeting Log

### 2026-06-17 — 1st meeting

- Brief discussion on the project and implementation approach (not limited to the tech stack in the doc).
- Recommendation: build a new, better pipeline on the existing one; try **Sarvam** (ASR), **PaddleOCR**; find better tech overall.
- Focus heavily on **Hindi** first.
- ~6 subtitle parameters (shadow, font, weight, …) — not a concern for now.
- **Immediate goal: separate disclaimer from subtitles.**
- Open doubt raised → Q1 (answered above).

---

## Parked (not now)

- ~6 subtitle-style parameters (shadow, font, weight, …).
- Generic burned-in subtitle *presence* detection across all video types (vision doc).
- Multi-language beyond Hindi (Kannada / Marathi branches exist but secondary).

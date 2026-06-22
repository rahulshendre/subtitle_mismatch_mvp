# Burnt-In Subtitle Detection Project

## Engineering Notes, Questions, Risks and Roadmap

---

# Objective

Build an open-source system capable of reliably detecting whether subtitles are permanently embedded (burned-in) into a video.

The long-term goal is not simply binary classification, but creating a reusable foundation for video text understanding.

---

# Success Criteria

Input:

```python
video.mp4
```

Output:

```json
{
  "has_burned_in_subtitles": true,
  "confidence": 0.94,
  "segments": [
    {
      "start": 34.2,
      "end": 36.8,
      "text": "Welcome home."
    }
  ]
}
```

---

# Important Observation

This is not merely an image classification problem.

Subtitles are temporal objects.

Detection depends on:

* Text persistence
* Position consistency
* Duration
* OCR quality
* Linguistic continuity

The system should therefore be designed as a hybrid pipeline rather than a single neural network.

---

# Primary Questions To Clarify

## Definition

What exactly counts as a subtitle?

Need clear answers for:

* Movie subtitles
* YouTube captions
* TikTok captions
* Karaoke subtitles
* Anime subtitles
* ASS subtitles
* Multiple subtitle tracks
* Bilingual subtitles
* Lyrics videos
* Meme captions
* Presentation recordings
* End credits

---

## Output

Should the model provide:

### Binary classification?

```json
{
    "burned_in": true
}
```

or

### Rich metadata?

```json
{
    "burned_in": true,
    "confidence": 0.93,
    "segments": [...],
    "language": "English"
}
```

---

## Granularity

Should classification happen:

* Per frame?
* Per segment?
* Per video?

---

## Explainability

Should the system explain why a decision was made?

Example:

```json
{
    "reason": [
        "persistent text region",
        "consistent OCR",
        "subtitle duration 2.5 seconds"
    ]
}
```

---

# Expected Difficult Cases

## News tickers

False positive risk.

---

## Watermarks

Channel logos.

Netflix logos.

---

## Sports scoreboards

Must not be classified as subtitles.

---

## Interview lower thirds

Persistent name labels.

---

## Karaoke videos

Text changes colour.

---

## Lyrics videos

Entire video may contain text.

---

## Meme videos

Top and bottom captions.

---

## End credits

Large amount of text.

---

## Vertical reels

Subtitle position may vary.

---

## Low-quality videos

240p

Compression artifacts.

Motion blur.

---

## Multiple languages

Hindi

English

Tamil

Telugu

Bengali

Urdu

Arabic

---

# Recommended Architecture

```text
Video
↓
Frame sampler
↓
Text detector
↓
OCR
↓
Subtitle tracker
↓
Temporal analysis
↓
Region analysis
↓
Rule engine
↓
Confidence scorer
↓
JSON output
```

---

# Major Components

## Video Processing

Tools:

* FFmpeg
* OpenCV
* PyAV

Responsibilities:

* Decode video
* Frame extraction
* Frame sampling

---

## OCR

Candidates:

* PaddleOCR
* Surya OCR
* EasyOCR
* Tesseract

Evaluation needed.

---

## Tracking

Need to track:

* Text persistence
* Bounding boxes
* Start time
* End time

Output:

```json
{
    "start": 12.4,
    "end": 14.9,
    "bbox": [...]
}
```

---

## Decision Layer

Use:

* Temporal consistency
* Position consistency
* OCR confidence
* Linguistic continuity

Avoid relying solely on a neural network.

---

# Dataset Strategy

Need:

## Positive examples

500+

Movie subtitles

YouTube captions

Anime

Short-form videos

---

## Negative examples

500+

News

Sports

Presentations

Screen recordings

Interview overlays

---

## Ambiguous examples

200+

Memes

Lyrics videos

Karaoke

Complex overlays

---

# Metadata To Store

```json
{
    "language": "",
    "resolution": "",
    "fps": "",
    "aspect_ratio": "",
    "subtitle_style": "",
    "burned_in": true
}
```

---

# Evaluation Metrics

Precision

Recall

F1

Latency

False positive rate

False negative rate

---

# More Important Than Accuracy

False positive analysis.

Every failure should be categorized.

Example:

```text
False Positive:
News ticker

False Positive:
Sports scoreboard

False Negative:
Yellow anime subtitles

False Positive:
Interview overlay
```

Build a failure database.

This database may eventually become more valuable than the training set itself.

---

# Computational Constraints

Need to support:

* 10 second videos
* 3 hour videos
* 24 FPS
* 60 FPS
* 240p
* 4K

Cannot process every frame.

Need adaptive frame sampling.

---

# Week 1 Priority

Do not train models.

Instead:

* Define scope.
* Define subtitle taxonomy.
* Define edge cases.
* Define success criteria.
* Create dataset format.

---

# Suggested Roadmap

## Phase 1

Dataset and problem understanding.

Weeks 1–3.

---

## Phase 2

Baseline pipeline.

Weeks 4–6.

Goal:

Reach approximately 70–80% performance without heavy ML.

---

## Phase 3

Hard negative handling.

Weeks 7–9.

Focus:

False positives.

---

## Phase 4

Performance and robustness.

Weeks 10–12.

Focus:

Latency

Memory

Generalization

---

# Long-Term Extensions

Possible future capabilities:

## Subtitle extraction

Video → SRT

---

## Subtitle quality audit

Duration

Placement

---

## Language identification

---

## Translation

---

## Searchable video archives

---

## Accessibility tooling

---

## Video indexing

---

## Content moderation

---

# Important Principle

Do not optimize for benchmark numbers.

Optimize for reliability.

A model with 94% accuracy and understandable failure modes is more valuable than a 99% accuracy system that behaves unpredictably.

---

# Main Project Risk

The hardest problem is not model training.

The hardest problem is defining what counts as a subtitle and handling edge cases.

Most project time should therefore be spent on:

* Failure analysis
* Dataset quality
* Evaluation
* Robustness

rather than architecture experimentation.

---

# Desired Outcome

By the end of the project, the repository should provide:

```python
result = analyze(video)

print(result)
```

and produce reliable, explainable subtitle detection on diverse real-world videos.

The repository should serve as the foundation for future work in video text understanding rather than being limited to binary subtitle detection.

import whisper
import json

model = whisper.load_model("small")
result = model.transcribe("test_vid.mp4", language="hi", temperature=0)

for segment in result["segments"]:
    print(f"{segment['start']:.2f}s -> {segment['end']:.2f}s : {segment['text']}")

with open("segments.json", "w", encoding="utf-8") as f:
    json.dump(result["segments"], f, ensure_ascii=False, indent=2)
print("Segments saved to segments.json")
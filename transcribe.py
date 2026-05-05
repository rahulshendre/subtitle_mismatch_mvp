import whisper

model = whisper.load_model("small")
result = model.transcribe("test_vid_marathi.mp4", language="mr")


for segment in result["segments"]:
    print(f"{segment['start']:.2f}s -> {segment['end']:.2f}s : {segment['text']}")
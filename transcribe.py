import whisper

model = whisper.load_model("small")
result = model.transcribe("test_vid.mp4", language = "hi")


for segment in result["segments"]:
    print(f"{segment['start']:.2f}s -> {segment['end']:.2f}s : {segment['text']}")
import whisper

model = whisper.load_model("medium")
result = model.transcribe("test_vid_kan_2.mp4", language="kn")


for segment in result["segments"]:
    print(f"{segment['start']:.2f}s -> {segment['end']:.2f}s : {segment['text']}")
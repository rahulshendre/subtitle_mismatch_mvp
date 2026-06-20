import cv2
import easyocr

video = cv2.VideoCapture("test_vid.mp4")
fps = video.get(cv2.CAP_PROP_FPS)
print(f"video FPS : {fps}")

timestamp = 8.0
frame_number = int(timestamp * fps)
video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

success, frame = video.read()
if success:
    height, width = frame.shape[:2]
    print(f"Frame size: {width}x{height}")

    cv2.imwrite("subtitle_crop.png", frame)
    print("saved subtitle_crop.png")

    reader = easyocr.Reader(['hi'], gpu=False, verbose=False)
    result = reader.readtext("subtitle_crop.png")

    # filter to subtitle zone (68-83% height), confidence > 0.4, sort left to right
    subtitle_words = [
        (bbox, text) for (bbox, text, conf) in result
        if 0.68 <= (bbox[0][1] + bbox[2][1]) / 2 / height <= 0.83 and conf > 0.4
    ]
    subtitle_words.sort(key=lambda x: x[0][0][0])
    text = " ".join(t for _, t in subtitle_words)

    print(f"OCR result: '{text}'")
else:
    print("failed to read frame")

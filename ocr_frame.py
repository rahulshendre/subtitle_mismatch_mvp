import cv2
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='hi')

video = cv2.VideoCapture("test_vid.mp4")
fps = video.get(cv2.CAP_PROP_FPS)
print(f"video FPS : {fps}")

# midpoint of first segment is best position to check
timestamp = 8.0
frame_number = int(timestamp * fps)
video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

success, frame = video.read()
if success:
    height, width = frame.shape[:2]
    print(f"Frame size: {width}x{height}")

    subtitle_region = frame[int(height * 0.80):, :]
    cv2.imwrite("subtitle_crop.png", subtitle_region)
    print("saved subtitle_crop.png")

    result = ocr.ocr(subtitle_region, cls=True)
    lines = result[0] if result and result[0] else []
    text = ' '.join(line[1][0] for line in lines).strip()
    print(f"OCR result: '{text}'")
else:
    print("failed to read frame")

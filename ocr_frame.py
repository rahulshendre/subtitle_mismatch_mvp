import cv2 
import pytesseract

video = cv2.VideoCapture("test_vid_marathi.mp4")
fps = video.get(cv2.CAP_PROP_FPS)
print(f"video FPS : {fps}")

#taking midpoint for the first one, as middle is the best position to check
timestamp = 8.0
frame_number = int(timestamp * fps)
video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

success, frame = video.read()
if success:
    height, width = frame.shape[:2]
    print(f"Frame size: {width}x{height}")

    #crop the bottom
    subtitle_region = frame[int(height * 0.80):, :]

    cv2.imwrite("subtitle_crop.png", subtitle_region)
    print("saved subtitle_crop.png - open this to see what we cropped")

    ##marathi OCR
    text = pytesseract.image_to_string(subtitle_region, lang='mar')
    print(f"OCR result: '{text.strip()}'")

else:
    print("failed to read frame")
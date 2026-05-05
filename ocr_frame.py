import cv2 
import pytesseract

video = cv2.VideoCapture("test_vid_kan_2.mp4")
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

    gray = cv2.cvtColor(subtitle_region, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(thresh, lang='kan')
    print(f"OCR result: '{text.strip()}'")

else:
    print("failed to read frame")
# ...existing code...
import argparse
import cv2
import sys
import os

def main():
    parser = argparse.ArgumentParser(description="Detect faces in an image")
    parser.add_argument("-i", "--image", help="Path to input image", default="mona.jpg")
    parser.add_argument("-c", "--cascade", help="Path to Haar cascade XML", default="haarcascade_frontalface_default.xml")
    args = parser.parse_args()

    if not os.path.isfile(args.image):
        print(f"Error: image file '{args.image}' not found")
        sys.exit(1)
    if not os.path.isfile(args.cascade):
        print(f"Error: cascade file '{args.cascade}' not found")
        sys.exit(1)

    img = cv2.imread(args.image)
    if img is None:
        print(f"Error: cannot read image '{args.image}'")
        sys.exit(1)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)   # 將圖片轉成灰階

    face_cascade = cv2.CascadeClassifier(args.cascade)   # 載入人臉模型
    if face_cascade.empty():
        print(f"Error: failed to load cascade '{args.cascade}'")
        sys.exit(1)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30,30))    # 偵測人臉

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)    # 利用 for 迴圈，抓取每個人臉屬性，繪製方框

    cv2.imshow('oxxostudio', img)
    cv2.waitKey(0) # 按下任意鍵停止
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
# ...existing code...
import cv2
img = cv2.imread('mona.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)   # 將圖片轉成灰階

face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")   # 載入人臉模型
faces = face_cascade.detectMultiScale(gray)    # 偵測人臉

for (x, y, w, h) in faces:
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)    # 利用 for 迴圈，抓取每個人臉屬性，繪製方框

cv2.imshow('oxxostudio', img)
cv2.waitKey(0) # 按下任意鍵停止
cv2.destroyAllWindows()
import cv2
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
#faces = face_cascade.detectMultiScale(gray)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    ret, frame = cap.read()
    if not ret:
        print("Cannot receive frame")
        break
    frame = cv2.resize(frame,(540,320))              # 縮小尺寸，避免尺寸過大導致效能不好
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)   # 將鏡頭影像轉換成灰階
    faces = face_cascade.detectMultiScale(gray)      # 偵測人臉
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)   # 標記人臉
    cv2.imshow('oxxostudio', frame)
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
import cv2
import os
import numpy as np
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

# Firebase initialization
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceattendance-8eecd-default-rtdb.firebaseio.com/"
})

# Initialize face detection and QR
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
qr_detector = cv2.QRCodeDetector()
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Train face model
def train_model(regno):
    images, labels = [], []
    for i in range(1, 51):
        img_path = f"faces/{regno}_{i}.jpg"
        if os.path.exists(img_path):
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            images.append(img)
            labels.append(i)
    if images:
        recognizer.train(images, np.array(labels))
        return True
    return False

# Update attendance in Firebase
def mark_attendance_in_firebase(regno):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    ref = db.reference(f"/Attendance/{date_str}/{regno}")
    ref.set({
        "status": "Present",
        "time": time_str
    })
    print(f"[FIREBASE] Attendance marked for {regno} at {time_str}")

# Open webcam
cap = cv2.VideoCapture(0)
cv2.namedWindow("Attendance System", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Attendance System", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

print("[INFO] Scanning started...")

regno_found = None
model_trained = False
marked = False
msg = ""
msg_timer = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    height, width, _ = frame.shape
    mid = width // 2

    # Divide screen
    left_frame = frame[:, :mid]
    right_frame = frame[:, mid:]

    # QR detection
    if not regno_found or marked:
        qr_data, bbox, _ = qr_detector.detectAndDecode(right_frame)
        if qr_data:
            regno_found = qr_data.strip()
            model_trained = train_model(regno_found)
            marked = False
            msg = f"[INFO] QR regno: {regno_found}"
            msg_timer = 50

    # Face matching
    if regno_found and model_trained and not marked:
        gray_left = cv2.cvtColor(left_frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_left, 1.3, 5)
        for (x, y, w, h) in faces:
            face_roi = gray_left[y:y+h, x:x+w]
            label, confidence = recognizer.predict(face_roi)
            print(f"[DEBUG] Confidence: {confidence}")
            if confidence < 70:
                msg = f"✅ Matched & Attendance marked for {regno_found}"
                marked = True
                msg_timer = 100

                # Firebase attendance mark
                mark_attendance_in_firebase(regno_found)

                # Log locally too
                with open("matched.txt", "a") as file:
                    file.write(f"{regno_found} - Marked at {datetime.now().strftime('%H:%M:%S')}\n")

            else:
                msg = f"❌ Face didn't match for {regno_found}. Try again."
                regno_found = None
                model_trained = False
                msg_timer = 100
            break

    # Draw layout
    cv2.line(frame, (mid, 0), (mid, height), (0, 255, 0), 2)
    cv2.putText(frame, "Live Face Scan", (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)
    cv2.putText(frame, "QR Code Scan", (mid + 30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 255), 2)

    # Show message
    if msg_timer > 0 and msg:
        font = cv2.FONT_HERSHEY_SIMPLEX
        max_width = width - 100
        words = msg.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + " " + word if current_line else word
            (text_width, _), _ = cv2.getTextSize(test_line, font, 0.9, 2)
            if text_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        start_y = max(height - len(lines) * 35 - 20, 30)
        for i, line in enumerate(lines):
            y = start_y + i * 35
            cv2.putText(frame, line, (50, y), font, 0.9, (0, 255, 255), 2)

        msg_timer -= 1

    # Display
    cv2.imshow("Attendance System", frame)

    key = cv2.waitKey(1)
    if key == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()

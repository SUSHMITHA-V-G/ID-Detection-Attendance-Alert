import cv2
import os
import qrcode

# Load Haarcascade for face detection
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Take input
name = input("Enter your name: ")
regno = input("Enter your registration number: ")

# Create faces folder if it doesn't exist
if not os.path.exists("faces"):
    os.makedirs("faces")

# Start camera
cap = cv2.VideoCapture(0)
count = 0

print("[INFO] Capturing 50 face images...")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Draw rectangle and save face region
    for (x, y, w, h) in faces:
        count += 1
        face_img = frame[y:y+h, x:x+w]
        face_path = f"faces/{regno}_{count}.jpg"
        cv2.imwrite(face_path, face_img)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(frame, f"Image {count}/50", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show camera
    cv2.imshow("Face Capture", frame)

    if cv2.waitKey(1) & 0xFF == 27 or count >= 50:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()

print(f"[INFO] {count} face images saved for {name} (RegNo: {regno})")

# Generate QR code with only regno
qr = qrcode.QRCode(version=1, box_size=10, border=5)
qr.add_data(regno)
qr.make(fit=True)
img = qr.make_image(fill="black", back_color="white")

# Save QR code
if not os.path.exists("qr_images"):
    os.makedirs("qr_images")

qr_path = f"qr_images/{regno}_qr.png"
img.save(qr_path)

print(f"[INFO] QR code saved as {qr_path}")

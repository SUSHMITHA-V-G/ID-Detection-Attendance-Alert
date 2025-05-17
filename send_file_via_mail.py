import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os

# ===== Fill these =====
sender_email = "sensusmitha944@gmail.com"
sender_password = "kkgf mmpo qkvz pqgj"  # Paste app password here (no spaces!)
receiver_email = "2212102@nec.edu.in"  # Person who should receive the file
file_to_send = "matched.txt"  # File that contains attendance list

def send_email():
    if not os.path.exists(file_to_send):
        print(f"[ERROR] File '{file_to_send}' not found!")
        return

    # Set up the email
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = "Today's Attendance File"

    # Attach body text
    body = "Hi, please find the attached attendance file."
    msg.attach(MIMEText(body, "plain"))

    # Attach the file
    with open(file_to_send, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {file_to_send}",
        )
        msg.attach(part)

    # Send the email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("[SUCCESS] Email sent successfully!")
    except Exception as e:
        print("[ERROR] Failed to send email:", e)

# Run it
send_email()





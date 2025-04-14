import smtplib
import uuid
import time
import imaplib
import email
import RPi.GPIO as GPIO
import board
import busio
import digitalio
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import picamera


import sys
import subprocess
from board import SCL, SDA
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import sys
sys.path.append('/home/pi/Adafruit-Raspberry-Pi-Python-Code-legacy/Adafruit_CircuitPython_MCP230xx-main')  # LIBRARY
from adafruit_mcp230xx.mcp23017 import MCP23017

#-----------OLED Font---------------#
RESET_PIN = digitalio.DigitalInOut(board.D4)
i2c = board.I2C()
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C, reset=RESET_PIN)


# Email Credentials
IMAP_SERVER = 'imap.gmail.com'
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
GMAIL_USERNAME = '126156165@sastra.ac.in'
GMAIL_PASSWORD = 'oobn otcb bujl klnm'



class Emailer:
    def sendmail(self, recipient, subject, file_path):
        global sent_message_id
       
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USERNAME
        msg['To'] = recipient
        msg['Subject'] = subject
       
        # Set the Message-ID explicitly to a unique value
        sent_message_id = str(uuid.uuid4())  # Generate a unique Message-ID
        msg['Message-ID'] = sent_message_id
       
        body = "See attached image"
        msg.attach(MIMEText(body, 'plain'))

        with open(file_path, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename={file_path}")
            msg.attach(part)

        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        session.starttls()
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD)

        # Send the email and store the message ID
        response = session.sendmail(GMAIL_USERNAME, recipient, msg.as_string())
        print(f"Email sent successfully with attachment. Message ID: {sent_message_id}")
       
        session.quit()



def capture_image():
    camera = picamera.PiCamera()
    camera.resolution = (1024, 768)
    camera.brightness = 60
    camera.start_preview()
    time.sleep(5)
    image_path = '/home/pi/Desktop/detected_image.jpg'
    camera.capture(image_path)
    camera.stop_preview()
    print("Image captured successfully.")
    return image_path

def check_email():
    global sent_message_id
   
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        mail.select('inbox')
       
        # Search for unread emails
        result, data = mail.search(None, '(UNSEEN)')
       
        if data[0]:
            latest_email_id = data[0].split()[-1]  # Get the latest unread email
            result, msg_data = mail.fetch(latest_email_id, '(RFC822)')
           
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = msg['subject']
                    sender = msg['from']
                    in_reply_to = msg.get('In-Reply-To', '')
                    references = msg.get('References', '')

                    print(f"New email received from {sender} with subject: {subject}")
                    print(f"In-Reply-To: {in_reply_to}")
                    print(f"References: {references}")

                    # Check if the email's subject is "Re: Object Detected"
                    if subject.lower() == "re: object detected":
                        print("This email is a reply to our previous email.")
                       
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode()
                                    print(f"Email body: {body}")
                                    return body.strip()
                        else:
                            body = msg.get_payload(decode=True).decode()
                            print(f"Email body: {body}")
                            return body.strip()
                    else:
                        print("This email is NOT a reply to our previous email (subject mismatch).")
       
        mail.logout()
    except Exception as e:
        print(f"Error checking email: {e}")

def opendoor():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)  # Use BCM mode for consistency
    GPIO.setup(16, GPIO.OUT)  # Relay 1 (BCM pin 16)
    GPIO.setup(20, GPIO.OUT)  # Relay 2 (BCM pin 20)
    GPIO.setup(21, GPIO.OUT)  # Relay 3 (BCM pin 21)

    try:
        while True:
            GPIO.output(16, 1)
            print("Relay1 ON")
            time.sleep(2)
            GPIO.output(20, 1)
            print("Relay2 ON")
            time.sleep(2)
            GPIO.output(21, 1)
            print("Relay3 ON")
            time.sleep(2)

            GPIO.output(16, 0)
            print("Relay1 OFF")
            time.sleep(2)
            GPIO.output(20, 0)
            print("Relay2 OFF")
            time.sleep(2)
            GPIO.output(21, 0)
            print("Relay3 OFF")
            time.sleep(2)

    except KeyboardInterrupt:
        print("Exiting relay control.")
    finally:
        GPIO.cleanup()  # Properly reset GPIO pins


def IR():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(26, GPIO.IN)  # Ensure pin is set as input

    val7 = GPIO.input(26)
    if val7 == 0:
        print("Object Detected")
        PortB[3].value = True  # Turn buzzer ON
        time.sleep(3)
        PortB[3].value = False  # Turn buzzer OFF

        # Capture image and send via email
        image_path = capture_image()
        sender = Emailer()
        sendTo = '126156165@sastra.ac.in'
        emailSubject = "Object Detected"
        sender.sendmail(sendTo, emailSubject, image_path)

        print("Waiting for reply email...")
        time.sleep(30)
        email_content = check_email()

        if email_content and "ok" in email_content.lower().split():
            print("Reply contains the word 'ok'. Activating sensor check.")
            opendoor()
        else:
            print("No relevant reply received. Retrying in 60 seconds...")
            time.sleep(60)
            check_email()




# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.IN)  # Sensor pin

# Initialize MCP23017 for output (buzzer)
i2c = busio.I2C(board.SCL, board.SDA)
mcp = MCP23017(i2c)
PortB = [mcp.get_pin(pin) for pin in range(8, 16)]
PortB[3].direction = digitalio.Direction.OUTPUT

try:
    while True:
        IR()  # Continuously monitor IR sensor
        time.sleep(1)  # Avoid busy loop

except KeyboardInterrupt:
    print("Program terminated by user.")
    GPIO.cleanup()

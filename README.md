# **Smart Object Detection / Smart Door Lock System**

This project turns your Raspberry Pi into a simple security or automation system. 
When a potential intruder is detected using a PIR sensor, the system captures an image and sends it to your specified email. 
If you reply with "ok", the system activates a set of relays — which could be used to open a door, turn something on, or trigger any action you want it to do.


## What this project does

- Detects intruder using an PIR (passive infrared->warm beings) sensor
- Captures an image using the inbuilt camera
- Sends the image to a specified email address
- Waits for an email reply
- If the reply contains "ok", it activates relays to perform an action (like opening a door or keeping it shut)

---

## Hardware Required

- Raspberry Pi
- Pi Camera
- IR sensor
- Relay module (3-channel used)
- Buzzer or trigger
- MCP23017 I/O Expander
- OLED display (can be built in)
- Wires and breadboard

---

## How it works!

1. The PIR sensor constantly checks for movement with a specified time interval.
2. When an object is detected:
   - The buzzer turns on briefly.
   - A photo of the intruder is taken using the camera.
   - The photo is sent via email to the user's email address.
3. The system then waits for a reply email.
4. If a reply comes back with the word "ok", the relays are turned on in sequence.
5. If there's no valid reply, the system waits and checks again later.

---

## Setup Instructions

1. **Install dependencies**:
   - `picamera`
   - `RPi.GPIO`
   - `adafruit-circuitpython-ssd1306`
   - `adafruit-circuitpython-mcp230xx`
   - `Pillow`
   - Email libraries (pre-installed in Python)

2. **Enable camera and I2C** on your Raspberry Pi via `raspi-config`.

3. **Replace your Gmail credentials** in my code. You’ll need to enable app passwords for you gmail account if you have 2-factor authentication enabled.

4. **Wire up your sensors and relays** according to the GPIO pin setup used in the code or switch it up.

5. Run the script using:
   ```bash
   python3 your_script_name.py
   ```

---

## Stuff to keep in mind

- The system checks for unread emails and only responds to replies with the subject "Re: Object Detected".
- The message ID is used to avoid irrelevant emails and clutter.

---

## Potential usecases

- Home or lab door unlock system with admin approval
- Smart-delivery lockers
- Gate control to secure areas


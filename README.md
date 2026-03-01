# 🤟 CommBridge: Real-Time Geometric Sign Language Translator

**CommBridge** is a zero-latency, privacy-first Sign Language to Speech translation engine. Built during the **NAH-X Assistive Technology Hackathon at JIS University**, it aims to bridge the communication gap using standard, low-cost webcams.

Unlike traditional heavy machine learning models, this project uses a **Custom Geometric Heuristics Engine** written purely in Python to instantly translate signs without needing the cloud.

---

## 🚀 The Core Innovation
Current real-time translation solutions often require expensive hardware or high-latency cloud computing. 

I solved this by building a custom logic engine on top of **Google MediaPipe**. Instead of relying on slow, black-box AI models, this system uses rapid mathematical calculations (trigonometry, joint coordinate tracking, and distance thresholds) to identify hand shapes instantly, ensuring real-time text-to-speech output locally on the machine.

## ✨ Key Technical Features
* **Zero-Latency Tracking:** Processes 14 distinct hand gestures in real-time.
* **Custom Geometric Logic:** Uses exact finger joint coordinates, angles, and distances to classify signs.
* **SOS Emergency Override:** Detects frantic hand-shaking (high variance in wrist X-coordinates) to trigger an immediate, high-volume audio alarm.
* **Intelligent Debouncing:** Features a 15-frame memory buffer to ignore half-formed signs and prevent UI flickering.
* **Flask-CORS Bridge:** Operates as an independent local API, allowing any frontend to connect and receive live video and translation text.

---

## 🛠️ Tech Stack
* **Computer Vision:** Google MediaPipe Hands, OpenCV
* **Backend API & Logic:** Python, Flask, Flask-CORS
* **Frontend Demo:** Pure HTML, CSS (Glassmorphism), Vanilla JavaScript
* **Audio:** Web Speech API (TTS)

---

## 🧠 How The Logic Engine Works
The core "brain" of CommBridge uses MediaPipe to extract 21 3D landmarks from the user's hand. 

My Python backend runs a math-based rules engine on these points:
1. **Finger State Detection:** Compares the Y-coordinate of a fingertip (e.g., landmark 8) to its base knuckle (landmark 6). If it is physically higher, the finger is classified as "Open" (1). Otherwise, it is "Closed" (0).
2. **Distance Calculations (Trigonometry):** For the "OK" sign, the system calculates the Euclidean distance between the thumb tip and the index tip. 
3. **Motion History Tracking:** For the "SOS" shake, the backend stores the wrist's X-coordinates in a continuous array, popping old frames to maintain a 0.5-second history. If the max variance exceeds `0.08`, the emergency event is triggered.

---

## ⚙️ Installation & Setup (Local Server)

To run the AI engine and the demo UI on your own machine:

### 1. Set up the Environment
Open a terminal in the project folder:
```bash
# Create a Python virtual environment
python -m venv .venv

# Activate the environment (Windows)
.\.venv\Scripts\activate
# Activate the environment (Mac/Linux)
source .venv/bin/activate
from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import time
import math
from collections import Counter # NEW: Imported for the smoothing buffer

app = Flask(__name__)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.6, min_tracking_confidence=0.6)
mp_draw = mp.solutions.drawing_utils

current_sign = "Waiting for sign..."
last_spoken_time = 0
wrist_x_history = []
gesture_buffer = [] # NEW: Memory array to prevent flickering

def get_distance(p1, p2):
    return math.hypot(p1.x - p2.x, p1.y - p2.y)

def generate_frames():
    global current_sign, last_spoken_time, wrist_x_history, gesture_buffer
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not camera.isOpened():
        camera = cv2.VideoCapture(0)
        
    while True:
        success, frame = camera.read()
        if not success: break
            
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        detected_word = "Waiting for sign..."

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # --- TWO HANDS LOGIC ---
            if len(results.multi_hand_landmarks) == 2:
                h1 = results.multi_hand_landmarks[0]
                h2 = results.multi_hand_landmarks[1]
                
                dist1 = get_distance(h1.landmark[8], h2.landmark[9])
                dist2 = get_distance(h2.landmark[8], h1.landmark[9])
                
                if dist1 < 0.15:
                    if h1.landmark[8].y < h1.landmark[5].y: detected_word = "Toilet"
                    else: detected_word = "Washroom"
                elif dist2 < 0.15:
                    if h2.landmark[8].y < h2.landmark[5].y: detected_word = "Toilet"
                    else: detected_word = "Washroom"

            # --- SINGLE HAND LOGIC ---
            else:
                hand_landmarks = results.multi_hand_landmarks[0]
                
                wrist_x = hand_landmarks.landmark[0].x
                wrist_x_history.append(wrist_x)
                if len(wrist_x_history) > 25: wrist_x_history.pop(0)
                is_shaking = (len(wrist_x_history) >= 15 and (max(wrist_x_history) - min(wrist_x_history)) > 0.08)

                finger_tips = [8, 12, 16, 20] 
                fingers_up = []
                for tip_id in finger_tips:
                    if hand_landmarks.landmark[tip_id].y < hand_landmarks.landmark[tip_id - 2].y:
                        fingers_up.append(1)
                    else:
                        fingers_up.append(0)

                thumb_tip = hand_landmarks.landmark[4]
                thumb_base = hand_landmarks.landmark[2]
                index_tip = hand_landmarks.landmark[8]
                pinky_mcp = hand_landmarks.landmark[17]
                
                thumb_is_up = thumb_tip.y < (thumb_base.y - 0.03)
                thumb_is_down = thumb_tip.y > (thumb_base.y + 0.03)
                thumb_is_open = abs(thumb_tip.x - pinky_mcp.x) > 0.15 

                if get_distance(thumb_tip, index_tip) < 0.05 and fingers_up[1:] == [1, 1, 1]: detected_word = "OK"
                elif fingers_up == [1, 0, 0, 0] and thumb_is_open: detected_word = "Light ON"
                elif fingers_up == [1, 0, 0, 0] and not thumb_is_open: detected_word = "Help"
                elif fingers_up == [1, 1, 0, 0]: detected_word = "Water"
                elif fingers_up == [1, 1, 1, 0]: detected_word = "Food"
                elif fingers_up == [1, 1, 1, 1] and not thumb_is_open: detected_word = "Thank You"
                elif fingers_up == [1, 1, 1, 1] and thumb_is_open:
                    if is_shaking: detected_word = "Emergency"
                    else:
                        middle_tip = hand_landmarks.landmark[12]
                        wrist = hand_landmarks.landmark[0]
                        if abs(middle_tip.x - wrist.x) > 0.15: 
                            if middle_tip.x > wrist.x: detected_word = "Fan ON"
                            else: detected_word = "Fan OFF"
                        else: detected_word = "Hello"
                elif fingers_up == [0, 0, 0, 1]: detected_word = "Call"
                elif fingers_up == [0, 0, 0, 0]:
                    if thumb_is_up: detected_word = "Yes"
                    elif thumb_is_down: detected_word = "No"
                    else: detected_word = "Stop"

        # --- THE LATENCY / SMOOTHING FIX ---
        
        # 1. Add the current frame's guess to our memory buffer
        gesture_buffer.append(detected_word)
        
        # 2. Keep only the last 15 frames (about half a second of video)
        if len(gesture_buffer) > 15:
            gesture_buffer.pop(0)
            
        # 3. Find the most common sign that occurred in that half second
        most_common_sign = Counter(gesture_buffer).most_common(1)[0][0]

        # 4. INCREASED COOLDOWN: Now waits 3.5 seconds before it is allowed to speak again
        if most_common_sign != "Waiting for sign..." and (time.time() - last_spoken_time > 3.5): 
            current_sign = most_common_sign
            last_spoken_time = time.time()
            
            # Clear the buffer after a successful read so it doesn't double-trigger
            gesture_buffer.clear()

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index(): return render_template('index.html')

@app.route('/video_feed')
def video_feed(): return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_sign')
def get_sign(): return jsonify({"sign": current_sign})

if __name__ == '__main__': app.run(debug=True, port=5000)
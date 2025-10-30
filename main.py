from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import base64
import cv2
import numpy as np
import mediapipe as mp
import random
import math

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Page principale ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# --- Fonction Shifumi ---
def play_shifumi(player_choice):
    options = ["Pierre", "Feuille", "Ciseaux"]
    computer_choice = random.choice(options)

    if player_choice == computer_choice:
        result = "Égalité"
    elif (player_choice == "Pierre" and computer_choice == "Ciseaux") or \
         (player_choice == "Feuille" and computer_choice == "Pierre") or \
         (player_choice == "Ciseaux" and computer_choice == "Feuille"):
        result = "Gagné !"
    elif player_choice == "Inconnu":
        result = "Geste non reconnu"
    else:
        result = "Perdu..."

    return {"player": player_choice, "computer": computer_choice, "result": result}


# --- Initialisation MediaPipe ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils


# --- Distance euclidienne ---
def distance(a, b):
    return math.sqrt((a.x - b.x) ** 2 + (a.y - b.y) ** 2)


# --- Détection du geste Shifumi ---
@app.post("/capture")
async def capture(data: dict):
    image_data = data.get("image")
    if not image_data:
        return {"message": "Aucune image reçue"}

    # Décodage de l'image base64
    header, encoded = image_data.split(",", 1)
    image_bytes = base64.b64decode(encoded)
    np_arr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Conversion BGR → RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    gesture = "Inconnu"

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        hand_label = results.multi_handedness[0].classification[0].label  # "Left" ou "Right"
        wrist = hand_landmarks.landmark[0]

        # --- Identifier quels doigts sont ouverts ---
        tips_ids = [4, 8, 12, 16, 20]  # pouce, index, majeur, annulaire, auriculaire
        open_fingers = []

        for tip_id in tips_ids:
            finger_tip = hand_landmarks.landmark[tip_id]
            finger_dip = hand_landmarks.landmark[tip_id - 2]

            if tip_id == 4:  # Pouce
                if hand_label == "Right" and finger_tip.x > finger_dip.x:
                    open_fingers.append(tip_id)
                elif hand_label == "Left" and finger_tip.x < finger_dip.x:
                    open_fingers.append(tip_id)
            else:
                if finger_tip.y < finger_dip.y:  # doigt levé
                    open_fingers.append(tip_id)

        fingers_open = len(open_fingers)

        # --- Distances des doigts au poignet ---
        dist_index = distance(wrist, hand_landmarks.landmark[8])
        dist_middle = distance(wrist, hand_landmarks.landmark[12])
        dist_ring = distance(wrist, hand_landmarks.landmark[16])
        dist_pinky = distance(wrist, hand_landmarks.landmark[20])
        avg_dist = (dist_index + dist_middle + dist_ring + dist_pinky) / 4

        # --- Logique améliorée ---
        if fingers_open == 0:
            gesture = "Pierre"

        elif 8 in open_fingers and 12 in open_fingers and fingers_open <= 3:
            # Vérifie que les autres doigts sont bien plus proches du poignet
            if dist_ring < dist_middle * 0.75 and dist_pinky < dist_middle * 0.75:
                gesture = "Ciseaux"
            else:
                gesture = "Feuille"

        elif fingers_open >= 4 or avg_dist > 0.25:
            gesture = "Feuille"
        else:
            gesture = "Inconnu"

    game_result = play_shifumi(gesture)
    return game_result

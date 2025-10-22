from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import base64
import cv2
import numpy as np
import mediapipe as mp
import random

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- FastAPI route page HTML ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- Fonction pour le jeu Shifumi ---
def play_shifumi(player_choice):
    options = ["Pierre", "Feuille", "Ciseaux"]
    computer_choice = random.choice(options)
    if player_choice == computer_choice:
        result = "Égalité"
    elif (player_choice == "Pierre" and computer_choice == "Ciseaux") or \
         (player_choice == "Feuille" and computer_choice == "Pierre") or \
         (player_choice == "Ciseaux" and computer_choice == "Feuille"):
        result = "Gagné !"
    else:
        result = "Perdu..."
    return {"player": player_choice, "computer": computer_choice, "result": result}

# --- Initialisation MediaPipe ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

# --- Route POST pour capturer l'image et détecter le geste ---
@app.post("/capture")
async def capture(data: dict):
    image_data = data.get("image")
    if not image_data:
        return {"message": "Aucune image reçue"}

    # Décodage base64 → image OpenCV
    header, encoded = image_data.split(",", 1)
    image_bytes = base64.b64decode(encoded)
    np_arr = np.frombuffer(image_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Conversion BGR → RGB pour MediaPipe
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    # Détection minimale des doigts pour Shifumi
    gesture = "Inconnu"
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]

        # Liste des landmarks clés : on compte combien de doigts sont "ouverts"
        fingers_open = 0
        tips_ids = [4, 8, 12, 16, 20]  # pouce, index, majeur, annulaire, auriculaire
        for tip_id in tips_ids:
            finger_tip = hand_landmarks.landmark[tip_id]
            finger_dip = hand_landmarks.landmark[tip_id - 2]
            if tip_id != 4:  # pour les doigts sauf pouce
                if finger_tip.y < finger_dip.y:
                    fingers_open += 1
            else:  # pouce
                if finger_tip.x > finger_dip.x:  # simplification pour main droite
                    fingers_open += 1

        # Détermination du geste
        if fingers_open == 0:
            gesture = "Pierre"
        elif fingers_open == 2:
            gesture = "Ciseaux"
        elif fingers_open == 5:
            gesture = "Feuille"
        else:
            gesture = "Inconnu"

    game_result = play_shifumi(gesture)
    return game_result

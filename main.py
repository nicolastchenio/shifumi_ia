from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
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

        # Liste des landmarks clés
        tips_ids = [4, 8, 12, 16, 20]  # pouce, index, majeur, annulaire, auriculaire
        fingers_open = 0

        # Vérification de chaque doigt
        for tip_id in tips_ids:
            finger_tip = hand_landmarks.landmark[tip_id]
            finger_dip = hand_landmarks.landmark[tip_id - 2]

            if tip_id == 4:  # Pouce
                if hand_label == "Right":
                    if finger_tip.x > finger_dip.x:
                        fingers_open += 1
                else:  # Main gauche
                    if finger_tip.x < finger_dip.x:
                        fingers_open += 1
            else:
                # Pour les autres doigts, on compare la position verticale
                if finger_tip.y < finger_dip.y:
                    fingers_open += 1

        # Détermination du geste selon le nombre de doigts ouverts
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

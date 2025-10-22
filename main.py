from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import base64

# Création de l'application FastAPI
# Dossier des templates HTML
# (Optionnel) Dossier des fichiers statiques (CSS, JS, images)
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Fonction de jeu ---
# def play_shifumi(player_choice):
#     options = ["Pierre", "Feuille", "Ciseaux"]
#     computer_choice = random.choice(options)
#     if player_choice == computer_choice:
#         result = "Égalité"
#     elif (player_choice == "Pierre" and computer_choice == "Ciseaux") or \
#          (player_choice == "Feuille" and computer_choice == "Pierre") or \
#          (player_choice == "Ciseaux" and computer_choice == "Feuille"):
#         result = "Gagné !"
#     else:
#         result = "Perdu..."
#     return {"player": player_choice, "computer": computer_choice, "result": result}

# --- Route page HTML ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/capture")
async def capture(data: dict):
    image_data = data.get("image")
    if not image_data:
        return {"message": "Aucune image reçue"}

    # Décodage de l'image base64 (tu pourras ensuite passer à OpenCV/MediaPipe)
    header, encoded = image_data.split(",", 1)
    image_bytes = base64.b64decode(encoded)

    # Sauvegarde temporaire (optionnel)
    with open("capture.jpg", "wb") as f:
        f.write(image_bytes)

    return {"message": "Image reçue !"}
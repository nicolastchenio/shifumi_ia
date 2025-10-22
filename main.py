from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import random

# Création de l'application FastAPI
# Dossier des templates HTML
# (Optionnel) Dossier des fichiers statiques (CSS, JS, images)
app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Fonction de jeu ---
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

# --- Route page HTML ---
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "result": None})

# --- Route POST pour jouer ---
@app.post("/", response_class=HTMLResponse)
async def play(request: Request, player_choice: str = Form(...)):
    game_result = play_shifumi(player_choice)
    return templates.TemplateResponse("index.html", {"request": request, "result": game_result})
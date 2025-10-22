# main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Création de l'application FastAPI
app = FastAPI()

# Dossier des templates HTML
templates = Jinja2Templates(directory="templates")

# (Optionnel) Dossier des fichiers statiques (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Route principale (accueil)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "title": "hello nicolas"})

# --- Exemple d'API JSON ---
@app.get("/api/hello")
async def api_hello():
    return {"message": "Hello depuis ton API FastAPI 👋", "status": "success"}
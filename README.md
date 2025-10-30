# shifumi_ia
Projet Simplon formation developpeur IA. une societe de jeux video souhaite obtenir un prototype d'application web qui permettrait à ses utilisateurs de jouer a shifumi de manière interactive avec leur webcam

Bibliothéque utilisé :
- fastapi
- uvicorn
- jinja2
- opencv-python
- mediapipe
- numpy
- python-multipart

Probleme pour mediapipe il faut une version de Python comprise entre 3.8 et 3.11


Télécharger Python 3.10.x ici :
🔗 https://www.python.org/downloads/release/python-31011/

Installe-le, puis crée un environnement virtuel basé dessus :
py -3.10 -m venv env3.10

activer l'environnement virtuel
env3.10\Scripts\activate

note personnel j ai rajouter 3.10 a env pour savoir que c est python 3.10 que j utilise

pour lancer app :
uvicorn main:app --reload

pour acceder a docs de FastAPI
http://127.0.0.1:8000/docs
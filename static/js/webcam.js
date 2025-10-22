const video = document.getElementById("webcam");
const captureBtn = document.getElementById("capture-btn");
const statusText = document.getElementById("status");

// Accès à la webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
    })
    .catch(err => {
        console.error("Erreur accès webcam :", err);
        statusText.textContent = "Impossible d’accéder à la webcam";
    });

// Capture l'image et envoie au serveur
captureBtn.addEventListener("click", () => {
    // Créer un canvas temporaire
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0);

    // Convertir en base64
    const dataURL = canvas.toDataURL("image/jpeg");

    // Envoyer au serveur via fetch
    fetch("/capture", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: dataURL })
    })
    .then(resp => resp.json())
    .then(data => {
        statusText.textContent = data.message;
    })
    .catch(err => {
        console.error(err);
        statusText.textContent = "Erreur serveur";
    });
});

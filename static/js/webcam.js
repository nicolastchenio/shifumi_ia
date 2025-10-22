const video = document.getElementById("webcam");
const captureBtn = document.getElementById("capture-btn");
const statusText = document.getElementById("status");
const resultText = document.getElementById("result");

// Accès webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => { video.srcObject = stream; })
    .catch(err => { console.error(err); statusText.textContent = "Impossible d’accéder à la webcam"; });

// Capture et envoie au serveur
captureBtn.addEventListener("click", () => {
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext("2d").drawImage(video, 0, 0);
    const dataURL = canvas.toDataURL("image/jpeg");

    fetch("/capture", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: dataURL })
    })
    .then(resp => resp.json())
    .then(data => {
        statusText.textContent = "Geste capturé !";
        resultText.textContent = `Ton choix : ${data.player} | Ordinateur : ${data.computer} | Résultat : ${data.result}`;
    })
    .catch(err => { console.error(err); statusText.textContent = "Erreur serveur"; });
});

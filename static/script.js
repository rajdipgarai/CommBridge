const outputBox = document.getElementById('translation-output');
const historyList = document.getElementById('history-list');
const videoStream = document.getElementById('video-stream');
const cameraOffMsg = document.getElementById('camera-off-msg');
const btnToggleCam = document.getElementById('btn-toggle-cam');
const btnSos = document.getElementById('btn-sos');

// MODAL CONTROLS
const modal = document.getElementById('guide-modal');
const btnGuide = document.getElementById('btn-guide');
const btnCloseGuide = document.getElementById('btn-close-guide');

btnGuide.addEventListener('click', () => { modal.style.display = 'flex'; });
btnCloseGuide.addEventListener('click', () => { modal.style.display = 'none'; });

let lastDetectedSign = "Waiting for sign...";
let isCameraActive = true;
let pollInterval;

function speakText(text, isEmergency = false) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        if (isEmergency) {
            utterance.rate = 1.2;
            utterance.pitch = 1.5;
            utterance.volume = 1;
        }
        window.speechSynthesis.speak(utterance);
    }
}

function addToHistory(sign) {
    const li = document.createElement('li');
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    li.innerHTML = `<span>${sign}</span> <span class="history-time">${time}</span>`;
    
    historyList.prepend(li);
    if (historyList.children.length > 50) { historyList.removeChild(historyList.lastChild); }
}

async function fetchLatestSign() {
    if (!isCameraActive) return;
    try {
        const response = await fetch('/get_sign');
        const data = await response.json();
        
        if (data.sign !== "Waiting for sign..." && data.sign !== lastDetectedSign) {
            outputBox.innerText = data.sign;
            speakText(data.sign);
            addToHistory(data.sign);
            lastDetectedSign = data.sign;
        }
    } catch (error) {}
}

pollInterval = setInterval(fetchLatestSign, 500);

btnToggleCam.addEventListener('click', () => {
    isCameraActive = !isCameraActive;
    if (isCameraActive) {
        videoStream.style.display = 'block';
        cameraOffMsg.style.display = 'none';
        videoStream.src = "/video_feed"; 
        btnToggleCam.innerText = "Pause Camera";
        outputBox.innerText = "Waiting...";
    } else {
        videoStream.style.display = 'none';
        cameraOffMsg.style.display = 'flex';
        videoStream.src = ""; 
        btnToggleCam.innerText = "Start Camera";
        outputBox.innerText = "Paused";
    }
});

btnSos.addEventListener('click', () => {
    outputBox.innerText = "🚨 SOS 🚨";
    outputBox.style.color = "var(--accent-red)"; 
    speakText("Emergency! I need assistance immediately!", true);
    addToHistory("🚨 SOS Triggered");
    
    setTimeout(() => {
        outputBox.style.color = "var(--accent-blue)"; 
        lastDetectedSign = ""; 
    }, 4000);
});
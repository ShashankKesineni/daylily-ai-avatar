const BACKEND_URL = "http://localhost:8000"; // Change if deploying elsewhere

// Session management
function getSessionId() {
  let sid = localStorage.getItem("daylily_session_id");
  if (!sid) {
    sid = Math.random().toString(36).slice(2) + Date.now();
    localStorage.setItem("daylily_session_id", sid);
  }
  return sid;
}
const sessionId = getSessionId();

// DOM elements
const messagesDiv = document.getElementById("messages");
const inputForm = document.getElementById("input-form");
const textInput = document.getElementById("text-input");
const sendBtn = document.getElementById("send-btn");
const micBtn = document.getElementById("mic-btn");
const micIcon = document.getElementById("mic-icon");
const avatarVideo = document.getElementById("avatar-video");
const latencyIndicator = document.getElementById("latency-indicator");
const errorMessage = document.getElementById("error-message");

// Chat message rendering
function addMessage(text, sender = "bot") {
  const msg = document.createElement("div");
  msg.className = `message ${sender}`;
  msg.textContent = text;
  messagesDiv.appendChild(msg);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// Audio recording
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;

micBtn.addEventListener("mousedown", startRecording);
micBtn.addEventListener("touchstart", startRecording);
micBtn.addEventListener("mouseup", stopRecording);
micBtn.addEventListener("mouseleave", stopRecording);
micBtn.addEventListener("touchend", stopRecording);

function startRecording(e) {
  e.preventDefault();
  if (isRecording) return;
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      // Use a more compatible audio format
      const options = { mimeType: 'audio/webm;codecs=opus' };
      try {
        mediaRecorder = new MediaRecorder(stream, options);
      } catch (e) {
        console.log("WebM not supported, falling back to default format");
        mediaRecorder = new MediaRecorder(stream);
      }
      audioChunks = [];
      mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType || 'audio/webm' });
        console.log("Audio recording completed, size:", audioBlob.size, "bytes, type:", audioBlob.type);
        if (audioBlob.size === 0) {
          showError("Audio recording is empty. Please try again.");
          return;
        }
        if (audioBlob.size < 1000) { // Less than 1KB is likely too short
          showError("Recording too short. Please speak for at least 1-2 seconds.");
          return;
        }
        console.log("Sending audio to backend..."); // Debug log
        sendAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };
      mediaRecorder.start();
      isRecording = true;
      micBtn.setAttribute("aria-pressed", "true");
      micIcon.textContent = "⏺️";
    })
    .catch(err => showError("Microphone access denied."));
}

function stopRecording(e) {
  if (!isRecording) return;
  mediaRecorder.stop();
  isRecording = false;
  micBtn.setAttribute("aria-pressed", "false");
  micIcon.textContent = "🎤";
}

// Send audio to backend for transcription
function sendAudio(audioBlob) {
  showError("");
  const formData = new FormData();
  // Use appropriate filename based on audio type
  const filename = audioBlob.type.includes('webm') ? 'audio.webm' : 'audio.wav';
  formData.append("audio", audioBlob, filename);
  const t0 = performance.now();
  
  console.log("Making request to:", `${BACKEND_URL}/transcribe?session_id_query=${sessionId}`); // Debug log
  console.log("Audio blob size:", audioBlob.size, "type:", audioBlob.type); // Debug log
  
  fetch(`${BACKEND_URL}/transcribe?session_id_query=${sessionId}`, {
    method: "POST",
    body: formData
  })
    .then(res => {
      console.log("Response status:", res.status, res.statusText); // Debug log
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      return res.json();
    })
    .then(data => {
      const t1 = performance.now();
      latencyIndicator.textContent = `STT: ${(t1-t0).toFixed(0)}ms`;
      console.log("Transcription response:", data); // Debug log
      if (data.transcript) {
        addMessage(data.transcript, "user");
        handleUserMessage(data.transcript);
      } else if (data.error) {
        showError(`Transcription error: ${data.error}`);
      } else {
        showError("No transcript received.");
      }
    })
    .catch((error) => {
      console.error("Transcription request failed:", error);
      showError(`Transcription failed: ${error.message}`);
    });
}

// Handle text input
inputForm.addEventListener("submit", e => {
  e.preventDefault();
  const text = textInput.value.trim();
  if (!text) return;
  addMessage(text, "user");
  textInput.value = "";
  handleUserMessage(text);
});

// Handle user message: TTS + Avatar
function handleUserMessage(text) {
  showError("");
  // 1. Get TTS audio
  const t0 = performance.now();
  fetch(`${BACKEND_URL}/speak?session_id=${sessionId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text })
  })
    .then(res => res.blob())
    .then(audioBlob => {
      const t1 = performance.now();
      latencyIndicator.textContent = `TTS: ${(t1-t0).toFixed(0)}ms`;
      playAudio(audioBlob);
      // 2. Generate avatar video
      generateAvatar(audioBlob, text);
    })
    .catch(() => showError("TTS failed."));
}

// Play TTS audio
function playAudio(audioBlob) {
  const audioUrl = URL.createObjectURL(audioBlob);
  const audio = new Audio(audioUrl);
  audio.play();
}

// Generate avatar video
function generateAvatar(audioBlob, text) {
  showError("");
  const formData = new FormData();
  formData.append("audio", audioBlob, "audio.wav");
  // Optionally, add an image if you want to support user-uploaded avatars
  // formData.append("image", ...);
  
  // Show loading message
  addMessage("🎬 Generating avatar video...", "bot");
  
  const t0 = performance.now();
  fetch(`${BACKEND_URL}/generate-avatar?session_id_query=${sessionId}`, {
    method: "POST",
    body: formData
  })
    .then(res => {
      if (!res.ok) {
        throw new Error(`Avatar generation failed: ${res.status}`);
      }
      // Return as blob for video playback
      return res.blob();
    })
    .then(videoBlob => {
      const t1 = performance.now();
      latencyIndicator.textContent = `Avatar: ${(t1-t0).toFixed(0)}ms`;
      console.log("Avatar video generated, size:", videoBlob.size, "bytes");
      // Play the video
      playVideo(videoBlob);
    })
    .catch((error) => {
      console.error("Avatar generation error:", error);
      showError("Avatar generation failed.");
    });
}

// Play avatar video
function playVideo(videoBlob) {
  // Create video URL from blob
  const videoUrl = URL.createObjectURL(videoBlob);
  
  // Update the video element
  avatarVideo.src = videoUrl;
  avatarVideo.style.display = "block";
  
  // Play the video
  avatarVideo.play().catch(error => {
    console.error("Error playing video:", error);
    showError("Video playback failed.");
  });
  
  // Clean up URL when video is done
  avatarVideo.onended = () => {
    URL.revokeObjectURL(videoUrl);
  };
  
  // Add a message to indicate video is playing
  addMessage("🎬 Playing avatar video...", "bot");
}

// Error display
function showError(msg) {
  errorMessage.textContent = msg;
}

// Initial greeting
addMessage("Hi! I'm Daylily AI Avatar. How can I help you today?", "bot");

// Add demo mode banner to the top of the page
window.addEventListener('DOMContentLoaded', function() {
  const banner = document.createElement('div');
  banner.textContent = 'Demo Mode: Avatar video is a placeholder. Real AI video coming soon!';
  banner.style.background = '#ffecb3';
  banner.style.color = '#333';
  banner.style.padding = '12px';
  banner.style.textAlign = 'center';
  banner.style.fontWeight = 'bold';
  banner.style.fontSize = '1.1em';
  banner.style.borderBottom = '2px solid #ffc107';
  banner.style.zIndex = '1000';
  banner.style.position = 'sticky';
  banner.style.top = '0';
  document.body.prepend(banner);
}); 
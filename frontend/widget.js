// AI Avatar Chat Widget for Shopify
// (c) 2024. MIT License. See README for usage and config.
(function () {
  // --- Config ---
  const config = window.AI_AVATAR_CHAT_CONFIG || {};
  const backendUrl = config.backendUrl || "http://localhost:8000";
  const avatarImage = config.avatarImage || "https://ui-avatars.com/api/?name=AI";
  const greeting = config.greeting || "Hi! How can I help you today?";
  const theme = config.theme || { primary: "#4f46e5", background: "#fff" };
  const sessionKey = config.sessionKey || "ai_avatar_session";

  // --- Session Management ---
  function getSessionId() {
    let sid = localStorage.getItem(sessionKey);
    if (!sid) {
      sid = Math.random().toString(36).slice(2) + Date.now();
      localStorage.setItem(sessionKey, sid);
    }
    return sid;
  }
  const sessionId = getSessionId();

  // --- DOM Helpers ---
  function el(tag, attrs = {}, ...children) {
    const e = document.createElement(tag);
    for (const k in attrs) {
      if (k.startsWith('on') && typeof attrs[k] === 'function') {
        e.addEventListener(k.slice(2).toLowerCase(), attrs[k]);
      } else if (k === 'style' && typeof attrs[k] === 'object') {
        Object.assign(e.style, attrs[k]);
      } else if (k === 'class') {
        e.className = attrs[k];
      } else {
        e.setAttribute(k, attrs[k]);
      }
    }
    for (const c of children) {
      if (typeof c === 'string') e.appendChild(document.createTextNode(c));
      else if (c) e.appendChild(c);
    }
    return e;
  }

  // --- Widget State ---
  let isOpen = false;
  let isLoading = false;
  let messages = [];
  let currentAudioBlob = null;
  let currentVideoUrl = null;
  let mediaRecorder = null;
  let audioChunks = [];

  // --- Widget UI ---
  const root = document.getElementById('ai-avatar-chat-root');
  if (!root) {
    console.error('AI Avatar Chat: #ai-avatar-chat-root not found');
    return;
  }

  // Apply theme
  document.documentElement.style.setProperty('--ai-avatar-primary', theme.primary);
  document.documentElement.style.setProperty('--ai-avatar-bg', theme.background);

  // --- Main Popup ---
  const popup = el('div', { class: 'ai-avatar-chat-popup', style: { display: 'none' } },
    el('div', { class: 'ai-avatar-chat-header' },
      el('img', { class: 'ai-avatar-chat-avatar', src: avatarImage, alt: 'Avatar' }),
      'AI Assistant',
      el('span', { style: { flex: 1 } }),
      el('button', {
        class: 'ai-avatar-chat-btn',
        style: { background: 'transparent', color: '#fff', fontSize: '20px', border: 'none', cursor: 'pointer' },
        onclick: () => togglePopup(false)
      }, '×')
    ),
    el('div', { class: 'ai-avatar-chat-messages', id: 'ai-avatar-chat-messages' }),
    el('div', { class: 'ai-avatar-chat-input-row' },
      el('input', {
        class: 'ai-avatar-chat-input',
        id: 'ai-avatar-chat-input',
        type: 'text',
        placeholder: 'Type your message...',
        onkeydown: (e) => { if (e.key === 'Enter') sendText(); }
      }),
      el('button', {
        class: 'ai-avatar-chat-btn',
        id: 'ai-avatar-chat-send-btn',
        onclick: sendText
      }, 'Send'),
      el('button', {
        class: 'ai-avatar-chat-btn',
        id: 'ai-avatar-chat-mic-btn',
        style: { marginLeft: '6px', background: '#fff', color: theme.primary, border: `1px solid ${theme.primary}` },
        onclick: toggleRecording
      }, el('span', { id: 'ai-avatar-chat-mic-icon' }, '🎤'))
    )
  );

  // --- Toggle Button ---
  const toggleBtn = el('button', {
    class: 'ai-avatar-chat-toggle-btn',
    onclick: () => togglePopup(!isOpen)
  }, '💬');

  root.appendChild(toggleBtn);
  root.appendChild(popup);

  // --- Message Rendering ---
  function renderMessages() {
    const msgBox = popup.querySelector('#ai-avatar-chat-messages');
    msgBox.innerHTML = '';
    for (const m of messages) {
      if (m.type === 'error') {
        msgBox.appendChild(el('div', { class: 'ai-avatar-chat-error' }, m.text));
      } else if (m.type === 'video') {
        msgBox.appendChild(el('video', {
          class: 'ai-avatar-chat-video',
          src: m.url,
          controls: true,
          autoplay: true
        }));
      } else {
        msgBox.appendChild(el('div', {
          class: 'ai-avatar-chat-bubble ' + (m.role === 'user' ? 'user' : 'ai')
        }, m.text));
      }
    }
    msgBox.scrollTop = msgBox.scrollHeight;
  }

  // --- Popup Control ---
  function togglePopup(open) {
    isOpen = open;
    popup.style.display = isOpen ? 'flex' : 'none';
    toggleBtn.style.display = isOpen ? 'none' : 'flex';
    if (isOpen && messages.length === 0) {
      messages.push({ role: 'ai', text: greeting });
      renderMessages();
    }
  }

  // --- Text Input ---
  function sendText() {
    const input = popup.querySelector('#ai-avatar-chat-input');
    const text = input.value.trim();
    if (!text || isLoading) return;
    input.value = '';
    messages.push({ role: 'user', text });
    renderMessages();
    handleAIResponse({ text });
  }

  // --- Voice Recording ---
  function toggleRecording() {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
      mediaRecorder.stop();
      popup.querySelector('#ai-avatar-chat-mic-icon').textContent = '🎤';
      return;
    }
    navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
      mediaRecorder = new window.MediaRecorder(stream);
      audioChunks = [];
      mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        currentAudioBlob = audioBlob;
        sendAudio(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };
      mediaRecorder.start();
      popup.querySelector('#ai-avatar-chat-mic-icon').textContent = '⏹️';
    }).catch(() => showError('Microphone access denied.'));
  }

  // --- Send Audio to Backend ---
  function sendAudio(blob) {
    if (isLoading) return;
    isLoading = true;
    showSpinner();
    const form = new FormData();
    form.append('file', blob, 'audio.wav');
    fetch(backendUrl + '/transcribe', {
      method: 'POST',
      headers: { 'session_id': sessionId },
      body: form
    })
      .then(r => r.json())
      .then(data => {
        if (data.transcript) {
          messages.push({ role: 'user', text: data.transcript });
          renderMessages();
          handleAIResponse({ text: data.transcript });
        } else {
          showError(data.error || 'Transcription failed.');
        }
      })
      .catch(() => showError('Network error.'))
      .finally(() => hideSpinner());
  }

  // --- Handle AI Response (Text to Speech + Avatar Video) ---
  function handleAIResponse({ text }) {
    isLoading = true;
    showSpinner();
    // 1. Get AI response (simulate, or call your LLM backend here)
    // For demo, echo user text as AI response
    const aiText = `You said: ${text}`;
    setTimeout(() => {
      messages.push({ role: 'ai', text: aiText });
      renderMessages();
      // 2. Get TTS audio
      fetch(backendUrl + '/speak', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'session_id': sessionId
        },
        body: JSON.stringify({ text: aiText })
      })
        .then(r => r.ok ? r.blob() : Promise.reject(r))
        .then(audioBlob => {
          // Optionally play audio
          const audioUrl = URL.createObjectURL(audioBlob);
          const audio = new Audio(audioUrl);
          audio.play();
          // 3. Generate avatar video
          if (currentAudioBlob) {
            sendAvatarVideo(currentAudioBlob);
          } else {
            // fallback: send TTS audio as input
            sendAvatarVideo(audioBlob);
          }
        })
        .catch(() => showError('TTS failed.'))
        .finally(() => { isLoading = false; hideSpinner(); });
    }, 800);
  }

  // --- Send Audio+Image to /generate-avatar ---
  function sendAvatarVideo(audioBlob) {
    isLoading = true;
    showSpinner();
    const form = new FormData();
    form.append('audio', audioBlob, 'audio.wav');
    form.append('image', avatarImage, 'avatar.png'); // If avatarImage is a URL, fetch and convert to blob
    fetchImageAsBlob(avatarImage).then(imgBlob => {
      form.set('image', imgBlob, 'avatar.png');
      fetch(backendUrl + '/generate-avatar', {
        method: 'POST',
        headers: { 'session_id': sessionId },
        body: form
      })
        .then(r => r.ok ? r.blob() : Promise.reject(r))
        .then(videoBlob => {
          if (currentVideoUrl) URL.revokeObjectURL(currentVideoUrl);
          currentVideoUrl = URL.createObjectURL(videoBlob);
          messages.push({ type: 'video', url: currentVideoUrl });
          renderMessages();
        })
        .catch(() => showError('Avatar video failed.'))
        .finally(() => { isLoading = false; hideSpinner(); });
    });
  }

  // --- Fetch image as blob (for avatar) ---
  function fetchImageAsBlob(url) {
    return fetch(url).then(r => r.blob());
  }

  // --- Spinner ---
  function showSpinner() {
    if (!popup.querySelector('.ai-avatar-chat-spinner')) {
      popup.querySelector('.ai-avatar-chat-messages').appendChild(
        el('div', { class: 'ai-avatar-chat-spinner' })
      );
    }
  }
  function hideSpinner() {
    const s = popup.querySelector('.ai-avatar-chat-spinner');
    if (s) s.remove();
  }

  // --- Error Handling ---
  function showError(msg) {
    messages.push({ type: 'error', text: msg });
    renderMessages();
    hideSpinner();
    isLoading = false;
  }

  // --- Expose for debugging ---
  window.AI_AVATAR_CHAT_WIDGET = { open: () => togglePopup(true) };
})(); 
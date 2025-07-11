# AI Avatar Chat Widget for Shopify

## Features
- Popup chat interface with text and voice input
- Streams AI responses and avatar video in real-time
- Session management via cookies/local storage
- Customizable avatar, greetings, and UI styling
- Lightweight, fast, and Shopify-compatible

## Usage
1. **Build or copy the `frontend/` directory to your Shopify app or theme.**
2. **Embed the widget:**
   - Add the following to your Shopify theme's `<head>` or via the theme editor:
     ```html
     <script src="/path/to/frontend/widget.js"></script>
     <link rel="stylesheet" href="/path/to/frontend/widget.css">
     <div id="ai-avatar-chat-root"></div>
     <script>window.AI_AVATAR_CHAT_CONFIG = { /* see below */ };</script>
     ```
3. **Configure:**
   - Set `window.AI_AVATAR_CHAT_CONFIG` with options:
     - `backendUrl`: Backend API base URL
     - `avatarImage`: Avatar image URL
     - `greeting`: Initial greeting text
     - `theme`: UI color/theme options
     - `sessionKey`: (optional) Key for session storage

## Customization
- Change avatar image, greeting, and theme via config.
- Edit `widget.css` for advanced styling.

## Requirements
- Backend endpoints `/transcribe`, `/speak`, `/generate-avatar` must be accessible from the Shopify store.

## Example Config
```js
window.AI_AVATAR_CHAT_CONFIG = {
  backendUrl: "https://your-backend-url",
  avatarImage: "/avatar.png",
  greeting: "Hi! How can I help you today?",
  theme: { primary: "#4f46e5", background: "#fff" },
  sessionKey: "ai_avatar_session"
};
```

## Notes
- The widget is fully self-contained and can be embedded on any page.
- For advanced integration, see code comments in `widget.js`. 
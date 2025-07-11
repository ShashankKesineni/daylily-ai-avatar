import threading
import uuid
import time
import logging
from typing import Optional, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)

# Session timeout in seconds (e.g., 30 minutes)
SESSION_TIMEOUT = 1800

class SessionManager:
    """
    Thread-safe in-memory session manager for FastAPI backend.
    Each session is identified by a UUID token.
    """
    def __init__(self):
        self.sessions: Dict[str, float] = {}  # session_id -> last_access timestamp
        self.lock = threading.Lock()

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        with self.lock:
            self.sessions[session_id] = time.time()
        logging.info(f"Session created: {session_id}")
        return session_id

    def touch_session(self, session_id: str) -> bool:
        """Update last access time if session exists and not expired."""
        with self.lock:
            if session_id in self.sessions:
                if time.time() - self.sessions[session_id] < SESSION_TIMEOUT:
                    self.sessions[session_id] = time.time()
                    logging.info(f"Session used: {session_id}")
                    return True
                else:
                    # Session expired
                    del self.sessions[session_id]
                    logging.info(f"Session expired: {session_id}")
        return False

    def cleanup_sessions(self):
        """Remove expired sessions."""
        with self.lock:
            expired = [sid for sid, ts in self.sessions.items() if time.time() - ts >= SESSION_TIMEOUT]
            for sid in expired:
                del self.sessions[sid]
                logging.info(f"Session expired (cleanup): {sid}")

    def get_active_sessions(self) -> int:
        with self.lock:
            return len(self.sessions)

# Singleton instance
session_manager = SessionManager()

def get_or_create_session(session_id: Optional[str]) -> str:
    """
    Retrieve a valid session or create a new one if not provided or expired.
    Returns a valid session_id.
    """
    if session_id and session_manager.touch_session(session_id):
        return session_id
    return session_manager.create_session() 
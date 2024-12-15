from datetime import datetime, timedelta
from typing import Dict, Optional
from agents.base import AgentState
import uuid

class SessionStore:
    def __init__(self):
        self.sessions: Dict[str, AgentState] = {}
        self.session_expiry: Dict[str, datetime] = {}
        self.expiry_time = timedelta(minutes=30)

    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = None
        self.session_expiry[session_id] = datetime.now() + self.expiry_time
        return session_id

    def get_session(self, session_id: str) -> Optional[AgentState]:
        self.cleanup_expired()
        if session_id in self.sessions:
            self.session_expiry[session_id] = datetime.now() + self.expiry_time
            return self.sessions.get(session_id)
        return None

    def update_session(self, session_id: str, state: AgentState):
        self.sessions[session_id] = state
        self.session_expiry[session_id] = datetime.now() + self.expiry_time

    def cleanup_expired(self):
        current_time = datetime.now()
        expired = [
            sid for sid, expiry in self.session_expiry.items()
            if current_time > expiry
        ]
        for sid in expired:
            del self.sessions[sid]
            del self.session_expiry[sid]

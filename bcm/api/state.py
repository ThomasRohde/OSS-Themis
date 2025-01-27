from dataclasses import dataclass, field
from typing import Dict

from fastapi import WebSocket


@dataclass
class AppState:
    """Centralized state management for the application."""
    active_users: Dict[str, dict] = field(default_factory=dict)
    
    def __post_init__(self):
        self.connection_manager = ConnectionManager()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}  # session_id -> websocket
        self.session_to_user: Dict[str, str] = {}  # session_id -> nickname

    async def connect(self, websocket: WebSocket, session_id: str, nickname: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.session_to_user[session_id] = nickname

    def disconnect(self, session_id: str) -> str | None:
        """Disconnect a session and return the user's nickname if found"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        
        nickname = None
        if session_id in self.session_to_user:
            nickname = self.session_to_user[session_id]
            del self.session_to_user[session_id]
            
        # Clean up user session and locks
        if session_id in app_state.active_users:
            if not nickname:
                nickname = app_state.active_users[session_id]["nickname"]
            # Clear any locks held by the user
            if app_state.active_users[session_id]["locked_capabilities"]:
                app_state.active_users[session_id]["locked_capabilities"] = []
            del app_state.active_users[session_id]
            
        return nickname

    async def broadcast_model_change(self, user_nickname: str, action: str):
        disconnected_sessions = []
        for session_id, connection in self.active_connections.items():
            try:
                await connection.send_json({
                    "type": "model_changed",
                    "user": user_nickname,
                    "action": action
                })
            except Exception:  # Including WebSocketDisconnect
                disconnected_sessions.append(session_id)
        
        # Clean up any disconnected sessions
        for session_id in disconnected_sessions:
            nickname = self.disconnect(session_id)
            if nickname:
                # Recursively broadcast that user left, but skip disconnected sessions
                active_connections = dict(self.active_connections)  # Make a copy
                for conn in active_connections.values():
                    try:
                        await conn.send_json({
                            "type": "user_event",
                            "user": nickname,
                            "event": "left"
                        })
                    except Exception:  # Including WebSocketDisconnect
                        pass

    async def broadcast_user_event(self, user_nickname: str, event_type: str):
        disconnected_sessions = []
        for session_id, connection in self.active_connections.items():
            try:
                await connection.send_json({
                    "type": "user_event",
                    "user": user_nickname,
                    "event": event_type
                })
            except Exception:  # Including WebSocketDisconnect
                disconnected_sessions.append(session_id)
        
        # Clean up any disconnected sessions
        for session_id in disconnected_sessions:
            nickname = self.disconnect(session_id)
            if nickname and nickname != user_nickname:  # Avoid recursive broadcast for same user
                # Recursively broadcast that user left, but skip disconnected sessions
                active_connections = dict(self.active_connections)  # Make a copy
                for conn in active_connections.values():
                    try:
                        await conn.send_json({
                            "type": "user_event",
                            "user": nickname,
                            "event": "left"
                        })
                    except Exception:  # Including WebSocketDisconnect
                        pass

# Create a single instance of AppState to be imported by other modules
app_state = AppState()

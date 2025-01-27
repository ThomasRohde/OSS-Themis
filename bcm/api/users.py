import uuid
from typing import List

from fastapi import APIRouter, HTTPException

from bcm.api.state import app_state
from bcm.models import User, UserSession

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.post(
    "",
    response_model=UserSession,
    responses={
        200: {"description": "Successfully created user session"},
        409: {"description": "Nickname already in use"}
    },
    description="Create a new user session and broadcast join event to other users"
)
async def create_user_session(user: User):
    """Create a new user session."""
    # Check if nickname is already in use
    if any(session["nickname"] == user.nickname for session in app_state.active_users.values()):
        raise HTTPException(status_code=409, detail="Nickname is already in use")
    
    session_id = str(uuid.uuid4())
    print("User joined:", user.nickname, session_id)
    session = {
        "session_id": session_id,
        "nickname": user.nickname,
        "locked_capabilities": []
    }
    app_state.active_users[session_id] = session
    # Broadcast user joined event
    await app_state.connection_manager.broadcast_user_event(user.nickname, "joined")
    return UserSession(**session)

@router.get(
    "",
    response_model=List[UserSession],
    description="Get list of all active users and their locked capabilities"
)
async def get_active_users():
    """Get all active users and their locked capabilities."""
    return [UserSession(**session) for session in app_state.active_users.values()]

@router.delete(
    "/{session_id}",
    responses={
        200: {"description": "Session removed and locks cleared"},
        404: {"description": "Session not found"}
    },
    description="Remove a user session and clear any locks held by the user"
)
async def remove_user_session(session_id: str):
    """Remove a user session and clear any locks held by the user."""
    if session_id not in app_state.active_users:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get user info before removing
    user = app_state.active_users[session_id]
    nickname = user["nickname"]
    
    # Clear any locks held by the user
    if user["locked_capabilities"]:
        user["locked_capabilities"] = []
        # Broadcast that locks were cleared
        await app_state.connection_manager.broadcast_model_change(nickname, "cleared their capability locks")
    
    # Remove the user session
    del app_state.active_users[session_id]
    
    # Broadcast user left event
    await app_state.connection_manager.broadcast_user_event(nickname, "left")
    
    return {"message": "Session removed and locks cleared"}

import os
import socket
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession

from bcm.api.settings import router as settings_router
from bcm.api.state import app_state
from bcm.api.users import router as users_router
from bcm.api.utilities import utilities_router
from bcm.api import confluence, io
from bcm.database import DatabaseOperations
from bcm.models import (
    AsyncSessionLocal,
    CapabilityCreate,
    CapabilityMove,
    CapabilityUpdate,
    PromptUpdate,
    get_db,
    init_db,
)

# Initialize database operations
db_ops = DatabaseOperations(AsyncSessionLocal)


def get_all_ipv4_addresses():
    """Get all available IPv4 addresses including VPN."""
    ip_addresses = []
    try:
        # Get all network interfaces
        interfaces = socket.getaddrinfo(
            socket.gethostname(), None, socket.AF_INET
        )  # AF_INET for IPv4 only
        for interface in interfaces:
            ip = interface[4][0]
            # Only include IPv4 addresses and exclude localhost
            if ip and not ip.startswith("127."):
                ip_addresses.append(ip)
        # Remove duplicates while preserving order
        return list(dict.fromkeys(ip_addresses))
    except Exception:
        # Fallback to basic hostname resolution
        try:
            return [socket.gethostbyname(socket.gethostname())]
        except Exception:
            return ["127.0.0.1"]  # Last resort fallback


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    # Initialize database
    await init_db()

    # Get port from uvicorn command arguments
    import sys

    port = 80  # Default port

    # Check if running with uvicorn CLI
    if "uvicorn" in sys.argv[0]:
        try:
            # Find --port argument
            port_index = sys.argv.index("--port") + 1
            if port_index < len(sys.argv):
                port = int(sys.argv[port_index])
        except (ValueError, IndexError):
            pass

    # Get all available IPv4 addresses
    ip_addresses = get_all_ipv4_addresses()

    print("\nAvailable network URLs:")
    urls = [f"http://{ip}:{port}" for ip in ip_addresses]

    for url in urls:
        print(f"- {url}")

    print("\nShare any of these URLs with other users to access the application")

    yield  # Server is running


# Initialize FastAPI app
app = FastAPI(
    title="Themis",
    description="Themis is a concept modeling and business capability mapping tool",
    version="0.1.13",
    contact={
        "name": "thomas@rohde.name",
        "url": "https://github.com/ThomasRohde/themis",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
)

api_app = FastAPI(
    title="Themis API",
    description="""
    REST API for Themis business capability modeling platform.
    
    This API provides comprehensive functionality for:
    - Creating and managing hierarchical business capability models
    - Real-time collaboration with multiple users
    - Export capabilities to various formats including ArchiMate, PowerPoint, and Confluence
    - Smart layout calculations for optimal visualization
    - User session management and capability locking
    - Template-based capability generation
    
    The API supports both synchronous REST endpoints and WebSocket connections for real-time updates.
    """,
    version="0.1.13",
)

# Add CORS middleware
api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

# Include routers
api_app.include_router(users_router)
api_app.include_router(settings_router)
api_app.include_router(utilities_router)
api_app.include_router(confluence.router)
api_app.include_router(io.router)

# Mount API routes
app.mount("/api", api_app)

# Mount static files
static_client_dir = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "static", "client"
)
app.mount(
    "/assets",
    StaticFiles(directory=os.path.join(static_client_dir, "assets")),
    name="assets",
)


@app.get("/")
async def serve_spa():
    return FileResponse(os.path.join(static_client_dir, "index.html"))


@app.get("/{full_path:path}")
async def serve_spa_routes(full_path: str):
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(os.path.join(static_client_dir, "index.html"))


@api_app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    # Verify session exists
    if session_id not in app_state.active_users:
        await websocket.close(code=4000)
        return

    nickname = app_state.active_users[session_id]["nickname"]
    await app_state.connection_manager.connect(websocket, session_id, nickname)

    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        nickname = app_state.connection_manager.disconnect(session_id)
        if nickname:
            # Broadcast user left event
            await app_state.connection_manager.broadcast_user_event(nickname, "left")


@api_app.post("/capabilities/lock/{capability_id}")
async def lock_capability(
    capability_id: int, nickname: str, db: AsyncSession = Depends(get_db)
):
    """Lock a capability for editing."""
    # Find user by nickname
    user_session = next(
        (
            session
            for session in app_state.active_users.values()
            if session["nickname"] == nickname
        ),
        None,
    )
    if not user_session:
        raise HTTPException(status_code=404, detail="User not found")

    # Get the capability to check its ancestors
    capability = await db_ops.get_capability(capability_id, db)
    if not capability:
        raise HTTPException(status_code=404, detail="Capability not found")

    # Check if any ancestor capabilities are locked
    current_parent_id = capability.parent_id
    while current_parent_id is not None:
        # Check if parent is locked by any user
        for user in app_state.active_users.values():
            if current_parent_id in user["locked_capabilities"]:
                # Parent is locked, silently ignore the lock request
                return {"message": "Capability is already locked by inheritance"}

        # Move up to next parent
        parent = await db_ops.get_capability(current_parent_id, db)
        if not parent:
            break
        current_parent_id = parent.parent_id

    # Check if capability itself is already locked
    for user in app_state.active_users.values():
        if capability_id in user["locked_capabilities"]:
            raise HTTPException(status_code=409, detail="Capability is already locked")

    # No ancestor locks found, proceed with locking
    user_session["locked_capabilities"].append(capability_id)
    # Broadcast lock change
    await app_state.connection_manager.broadcast_model_change(
        user_session["nickname"], f"locked capability '{capability.name}'"
    )
    return {"message": "Capability locked"}


@api_app.post("/capabilities/unlock/{capability_id}")
async def unlock_capability(
    capability_id: int, nickname: str, db: AsyncSession = Depends(get_db)
):
    """Unlock a capability."""
    # Find user by nickname
    user_session = next(
        (
            session
            for session in app_state.active_users.values()
            if session["nickname"] == nickname
        ),
        None,
    )
    if not user_session:
        raise HTTPException(status_code=404, detail="User not found")

    if capability_id in user_session["locked_capabilities"]:
        # Get capability name before unlocking
        capability = await db_ops.get_capability(capability_id, db)
        if not capability:
            raise HTTPException(status_code=404, detail="Capability not found")

        user_session["locked_capabilities"].remove(capability_id)
        # Broadcast unlock change
        await app_state.connection_manager.broadcast_model_change(
            user_session["nickname"], f"unlocked capability '{capability.name}'"
        )
        return {"message": "Capability unlocked"}

    raise HTTPException(status_code=404, detail="Capability not locked by this user")


@api_app.post("/capabilities", response_model=dict)
async def create_capability(
    capability: CapabilityCreate, session_id: str, db: AsyncSession = Depends(get_db)
):
    """Create a new capability."""
    if session_id not in app_state.active_users:
        raise HTTPException(status_code=404, detail="Session not found")

    result = await db_ops.create_capability(capability, db)
    # Notify all clients about model change
    await app_state.connection_manager.broadcast_model_change(
        app_state.active_users[session_id]["nickname"],
        f"created capability '{result.name}'",
    )
    return {
        "id": result.id,
        "name": result.name,
        "description": result.description,
        "parent_id": result.parent_id,
    }


@api_app.get("/capabilities/{capability_id}", response_model=dict)
async def get_capability(capability_id: int, db: AsyncSession = Depends(get_db)):
    """Get a capability by ID."""
    result = await db_ops.get_capability(capability_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="Capability not found")
    return {
        "id": result.id,
        "name": result.name,
        "description": result.description,
        "parent_id": result.parent_id,
    }


@api_app.get("/capabilities/{capability_id}/context")
async def get_capability_context_endpoint(
    capability_id: int, db: AsyncSession = Depends(get_db)
):
    """Get a capability's context rendered in template format for clipboard."""
    from bcm.settings import Settings
    from bcm.utils import get_capability_context, jinja_env

    # Get capability info
    capability = await db_ops.get_capability(capability_id, db)
    if not capability:
        raise HTTPException(status_code=404, detail="Capability not found")

    # Get context
    context = await get_capability_context(db_ops, capability_id)
    if not context:
        raise HTTPException(status_code=404, detail="Context not found")

    # Get settings
    settings = Settings()

    # Determine if this is a first-level capability
    is_first_level = not capability.parent_id

    # Render appropriate template
    if is_first_level:
        template = jinja_env.get_template(settings.get("first_level_template"))
        rendered_context = template.render(
            organisation_name=capability.name,
            organisation_description=capability.description
            or f"An organization focused on {capability.name}",
            first_level=settings.get("first_level_range"),
        )
    else:
        template = jinja_env.get_template(settings.get("normal_template"))
        rendered_context = template.render(
            capability_name=capability.name,
            context=context,
            max_capabilities=settings.get("max_ai_capabilities"),
        )

    return {"rendered_context": rendered_context}


@api_app.put("/capabilities/{capability_id}", response_model=dict)
async def update_capability(
    capability_id: int,
    capability: CapabilityUpdate,
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Update a capability."""
    if session_id not in app_state.active_users:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check if capability is locked by another user
    current_user = app_state.active_users[session_id]
    for user in app_state.active_users.values():
        if (
            capability_id in user["locked_capabilities"]
            and user["nickname"] != current_user["nickname"]
        ):
            raise HTTPException(
                status_code=409, detail="Capability is locked by another user"
            )

    result = await db_ops.update_capability(capability_id, capability, db)
    if not result:
        raise HTTPException(status_code=404, detail="Capability not found")
    # Notify all clients about model change
    await app_state.connection_manager.broadcast_model_change(
        app_state.active_users[session_id]["nickname"],
        f"updated capability '{result.name}'",
    )
    return {
        "id": result.id,
        "name": result.name,
        "description": result.description,
        "parent_id": result.parent_id,
    }


@api_app.delete("/capabilities/{capability_id}")
async def delete_capability(
    capability_id: int, session_id: str, db: AsyncSession = Depends(get_db)
):
    """Delete a capability."""
    if session_id not in app_state.active_users:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check if capability is locked by another user
    current_user = app_state.active_users[session_id]
    for user in app_state.active_users.values():
        if (
            capability_id in user["locked_capabilities"]
            and user["nickname"] != current_user["nickname"]
        ):
            raise HTTPException(
                status_code=409, detail="Capability is locked by another user"
            )

    # Get capability name before deletion
    capability = await db_ops.get_capability(capability_id, db)
    if not capability:
        raise HTTPException(status_code=404, detail="Capability not found")

    result = await db_ops.delete_capability(capability_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="Capability not found")
    # Notify all clients about model change
    await app_state.connection_manager.broadcast_model_change(
        app_state.active_users[session_id]["nickname"],
        f"deleted capability '{capability.name}'",
    )
    return {"message": "Capability deleted"}


@api_app.post("/capabilities/{capability_id}/move")
async def move_capability(
    capability_id: int,
    move: CapabilityMove,
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Move a capability to a new parent and/or position."""
    if session_id not in app_state.active_users:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check if capability is locked by another user
    current_user = app_state.active_users[session_id]
    for user in app_state.active_users.values():
        if (
            capability_id in user["locked_capabilities"]
            and user["nickname"] != current_user["nickname"]
        ):
            raise HTTPException(
                status_code=409, detail="Capability is locked by another user"
            )

    # Get capability name before move
    capability = await db_ops.get_capability(capability_id, db)
    if not capability:
        raise HTTPException(status_code=404, detail="Capability not found")

    result = await db_ops.update_capability_order(
        capability_id, move.new_parent_id, move.new_order
    )
    if not result:
        raise HTTPException(status_code=404, detail="Capability not found")
    # Notify all clients about model change
    await app_state.connection_manager.broadcast_model_change(
        app_state.active_users[session_id]["nickname"],
        f"moved capability '{capability.name}'",
    )
    return {"message": "Capability moved successfully"}


@api_app.put("/capabilities/{capability_id}/description")
async def update_description(
    capability_id: int,
    description: str,
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Update a capability's description."""
    if session_id not in app_state.active_users:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check if capability is locked by another user
    current_user = app_state.active_users[session_id]
    for user in app_state.active_users.values():
        if (
            capability_id in user["locked_capabilities"]
            and user["nickname"] != current_user["nickname"]
        ):
            raise HTTPException(
                status_code=409, detail="Capability is locked by another user"
            )

    result = await db_ops.save_description(capability_id, description)
    if not result:
        raise HTTPException(status_code=404, detail="Capability not found")
    return {"message": "Description updated successfully"}


@api_app.put("/capabilities/{capability_id}/prompt")
async def update_prompt(
    capability_id: int, prompt_update: PromptUpdate, session_id: str
):
    """Update a capability's first-level or expansion prompt."""
    if session_id not in app_state.active_users:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check if capability is locked by another user
    current_user = app_state.active_users[session_id]
    for user in app_state.active_users.values():
        if (
            capability_id in user["locked_capabilities"]
            and user["nickname"] != current_user["nickname"]
        ):
            raise HTTPException(
                status_code=409, detail="Capability is locked by another user"
            )

    # In a real implementation, this would update the prompt in a database
    # For now, we'll just return success
    return {"message": f"{prompt_update.prompt_type} prompt updated successfully"}


@api_app.get("/capabilities", response_model=List[dict])
async def get_capabilities(
    parent_id: Optional[int] = None,
    hierarchical: bool = False,
    db: AsyncSession = Depends(get_db),
):
    """
    Get capabilities, optionally filtered by parent_id.
    If hierarchical=True, returns full tree structure under the parent_id.
    If hierarchical=False, returns flat list of immediate children.
    """
    if hierarchical:
        if parent_id is None:
            # Get full hierarchy starting from root
            return await db_ops.get_all_capabilities()
        else:
            # Get hierarchy starting from specific parent
            result = await db_ops.get_capability_with_children(parent_id)
            return [result] if result else []
    else:
        # Original flat list behavior
        capabilities = await db_ops.get_capabilities(parent_id, db)
        return [
            {
                "id": cap.id,
                "name": cap.name,
                "description": cap.description,
                "parent_id": cap.parent_id,
                "order_position": cap.order_position,
            }
            for cap in capabilities
        ]


def main():
    import sys

    import uvicorn

    # Default port
    port = 80

    # Check for port argument
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)

    try:
        # Store the port in app state for lifespan to access
        app.state.port = port
        print(f"Starting server on port {port}")
        uvicorn.run(app, host="0.0.0.0", port=port)
    except OSError as e:
        print(f"ERROR: Could not start server on port {port} - port is already in use.")
        print("Please ensure no other instance of the server is running and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()

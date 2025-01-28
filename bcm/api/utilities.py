import zipfile
from io import BytesIO
from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from bcm.api.state import app_state
from bcm.context_export import export_context
from bcm.database import DatabaseOperations
from bcm.models import AuditLogEntry, Capability

# Initialize database operations
from bcm.models import AsyncSessionLocal
db_ops = DatabaseOperations(AsyncSessionLocal)

# Create router
utilities_router = APIRouter(
    prefix="",  # Keep original paths
    tags=["utilities"],
    responses={404: {"description": "Not found"}},
)

@utilities_router.get(
    "/context",
    response_class=Response,
    responses={
        200: {
            "description": "Successfully exported context",
            "content": {
                "text/markdown": {
                    "schema": {"type": "string"},
                    "description": "Single markdown file containing the context"
                },
                "application/zip": {
                    "schema": {"type": "string", "format": "binary"},
                    "description": "ZIP archive containing multiple markdown files"
                }
            }
        },
        404: {"description": "No capabilities or content found"},
        500: {"description": "Internal server error"}
    },
    description="""
    Export the entire capability model context as markdown file(s).
    Returns either a single markdown file or a ZIP archive containing multiple markdown files
    depending on the size and complexity of the model.
    The filename is derived from the root capability name.
    """
)
async def get_context():
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for Windows compatibility."""
        # Replace invalid characters with underscore
        invalid_chars = '<>:"/\\|?*'
        sanitized = ''.join('_' if c in invalid_chars else c for c in filename)
        # Remove trailing spaces and periods
        sanitized = sanitized.rstrip('. ')
        # Limit length to 255 characters
        return sanitized[:255]

    try:
        # First get capabilities to find root node
        root_nodes: List[Capability] = await db_ops.get_capabilities(parent_id=None)
        if not root_nodes:
            raise HTTPException(status_code=404, detail="No capabilities found")
        
        # Use first root node's name for filename
        root_name: str = sanitize_filename(root_nodes[0].name)
        if not root_name:
            root_name = "capability_model"  # fallback name
        
        # Get markdown content split into files
        files: List[tuple[str, str]] = await export_context(db_ops)
        if not files:
            raise HTTPException(status_code=404, detail="No content to export")
        
        # If only one file and small enough, return directly
        if len(files) == 1:
            return Response(
                content=files[0][1],
                media_type="text/markdown",
                headers={"Content-Disposition": f"attachment; filename={root_name}.md"}
            )
        
        # Otherwise create zip file containing all parts
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in files:
                zip_file.writestr(filename, content)
        
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={root_name}.zip"}
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@utilities_router.post("/reset")
async def reset_database(session_id: str):
    """Reset database and clear locks but preserve sessions and users."""
    if session_id not in app_state.active_users:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Clear all capabilities
        await db_ops.clear_all_capabilities()
        
        # Clear all locks from users while preserving sessions
        for user in app_state.active_users.values():
            user["locked_capabilities"] = []
            
        # Broadcast the reset action
        await app_state.connection_manager.broadcast_model_change(
            app_state.active_users[session_id]["nickname"],
            "reset database and cleared all locks"
        )
        
        return {"message": "Database reset and locks cleared successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@utilities_router.get("/logs", response_model=List[AuditLogEntry])
async def get_audit_logs():
    """Get all audit logs."""
    try:
        logs = await db_ops.export_audit_logs()
        return logs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@utilities_router.post("/clearlocks")
async def clear_all_locks(session_id: str):
    """Clear all capability locks and notify users."""
    if session_id not in app_state.active_users:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get the user who initiated the clear
    current_user = app_state.active_users[session_id]
    
    # Clear all locks from all users
    for user in app_state.active_users.values():
        user["locked_capabilities"] = []
    
    # Broadcast the clear locks action
    await app_state.connection_manager.broadcast_model_change(
        current_user["nickname"],
        "cleared all capability locks"
    )
    
    return {"message": "All capability locks cleared"}

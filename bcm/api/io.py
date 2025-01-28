from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from bcm.api.export_handler import format_capability
from bcm.api.state import app_state
from bcm.database import DatabaseOperations
from bcm.layout_manager import process_layout
from bcm.models import (
    AsyncSessionLocal,
    FormatRequest,
    ImportData,
    LayoutModel,
    get_db
)
from bcm.settings import Settings

# Initialize database operations
db_ops = DatabaseOperations(AsyncSessionLocal)

router = APIRouter(tags=["io"])

@router.post("/import")
async def import_capabilities(
    import_data: ImportData, session_id: str, db: AsyncSession = Depends(get_db)
):
    """Import capabilities from JSON data."""
    if session_id not in app_state.active_users:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        await db_ops.import_capabilities(import_data.data)
        # Notify all clients about model change
        await app_state.connection_manager.broadcast_model_change(
            app_state.active_users[session_id]["nickname"], "imported capabilities"
        )
        return {"message": "Capabilities imported successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/export")
async def export_capabilities(session_id: str, db: AsyncSession = Depends(get_db)):
    """Export capabilities to JSON."""
    if session_id not in app_state.active_users:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        data = await db_ops.export_capabilities()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/layout/{node_id}", response_model=LayoutModel)
async def get_layout(node_id: int, db: AsyncSession = Depends(get_db)):
    """Get layouted model starting from the specified node ID."""
    # Get hierarchical data starting from node
    node_data = await db_ops.get_capability_with_children(node_id)
    if not node_data:
        raise HTTPException(status_code=404, detail="Node not found")

    # Convert to layout format using shared method
    settings = Settings()
    max_level = settings.get("max_level", 6)
    layout_model = LayoutModel.convert_to_layout_format(node_data, max_level)
    return process_layout(layout_model, settings)


@router.post("/format/{node_id}")
async def format_node(
    node_id: int, format_request: FormatRequest, db: AsyncSession = Depends(get_db)
):
    """Format a node and its children in the specified format."""
    # Get hierarchical data starting from node
    node_data = await db_ops.get_capability_with_children(node_id)
    if not node_data:
        raise HTTPException(status_code=404, detail="Node not found")

    # Convert to layout format
    settings = Settings()
    max_level = settings.get("max_level", 6)
    layout_model = LayoutModel.convert_to_layout_format(node_data, max_level)

    return format_capability(node_id, format_request.format, layout_model, settings)

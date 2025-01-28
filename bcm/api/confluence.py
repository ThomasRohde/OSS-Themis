import json
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from bcm.models import AsyncSessionLocal, ConfluencePublishRequest, get_db
from bcm.confluence import publish_capability_to_confluence
from bcm.api.state import app_state
from bcm.database import DatabaseOperations

# Initialize database operations
db_ops = DatabaseOperations(AsyncSessionLocal)

router = APIRouter(tags=["io"])

@router.post(
    "/confluence/{capability_id}",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "Stream of publish progress updates",
            "content": {
                "application/x-ndjson": {
                    "schema": {
                        "type": "string",
                        "format": "ndjson",
                        "example": '{"total_pages": 5, "current_page": 1, "page_title": "My Capability", "url": "https://..."}\n{"total_pages": 5, "current_page": 2, "page_title": "Sub Capability", "url": "https://..."}\n',
                    }
                }
            },
        },
        404: {"description": "Session not found"},
        500: {"description": "Publishing error occurred"},
    },
)
async def publish_to_confluence(
    capability_id: int,
    request: ConfluencePublishRequest,
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Publish a capability and its children to Confluence with progress updates.

    Returns a stream of newline-delimited JSON objects containing:
    - total_pages: Total number of pages to be published
    - current_page: Current page being published
    - page_title: Title of the current page
    - url: URL of the published page (on success)
    - error: Error message (if an error occurs)
    """
    if session_id not in app_state.active_users:
        raise HTTPException(status_code=404, detail="Session not found")

    async def progress_stream():
        """Generate progress updates as JSON Lines."""
        try:
            async for progress in publish_capability_to_confluence(
                db_ops=db_ops,
                capability_id=capability_id,
                space_key=request.space_key,
                token=request.token,
                parent_page_title=request.parent_page_title,
                confluence_url=request.confluence_url,
            ):
                # Convert progress model to JSON and yield
                yield json.dumps(progress.model_dump()) + "\n"

            # After successful completion, notify all clients
            await app_state.connection_manager.broadcast_model_change(
                app_state.active_users[session_id]["nickname"],
                "published to Confluence",
            )

        except Exception as e:
            # Yield error as final message
            yield (
                json.dumps(
                    {
                        "error": str(e),
                        "total_pages": 0,
                        "current_page": 0,
                        "page_title": "",
                    }
                )
                + "\n"
            )

    return StreamingResponse(progress_stream(), media_type="application/x-ndjson")

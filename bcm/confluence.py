import logging
from typing import Any, AsyncGenerator, Dict, Optional

import markdown
from atlassian import Confluence

from bcm.database import DatabaseOperations
from bcm.html_export import export_to_html_macro
from bcm.models import LayoutModel, PublishProgress
from bcm.settings import Settings


class ConfluenceFormatter:
    """Formats capability data into Confluence storage format."""
    
    def __init__(self):
        """Initialize Markdown converter."""
        self.markdown = markdown.Markdown(extensions=['fenced_code', 'tables'])
        self.html_escapes = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;",
        }
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        for char, escape in self.html_escapes.items():
            text = text.replace(char, escape)
        return text
    
    def _convert_markdown(self, text: str) -> str:
        """Convert markdown text to HTML."""
        return self.markdown.convert(self._escape_html(text) or '')
    
    def _format_leaf_capability(self, capability: Dict[Any, Any]) -> str:
        """Format a capability with no children."""
        return "\n".join([
            f"<h1>{self._escape_html(capability['name'])}</h1>",
            f"<p>{self._convert_markdown(capability.get('description', ''))}</p>"
        ])
    
    def _format_capability_with_leaf_children(self, capability: Dict[Any, Any], children: list) -> str:
        """Format a capability whose children are all leaf nodes."""
        content = [
            f"<p>{self._convert_markdown(capability.get('description', ''))}</p>"
        ]

        # Add capability model visualization
        settings = Settings()
        max_level = settings.get("max_level", 6)
        layout_data = {
            "id": capability["id"],
            "name": capability["name"],
            "description": capability.get("description", ""),
            "children": children
        }
        layout_model = LayoutModel.convert_to_layout_format(layout_data, max_level)
        
        # Generate HTML layout and wrap in Confluence HTML macro
        html_content = export_to_html_macro(layout_model, settings)
        wrapped_content = f"""<ac:structured-macro ac:macro-id="128a5fdd-f45d-4300-b6fe-4fc28e6f21b1" ac:name="html" ac:schema-version="1">
 <ac:plain-text-body><![CDATA[{html_content}]]></ac:plain-text-body>
</ac:structured-macro>"""
        content.append(wrapped_content)
        
        # Add TOC before child descriptions - set maxLevel to 2
        content.append("""<ac:structured-macro ac:macro-id=\"e28a9a22-7658-4c57-9edb-16f014842ddd\" ac:name=\"toc\" ac:schema-version=\"1\"><ac:parameter ac:name="maxLevel">2</ac:parameter></ac:structured-macro>""")
        
        # Add child descriptions after the layout
        for child in children:
            content.extend([
                f"<h2>{self._escape_html(child['name'])}</h2>",
                f"<p>{self._convert_markdown(child.get('description', ''))}</p>"
            ])
        
        return "\n".join(content)
    
    def _format_capability_with_complex_children(self, capability: Dict[Any, Any], children: list) -> str:
        """Format a capability whose children have their own children."""
        # Generate layout model
        settings = Settings()
        max_level = settings.get("max_level", 6)
        layout_data = {
            "id": capability["id"],
            "name": capability["name"],
            "description": capability.get("description", ""),
            "children": children  # Include children in layout
        }
        layout_model = LayoutModel.convert_to_layout_format(layout_data, max_level)
        
        # Generate HTML layout
        html_content = export_to_html_macro(layout_model, settings)
        wrapped_content = f"""<ac:structured-macro ac:macro-id="128a5fdd-f45d-4300-b6fe-4fc28e6f21b1" ac:name="html" ac:schema-version="1">
 <ac:plain-text-body><![CDATA[{html_content}]]></ac:plain-text-body>
</ac:structured-macro>"""

        return "\n".join([
            f"<h1>{self._escape_html(capability['name'])}</h1>",
            f"<p>{self._convert_markdown(capability.get('description', ''))}</p>",
            wrapped_content,
            "<p>",
            "<ac:structured-macro ac:macro-id=\"16f8e632-2be7-41c7-902a-f2e15c8746a6\" ac:name=\"children\" ac:schema-version=\"2\">",
            "<ac:parameter ac:name=\"excerptType\">simple</ac:parameter>",
            "</ac:structured-macro>",
            "</p>"
        ])
    
    def format_capability_content(self, capability: Dict[Any, Any], children: list = None) -> str:
        """Convert capability data to Confluence storage format based on hierarchy."""
        if not children:
            return self._format_leaf_capability(capability)
        
        # Check if any children have their own children
        has_complex_children = any('children' in child and child['children'] for child in children)
        
        if has_complex_children:
            return self._format_capability_with_complex_children(capability, children)  # Pass children parameter
        else:
            return self._format_capability_with_leaf_children(capability, children)

class ConfluencePublisher:
    """Handles Confluence API interactions."""
    
    def __init__(self, url: str, token: str):
        """Initialize Confluence client."""
        self.confluence = Confluence(
            url=url,
            token=token
        )
        self.logger = logging.getLogger(__name__)
    
    def get_space_home_page(self, space_key: str) -> Optional[Dict[str, Any]]:
        """Get the home page of a space."""
        try:
            space = self.confluence.get_space(space_key)
            if space and 'homepage' in space:
                return space['homepage']
            return None
        except Exception as e:
            self.logger.error(f'Error getting space home page: {e}')
            return None

    def create_or_update_page(
        self,
        space_key: str,
        title: str,
        body: str,
        parent_title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create or update a Confluence page."""
        try:
            # Check if page exists
            existing_page = self.confluence.get_page_by_title(
                space=space_key,
                title=title
            )
            
            # Get parent_id
            parent_id = None
            if parent_title:
                parent_page = self.confluence.get_page_by_title(
                    space=space_key,
                    title=parent_title
                )
                if parent_page:
                    parent_id = parent_page['id']
            else:
                # If no parent_title given, use space home page as parent
                home_page = self.get_space_home_page(space_key)
                if home_page:
                    parent_id = home_page['id']
            
            if existing_page:
                # Update existing page
                result = self.confluence.update_page(
                    page_id=existing_page['id'],
                    title=title,
                    body=body,
                    parent_id=parent_id,
                    type='page',
                    representation='storage'
                )
                self.logger.info(f'Page "{title}" updated successfully')
            else:
                # Create new page
                result = self.confluence.create_page(
                    space=space_key,
                    title=title,
                    body=body,
                    parent_id=parent_id,
                    type='page',
                    representation='storage'
                )
                self.logger.info(f'Page "{title}" created successfully')
            
            return {
                'id': result['id'],
                'title': result['title'],
                'url': f"{self.confluence.url}/pages/viewpage.action?pageId={result['id']}"
            }
        except Exception as e:
            self.logger.error(f'An error occurred: {e}')
            raise

async def count_pages_recursive(capability_data: dict) -> int:
    """Count total number of pages that will be created."""
    count = 1  # Count current capability
    children = capability_data.get('children', [])
    if children and any('children' in child and child['children'] for child in children):
        for child in children:
            count += await count_pages_recursive(child)
    return count

async def publish_capability_to_confluence(
    db_ops: DatabaseOperations,
    capability_id: int,
    space_key: str,
    token: str,
    parent_page_title: Optional[str] = None,
    confluence_url: str = "https://your-domain.atlassian.net",
    current_page: int = 1,
    total_pages: Optional[int] = None
) -> AsyncGenerator[PublishProgress, None]:
    """
    Publish a capability and its children to Confluence, yielding progress.
    
    Args:
        db_ops: Database operations instance
        capability_id: ID of the capability to publish
        space_key: Confluence space key
        token: Confluence API token
        parent_page_title: Optional parent page title in Confluence
        confluence_url: Confluence instance URL
        current_page: Current page number being processed
        total_pages: Total number of pages to be created
        
    Yields:
        PublishProgress objects indicating the progress of publishing
    """
    # Get capability data with children
    capability_data = await db_ops.get_capability_with_children(capability_id)
    if not capability_data:
        yield PublishProgress(
            total_pages=total_pages or 0,
            current_page=current_page,
            page_title="",
            error="Capability not found"
        )
        return

    # Count total pages on first call
    if total_pages is None:
        total_pages = await count_pages_recursive(capability_data)

    # Extract children and format content
    children = capability_data.get('children', [])
    formatter = ConfluenceFormatter()
    content = formatter.format_capability_content(capability_data, children)

    try:
        # Initialize publisher and create/update page
        publisher = ConfluencePublisher(confluence_url, token)
        result = publisher.create_or_update_page(
            space_key=space_key,
            title=capability_data['name'],
            body=content,
            parent_title=parent_page_title
        )

        # Yield success progress
        yield PublishProgress(
            total_pages=total_pages,
            current_page=current_page,
            page_title=capability_data['name'],
            url=result['url']
        )

        # Process children if they have their own children
        if children and any('children' in child and child['children'] for child in children):
            next_page = current_page + 1
            for child in children:
                async for progress in publish_capability_to_confluence(
                    db_ops=db_ops,
                    capability_id=child['id'],
                    space_key=space_key,
                    token=token,
                    parent_page_title=capability_data['name'],
                    confluence_url=confluence_url,
                    current_page=next_page,
                    total_pages=total_pages
                ):
                    yield progress
                    next_page = progress.current_page + 1

    except Exception as e:
        yield PublishProgress(
            total_pages=total_pages,
            current_page=current_page,
            page_title=capability_data['name'],
            error=str(e)
        )

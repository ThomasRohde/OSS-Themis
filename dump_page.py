import json
import os
from typing import Any, Dict

from atlassian import Confluence
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables
CONFLUENCE_URL = os.getenv('CONFLUENCE_URL', 'https://confluence.danskenet.net')
CONFLUENCE_TOKEN = os.getenv('CONFLUENCE_TOKEN', '')
SPACE_KEY = os.getenv('CONFLUENCE_SPACE_KEY', '~thro')

def pretty_print_json(data: Dict[str, Any]) -> None:
    """Print JSON data and HTML content in a readable format using rich"""
    console = Console()
    
    # Extract HTML content before converting to JSON string
    html_content = data.pop('content', '')
    
    # Print JSON data
    json_str = json.dumps(data, indent=2)
    json_syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
    console.print(Panel(json_syntax, title="Page Metadata", border_style="blue"))
    
    # Format and print HTML content
    if (html_content):
        # Parse and prettify HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        formatted_html = soup.prettify()
        print(formatted_html)
        html_syntax = Syntax(formatted_html, "html", theme="monokai", line_numbers=True)
        console.print(Panel(html_syntax, title="Page Content (HTML)", border_style="green"))
    
    # Restore the content field
    data['content'] = html_content

def fetch_confluence_page(page_title: str) -> None:
    """
    Fetch and display a Confluence page content
    
    Args:
        page_title: Title of the page to fetch
    """
    try:
        # Initialize Confluence client
        confluence = Confluence(
            url=CONFLUENCE_URL,
            token=CONFLUENCE_TOKEN
        )

        # Get page content with expanded body
        page = confluence.get_page_by_title(
            space=SPACE_KEY,
            title=page_title,
            expand='body.storage'
        )

        if page:
            print(f"\nPage Found: {page['title']}")
            print("\nPage Details:")
            print("-" * 80)
            pretty_print_json({
                'id': page['id'],
                'title': page['title'],
                'space': SPACE_KEY,
                'url': f"{CONFLUENCE_URL}/pages/viewpage.action?pageId={page['id']}",
                'content': page['body']['storage']['value']
            })
        else:
            print(f"\nNo page found with title '{page_title}' in space {SPACE_KEY}")

    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python test_confluence.py 'Page Title'")
        sys.exit(1)
    
    page_title = sys.argv[1]
    fetch_confluence_page(page_title)
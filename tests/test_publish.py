
import asyncio
import os

from dotenv import load_dotenv

from bcm.confluence_publish import ConfluencePublisher


def convert(text: str) -> str:
    if not text:
        return ''
        
    # Escape special HTML characters
    escaped_text = (
        text.replace('&', 'and')
    )
    
    return escaped_text

def test_simple_publish():
    """Test publishing a simple page to Confluence."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get Confluence credentials from environment variables
    confluence_url = os.getenv('CONFLUENCE_URL')
    token = os.getenv('CONFLUENCE_TOKEN')
    space_key = os.getenv('CONFLUENCE_SPACE')
    
    if not all([confluence_url, token, space_key]):
        raise ValueError("Please set CONFLUENCE_URL, CONFLUENCE_TOKEN, and CONFLUENCE_SPACE environment variables")

    # Create test content with various formatting
    content = """
    <h1>Test Page</h1>
    <p>This is a test page with some & formatted content.</p>
    
    <h2>Formatting Examples</h2>
    <p>Here are some examples of <strong>bold</strong> and <em>italic</em> text.</p>
    
    <h3>Code Block Example</h3>
    <ac:structured-macro ac:name="code" ac:schema-version="1">
        <ac:parameter ac:name="language">python</ac:parameter>
        <ac:plain-text-body><![CDATA[def hello_world():
    print("Hello, Confluence!")]]></ac:plain-text-body>
    </ac:structured-macro>
    
    <h3>Table Example</h3>
    <table>
        <tbody>
            <tr>
                <th>Header 1</th>
                <th>Header 2</th>
            </tr>
            <tr>
                <td>Cell 1</td>
                <td>Cell 2</td>
            </tr>
        </tbody>
    </table>
    
    <h3>List Example</h3>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
    </ul>
    """

    try:
        # Initialize publisher
        publisher = ConfluencePublisher(confluence_url, token)
        
        # Create or update the page
        result = publisher.create_or_update_page(
            space_key=space_key,
            title="Test Page from Python & friends",
            body=convert(content)
        )
        
        print(f"Successfully published page!")
        print(f"Title: {result['title']}")
        print(f"ID: {result['id']}")
        print(f"URL: {result['url']}")
        
    except Exception as e:
        print(f"Error publishing page: {e}")

if __name__ == "__main__":
    test_simple_publish()
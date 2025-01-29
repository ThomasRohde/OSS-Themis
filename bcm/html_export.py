import math
import textwrap  # Add this import at the top
import xml.etree.ElementTree as ET
from typing import List

import markdown  # Changed from markdown2

from bcm.layout_manager import process_layout
from bcm.models import LayoutModel
from bcm.settings import Settings
from bcm.svg_export import add_wrapped_text, calculate_font_size, wrap_text


def create_html_node(node: LayoutModel, level: int = 0) -> str:
    """Create HTML for a node and its children."""
    # Determine node color based on level and whether it has children
    color = "var(--leaf-color)" if not node.children else f"var(--level-{min(level, 6)}-color)"
    
    # Create node HTML with data attributes for hover and position class
    position_class = "has-children" if node.children else "leaf-node"
    node_html = f'''
    <div class="node level-{level} {position_class}" 
         style="left: {node.x}px; top: {node.y}px; width: {node.width}px; height: {node.height}px; background-color: {color};"
         data-description="{node.description or ''}"
         data-name="{node.name}">
        <div class="node-content">{node.name}</div>
    </div>'''

    # Recursively add child nodes
    if node.children:
        for child in node.children:
            node_html += create_html_node(child, level + 1)

    return node_html

def create_html_node_with_styles(node: LayoutModel, level: int = 0) -> str:
    """Create HTML for a node and its children with inline styles."""
    color = "var(--leaf-color)" if not node.children else f"var(--level-{min(level, 6)}-color)"
    position_class = "has-children" if node.children else "leaf-node"
    
    # Base styles for the node
    node_style = (
        f"position: absolute; left: {node.x}px; top: {node.y}px; "
        f"width: {node.width}px; height: {node.height}px; "
        f"background-color: {color}; border: 1px solid #333333; "
        f"border-radius: 5px; overflow: hidden;"
    )
    
    # Content styles based on node type
    content_style = (
        "padding: 8px; font-size: 12px; text-align: center; "
        "word-wrap: break-word; position: absolute; left: 50%; "
        f"{'top: 50%; transform: translate(-50%, -50%);' if not node.children else 'top: 8px; transform: translateX(-50%);'} "
        "width: calc(100% - 16px);"
    )

    node_html = f'''
    <div style="{node_style}"
         data-description="{node.description or ''}"
         data-name="{node.name}">
        <div style="{content_style}">{node.name}</div>
    </div>'''

    if node.children:
        for child in node.children:
            node_html += create_html_node_with_styles(child, level + 1)

    return node_html

def create_html_node_with_styles_no_description(node: LayoutModel, level: int = 0) -> str:
    """Create HTML for a node and its children with inline styles, without descriptions."""
    color = "var(--leaf-color)" if not node.children else f"var(--level-{min(level, 6)}-color)"
    
    # Base styles for the node
    node_style = (
        f"position: absolute; left: {node.x}px; top: {node.y}px; "
        f"width: {node.width}px; height: {node.height}px; "
        f"background-color: {color}; border: 1px solid #333333; "
        f"border-radius: 5px; overflow: hidden;"
    )
    
    # Content styles based on node type
    content_style = (
        "padding: 8px; font-size: 12px; text-align: center; "
        "word-wrap: break-word; position: absolute; left: 50%; "
        f"{'top: 50%; transform: translate(-50%, -50%);' if not node.children else 'top: 8px; transform: translateX(-50%);'} "
        "width: calc(100% - 16px);"
    )

    node_html = f'''
    <div style="{node_style}">
        <div style="{content_style}">{node.name}</div>
    </div>'''

    if node.children:
        for child in node.children:
            node_html += create_html_node_with_styles_no_description(child, level + 1)

    return node_html

def export_to_html(model: LayoutModel, settings: Settings) -> str:
    """Export the capability model to HTML format."""
    # Process layout
    processed_model = process_layout(model, settings)

    # Calculate dimensions with padding
    padding = settings.get("padding", 20)
    width = math.ceil(processed_model.width + 2 * padding)
    height = math.ceil(processed_model.height + 2 * padding)

    # Create CSS variables for colors
    color_vars = ""
    for i in range(7):  # 0-6 levels
        color_vars += f"--level-{i}-color: {settings.get(f'color_{i}', '#ffffff')};\n"
    color_vars += f"--leaf-color: {settings.get('color_leaf', '#ffffff')};\n"

    # Create the HTML content with embedded CSS and JS
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Capability Model</title>
    <style>
        :root {{
            {color_vars}
        }}
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
        }}
        #model-container {{
            position: relative;
            width: {width}px;
            height: {height}px;
        }}
        .node {{
            position: absolute;
            border: 1px solid #333333;
            border-radius: 5px;
            overflow: hidden;
            transition: box-shadow 0.3s ease;
        }}
        .node:hover {{
            box-shadow: 0 0 10px rgba(0,0,0,0.3);
        }}
        .node-content {{
            padding: 8px;
            font-size: {settings.get("root_font_size", 14)}px;
            text-align: center;
            word-wrap: break-word;
            position: absolute;
            left: 50%;
            transform: translateX(-50%);
            width: calc(100% - 16px); /* Account for padding */
        }}
        .leaf-node .node-content {{
            top: 50%;
            transform: translate(-50%, -50%);
        }}
        .has-children .node-content {{
            top: 8px;
            transform: translateX(-50%);
        }}
        #tooltip {{
            position: fixed;
            display: none;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 10px;
            border-radius: 4px;
            max-width: 300px;
            z-index: 1000;
        }}
    </style>
</head>
<body>
    <div id="model-container">
        {create_html_node(processed_model)}
    </div>
    <div id="tooltip"></div>

    <script>
        const tooltip = document.getElementById('tooltip');
        
        document.querySelectorAll('.node').forEach(node => {{
            node.addEventListener('mousemove', (e) => {{
                const description = node.dataset.description;
                if (description) {{
                    tooltip.textContent = `${{node.dataset.name}}: ${{description}}`;
                    tooltip.style.display = 'block';
                    tooltip.style.left = e.pageX + 10 + 'px';
                    tooltip.style.top = e.pageY + 10 + 'px';
                }}
            }});

            node.addEventListener('mouseleave', () => {{
                tooltip.style.display = 'none';
            }});
        }});
    </script>
</body>
</html>'''

    return html_content

def export_to_html_macro(model: LayoutModel, settings: Settings) -> str:
    """Export the capability model to HTML format suitable for Confluence macros."""
    processed_model = process_layout(model, settings)
    width = math.ceil(processed_model.width)
    height = math.ceil(processed_model.height)

    # Create color styles
    styles = f'''
        <style>
            :root {{
                --level-0-color: {settings.get('color_0', '#ffffff')};
                --level-1-color: {settings.get('color_1', '#e6f3ff')};
                --level-2-color: {settings.get('color_2', '#cce7ff')};
                --level-3-color: {settings.get('color_3', '#b3dbff')};
                --level-4-color: {settings.get('color_4', '#99cfff')};
                --level-5-color: {settings.get('color_5', '#80c3ff')};
                --level-6-color: {settings.get('color_6', '#66b7ff')};
                --leaf-color: {settings.get('color_leaf', '#4dacff')};
            }}
        </style>
    '''

    html_content = f'''<div style="margin: 0; padding: 20px; font-family: Arial, sans-serif;">
    {styles}
    <div id="model-container" style="position: relative; width: {width}px; height: {height}px;">
        {create_html_node_with_styles_no_description(processed_model)}
    </div>
</div>'''

    return html_content

def export_to_svg_macro(model: LayoutModel, settings: Settings) -> str:
    """Export the capability model to SVG format suitable for Confluence macros."""
    processed_model = process_layout(model, settings)
    padding = settings.get("padding", 20)
    width = math.ceil(processed_model.width + 2 * padding)
    height = math.ceil(processed_model.height + 2 * padding)
    
    svg = ET.Element(
        "svg",
        {
            "width": str(width),
            "height": str(height),
            "xmlns": "http://www.w3.org/2000/svg",
            "version": "1.1",
        },
    )

    def add_node_to_svg(node: LayoutModel, level: int = 0):
        g = ET.SubElement(svg, "g")
        color = settings.get("color_leaf") if not node.children else settings.get(f"color_{min(level, 6)}")
        
        # Add rectangle
        rect_attrs = {
            "x": str(node.x),
            "y": str(node.y),
            "width": str(node.width),
            "height": str(node.height),
            "fill": color,
            "rx": "5",
            "ry": "5",
            "stroke": "#333333",
            "stroke-width": "1",
        }
        
        if node.description:
            # Convert markdown description to HTML using markdown package
            html_description = markdown.markdown(node.description)
            rect_attrs["data-tippy-content"] = html_description
            
        ET.SubElement(g, "rect", rect_attrs)
        # Add wrapped text with appropriate positioning
        add_wrapped_text(
            g,
            node.name,
            node.x + node.width / 2,  # Center horizontally
            node.y,  # Start from top
            node.height,  # Pass height for vertical centering
            node.width,
            settings.get("root_font_size"),  # Pass base font size
            level,  # Pass level for font size calculation
            has_children=bool(node.children),
        )

        if node.children:
            for child in node.children:
                add_node_to_svg(child, level + 1)

    add_node_to_svg(processed_model)
    svg_string = ET.tostring(svg, encoding="unicode", method="xml")
    
    return f'''<div id="svg-container">
{svg_string}
</div>

<link rel="stylesheet" href="https://unpkg.com/tippy.js@6/dist/tippy.css">
<link rel="stylesheet" href="https://unpkg.com/tippy.js/themes/light.css">
<script src="https://unpkg.com/@popperjs/core@2"></script>
<script src="https://unpkg.com/tippy.js@6"></script>

<script>
    // Initialise Tippy.js within Confluence
    document.addEventListener("DOMContentLoaded", function() {{
        tippy('#svg-container rect', {{
            placement: 'right', // Tooltip position
            maxWidth: '35%',
            allowHTML: true, // Allow HTML content
            theme: 'light', // Light theme
        }});
    }});
</script>'''

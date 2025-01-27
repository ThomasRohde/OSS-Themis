import os
from typing import List, Tuple

from bcm.database import DatabaseOperations

# Maximum size of each markdown file in bytes
MAX_FILE_SIZE = 50000  # 50KB per file

def _format_description(description: str) -> str:
    """Format description text for markdown, handling newlines and quotes."""
    if not description:
        return "_No description provided_"
    
    # Replace newlines with markdown line breaks
    description = description.replace('\n', '  \n')
    return description

async def _process_capability(db_ops: DatabaseOperations, capability: dict, level: int = 0) -> List[str]:
    """Process a capability and its children recursively to generate markdown lines."""
    lines = []
    
    # Add header with proper level
    header_level = '#' * (level + 1)
    lines.append(f"{header_level} {capability['name']}\n")
    
    # Add description if present
    if capability.get('description'):
        desc_lines = _format_description(capability['description']).split('\n')
        lines.extend(f"{line}\n" for line in desc_lines)
        lines.append('\n')
    
    # Process children if present
    children = await db_ops.get_capabilities(capability['id'])
    if children:
        for child in sorted(children, key=lambda x: x.order_position):
            child_dict = {
                'id': child.id,
                'name': child.name,
                'description': child.description,
                'parent_id': child.parent_id
            }
            lines.extend(await _process_capability(db_ops, child_dict, level + 1))
    
    return lines

def _split_content(content: str) -> List[Tuple[str, str]]:
    """Split content into multiple files if it exceeds MAX_FILE_SIZE.
    
    Returns:
        List of tuples containing (filename, content)
    """
    if len(content.encode('utf-8')) <= MAX_FILE_SIZE:
        return [('context.md', content)]
    
    files = []
    current_file = []
    current_size = 0
    file_counter = 1
    
    for line in content.split('\n'):
        line_size = len((line + '\n').encode('utf-8'))
        
        if current_size + line_size > MAX_FILE_SIZE and current_file:
            # Save current file
            files.append((
                f'context-{file_counter}.md',
                '\n'.join(current_file) + '\n'
            ))
            file_counter += 1
            current_file = []
            current_size = 0
        
        current_file.append(line)
        current_size += line_size
    
    # Save remaining content
    if current_file:
        files.append((
            f'context-{file_counter}.md',
            '\n'.join(current_file) + '\n'
        ))
    
    return files

async def export_context(db_ops: DatabaseOperations) -> List[Tuple[str, str]]:
    """Export the entire capability model to markdown files.
    
    Returns:
        List of tuples containing (filename, content)
    """
    # Get root capabilities (those without parent)
    roots = await db_ops.get_capabilities(None)
    
    # Process each root capability
    lines = []
    for root in sorted(roots, key=lambda x: x.order_position):
        root_dict = {
            'id': root.id,
            'name': root.name,
            'description': root.description,
            'parent_id': root.parent_id
        }
        lines.extend(await _process_capability(db_ops, root_dict))
    
    # Join all lines and split into files if needed
    content = ''.join(lines)
    return _split_content(content)

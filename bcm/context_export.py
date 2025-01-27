import os
from typing import List, Tuple

from bcm.database import DatabaseOperations

# Maximum size of each markdown file in bytes
MAX_FILE_SIZE = 600000  # 600KB per file

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

def _find_split_points(content: str, max_size: int) -> List[int]:
    """Find suitable points to split content, preferring headers and keeping content with its header."""
    lines = content.split('\n')
    current_size = 0
    split_points = []
    last_header = -1
    min_chunk_size = max_size * 0.4  # Minimum chunk size (40% of max)
    
    for i, line in enumerate(lines):
        line_size = len((line + '\n').encode('utf-8'))
        current_size += line_size
        
        # Track header positions
        if line.startswith('#'):
            # If we're past min size and have a previous header, we can split at current
            if current_size >= min_chunk_size and last_header >= 0:
                split_points.append(i)
                current_size = line_size
            last_header = i
        
        if current_size > max_size:
            # Find next header position
            next_header = -1
            for j in range(i + 1, len(lines)):
                if lines[j].startswith('#'):
                    next_header = j
                    break
            
            # If next header is close, include content up to it
            if next_header != -1 and (next_header - i) <= 5:  # within 5 lines
                split_points.append(next_header)
                current_size = sum(len((l + '\n').encode('utf-8')) 
                                 for l in lines[next_header:i+1])
            else:
                # Split at last header if we have one
                if last_header > (split_points[-1] if split_points else -1):
                    split_points.append(last_header)
                    current_size = sum(len((l + '\n').encode('utf-8')) 
                                     for l in lines[last_header:i+1])
                else:
                    # Force split at current position
                    split_points.append(i)
                    current_size = line_size
    
    return split_points

def _sanitize_filename(name: str) -> str:
    """Convert a string into a safe filename."""
    # Replace spaces and special characters with underscores
    safe_name = ''.join(c if c.isalnum() else '_' for c in name.lower())
    # Remove consecutive underscores
    safe_name = '_'.join(filter(None, safe_name.split('_')))
    return safe_name

def _split_content(content: str, model_name: str) -> List[Tuple[str, str]]:
    """Split content into multiple files if it exceeds MAX_FILE_SIZE."""
    safe_name = _sanitize_filename(model_name)
    
    if len(content.encode('utf-8')) <= MAX_FILE_SIZE:
        return [(f'{safe_name}.md', content)]
    
    split_points = _find_split_points(content, MAX_FILE_SIZE)
    files = []
    lines = content.split('\n')
    min_last_chunk = MAX_FILE_SIZE * 0.2  # 20% of max size
    
    start = 0
    for i, split_point in enumerate(split_points, 1):
        # If split point is at a header, move split point before the header
        if split_point < len(lines) and lines[split_point].startswith('#'):
            file_content = '\n'.join(lines[start:split_point])
        else:
            file_content = '\n'.join(lines[start:split_point+1])
            split_point += 1
        
        files.append((f'{safe_name}-{i}.md', file_content + '\n'))
        start = split_point
    
    # Handle remaining content
    if start < len(lines):
        last_chunk = '\n'.join(lines[start:])
        if len(last_chunk.encode('utf-8')) < min_last_chunk and files:
            # Merge with previous chunk if too small
            prev_filename, prev_content = files.pop()
            combined_content = prev_content.rstrip() + '\n\n' + last_chunk + '\n'
            files.append((prev_filename, combined_content))
        else:
            files.append((f'{safe_name}-{len(split_points)+1}.md', last_chunk + '\n'))
    
    return files

async def export_context(db_ops: DatabaseOperations) -> List[Tuple[str, str]]:
    """Export the entire capability model to markdown files.
    
    Returns:
        List of tuples containing (filename, content)
    """
    # Get root capabilities (those without parent)
    roots = await db_ops.get_capabilities(None)
    if not roots:
        return []
    
    # Get the first root's name for the filename
    model_name = roots[0].name
    
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
    return _split_content(content, model_name)

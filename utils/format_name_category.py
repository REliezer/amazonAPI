import re
from fastapi import HTTPException

async def format_name_category(category_name):
    """
    Formats a category name by:
    - Converting to lowercase
    - Replacing spaces with underscores
    - Removing special characters (keeping only letters, numbers, and underscores)
    
    Args:
        category_name (str): The category name to format
        
    Returns:
        str: The formatted category name
        
    Raises:
        HTTPException: If category_name is empty or None
    """
    if not category_name:
        raise HTTPException(status_code=400, detail="Category name not found")
    
    # Convert to lowercase and replace spaces with underscores
    formatted_name = category_name.lower().replace(' ', '_')
    
    # Remove special characters, keeping only letters, numbers, and underscores
    formatted_name = re.sub(r'[^a-z0-9_]', '', formatted_name)
    
    # Remove multiple consecutive underscores and strip leading/trailing underscores
    formatted_name = re.sub(r'_+', '_', formatted_name).strip('_')
    
    return formatted_name

import json
import logging

from fastapi import HTTPException

from utils.database import execute_query_json
from models.productscategory import ProductsCategories

logger = logging.getLogger(__name__)

async def get_category_name_by_id(category_id: int) -> str:
    """Get category name by ID"""
    query = "SELECT category_name FROM amazon.categories WHERE id = ?"
    result = await execute_query_json(query, [category_id])
    data = json.loads(result)
    if not data:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return data[0]['category_name']

async def get_count_products_by_category() -> list[dict]:
    """Get all categories with their product count"""
    query = """    
        SELECT c.id AS category_id, c.category_name AS category_name, COUNT(p.asin) AS total_products
        FROM amazon.products p
        JOIN amazon.categories c ON p.category_id = c.id
        GROUP BY c.id, c.category_name
        ORDER BY total_products DESC;
    """
    result = await execute_query_json(query)
    data = json.loads(result)
    if not data:
        raise HTTPException(status_code=404, detail="No categories found")
    
    return data
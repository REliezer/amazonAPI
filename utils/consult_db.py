import json

from fastapi import HTTPException

from utils.database import execute_query_json
from models.productscatalog import ProductsCatalog

async def get_category_name_from_db(category_id):
    #Obtener el nombre de la categoria
    category_query = "SELECT category_name FROM amazon.categories WHERE id = ?"
    category_result = await execute_query_json(category_query, [category_id])
    category_data = json.loads(category_result)
    if not category_data:
        raise HTTPException(status_code=404, detail="Category not found")
    
    category_name = category_data[0]['category_name']

    return category_name

async def get_count_products_by_category():
    category_query = """    
        SELECT c.id AS category_id, c.category_name AS category_name, COUNT(p.asin) AS total_products
        FROM amazon.products p
        JOIN amazon.categories c ON p.category_id = c.id
        GROUP BY c.id, c.category_name
        ORDER BY total_products DESC;
    """
    category_result = await execute_query_json(category_query)
    category_data = json.loads(category_result)
    if not category_data:
        raise HTTPException(status_code=404, detail="No categories found")
    
    return category_data
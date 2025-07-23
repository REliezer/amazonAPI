import os
import json
import logging
import firebase_admin
import requests

from fastapi import HTTPException
from firebase_admin import credentials, auth as firebase_auth
from dotenv import load_dotenv

from utils.database import execute_query_json
from utils.security import create_jwt_token
from utils.keyvault import get_secret_by_name

from models.userregister import UserRegister
from models.userlogin import UserLogin

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar la app de Firebase Admin usando secret de Key Vault
async def initialize_firebase_admin():
    """Initialize Firebase Admin SDK using credentials from Azure Key Vault"""
    try:
        # Verificar si ya está inicializada
        if firebase_admin._apps:
            logger.info("Firebase Admin ya está inicializada")
            return
            
        # Obtener las credenciales de Firebase desde Key Vault
        firebase_credentials_json = await get_secret_by_name("firebase-secret")
        
        # Convertir el JSON string a un diccionario
        firebase_credentials = json.loads(firebase_credentials_json)
        
        # Crear las credenciales usando el diccionario
        cred = credentials.Certificate(firebase_credentials)
        
        # Inicializar Firebase Admin
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin inicializada exitosamente desde Key Vault")
        
    except Exception as e:
        logger.error(f"Error al inicializar Firebase Admin: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al inicializar Firebase Admin: {e}"
        )

load_dotenv()

async def register_user_firebase(user: UserRegister) -> dict:
    await initialize_firebase_admin()

    user_record = {}
    try:
        user_record = firebase_auth.create_user(
            email=user.email,
            password=user.password
        )

    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Error al registrar usuario: {e}"
        )

    query = f" exec amazon.users_insert ?, ?, ?, ?, ? "
    params = (
        user_record.email,
        user.firstName,
        user.lastName,
        user.active,
        user.admin
    )
    try:
        result_json = await execute_query_json(query, params, needs_commit=True)
        return json.loads(result_json)
    except Exception as e:
        firebase_auth.delete_user(user_record.uid)
        raise HTTPException(status_code=500, detail=str(e))


async def login_user_firebase(user: UserLogin):
    await initialize_firebase_admin()
    
    # Autenticar usuario con Firebase Authentication usando la API REST
    api_key = await get_secret_by_name("firebase-api-key")
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": user.email,
        "password": user.password,
        "returnSecureToken": True
    }
    response = requests.post(url, json=payload)
    response_data = response.json()

    if "error" in response_data:
        raise HTTPException(
            status_code=400,
            detail=f"Error al autenticar usuario: {response_data['error']['message']}"
        )

    query = f"""select
                    email
                    , firstName
                    , lastName
                    , active
                    , [admin]
                from [amazon].[users]
                where email = ?
                """

    try:
        result_json = await execute_query_json(query, (user.email,), needs_commit=False)
        result_dict = json.loads(result_json)
        jwt_token = await create_jwt_token(
            result_dict[0]["firstName"],
            result_dict[0]["lastName"],
            user.email,
            result_dict[0]["active"],
            result_dict[0]["admin"],
        )
        return {
            "message": "Usuario autenticado exitosamente",
            "idToken": jwt_token
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
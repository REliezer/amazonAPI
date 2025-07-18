from dotenv import load_dotenv
import os
import logging

from fastapi import HTTPException

from azure.core.exceptions import AzureError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def get_client_keyvault():
    try:
        key_vault_url = os.getenv('KEY_VAULT_URL')

        logger.info(f"Intentando conectar al key vault...")        
        # Automatically uses Managed Identity (Azure) or Azure CLI/MSAL (local)
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=key_vault_url, credential=credential)
        
        logger.info(f"Conexión exitosa al Key Vault.")
        return client
    except AzureError as e:
        logger.error(f"Failed to connect key vault: {e}")
        raise HTTPException(status_code=500, detail=f"Key Vault connection failed: {str(e)}")

async def get_secret_by_name(secret_name):
    if not secret_name:
        raise HTTPException(status_code=400, detail="Secret name not found")
    
    try:
        client = await get_client_keyvault()
        secret = client.get_secret(secret_name)
        logger.info(f"Secret '{secret_name}' retrieved successfully")
        return secret.value
    except AzureError as e:
        logger.error(f"Failed to retrieve secret '{secret_name}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve secret: {str(e)}")

import os
import jwt

from datetime import datetime, timedelta
from fastapi import HTTPException
from dotenv import load_dotenv
from jwt import PyJWTError
from functools import wraps

from utils.keyvault import get_secret_by_name

load_dotenv()

#SECRET_KEY = os.getenv("SECRET_KEY")

# Función para crear un JWT
async def create_jwt_token(firstName:str, lastName:str, email: str, active: bool, admin: bool):
    secret_key = await get_secret_by_name("jwt-secret-key")
    expiration = datetime.utcnow() + timedelta(hours=1)  # El token expira en 1 hora
    token = jwt.encode(
        {
            "firstName": firstName,
            "lastName": lastName,
            "email": email,
            "active": active,
            "admin": admin,
            "exp": expiration,
            "iat": datetime.utcnow()
        },
        secret_key,
        algorithm="HS256"
    )
    return token

def validate(func):
    @wraps(func)
    async def wrapper( *args, **kwargs ):
        request = kwargs.get('request')
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found" )

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=400, detail="Authorization header missing" )

        schema, token = authorization.split()
        if schema.lower() != "bearer":
            raise HTTPException(status_code=400, detail="Invalid auth schema" )


        try:
            secret_key = await get_secret_by_name("jwt-secret-key")
            payload = jwt.decode( token , secret_key , algorithms=["HS256"] )
            email = payload.get("email")
            firstName = payload.get("firstName")
            lastName = payload.get("lastName")
            active = payload.get("active")
            exp = payload.get("exp")

            if email is None or exp is None or active is None:
                raise HTTPException(status_code=400, detail="Invalid token 3" )

            if datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException( status_code=401, detail="Expired token" )

            if not active:
                raise HTTPException( status_code=403, detail="Inactive user" )

            request.state.email = email
            request.state.firstName = firstName
            request.state.lastName = lastName

        except PyJWTError:
            raise HTTPException( status_code=401 , detail="Invalid token or expired token" )

        return await func( *args, **kwargs )
    return wrapper

def validateadmin(func):
    @wraps(func)
    async def wrapper( *args, **kwargs ):
        request = kwargs.get('request')
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found" )

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=400, detail="Authorization header missing" )

        schema, token = authorization.split()
        if schema.lower() != "bearer":
            raise HTTPException(status_code=400, detail="Invalid auth schema" )


        try:
            secret_key = await get_secret_by_name("jwt-secret-key")
            payload = jwt.decode( token , secret_key , algorithms=["HS256"] )
            email = payload.get("email")
            firstName = payload.get("firstName")
            lastName = payload.get("lastName")
            active = payload.get("active")
            admin = payload.get("admin")
            exp = payload.get("exp")

            if email is None or exp is None or active is None:
                raise HTTPException(status_code=400, detail="Invalid token 3" )

            if datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException( status_code=401, detail="Expired token" )

            if not active:
                raise HTTPException( status_code=403, detail="Inactive user" )

            if not admin:
                raise HTTPException( status_code=403, detail="Not Admin!" )

            request.state.email = email
            request.state.firstName = firstName
            request.state.lastName = lastName

        except PyJWTError:
            raise HTTPException( status_code=401 , detail="Invalid token or expired token" )

        return await func( *args, **kwargs )
    return wrapper




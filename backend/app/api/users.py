from motor.motor_asyncio import AsyncIOMotorClient
from jose import jwt
from passlib.context import CryptContext
from email_validator import validate_email, EmailNotValidError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user_payload(name: str, email: str, password:str) -> dict:
    #Validación básica 
    name = (name or "").strip() 
    if not name:
        raise ValueError("El nombre es obligatorio")
    if not password or len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")
 
    #Validacíon del email
    try:
        #Validamos la entrada del mail y lo normalizamos
        valid = validate_email(email, check_deliverability=False)
        email = valid.email
    except EmailNotValidError as e:
        raise ValueError("Email no válido: " + str(e))

    #Encriptamos la contraseña con bcrypt
    password_hasheada = pwd_context.hash(password)

    return {
        "name": name,
        "email": email,
        "password": password_hasheada
    }


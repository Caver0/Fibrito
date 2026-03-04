from motor.motor_asyncio import AsyncIOMotorClient
from jose import jwt
from passlib.context import CryptContext
from email_validator import validate_email, EmailNotValidError
from app.models.domain.usuario import Usuario

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
user_counter = 0


def create_user_payload(name: str, email: str, password: str) -> Usuario:
    global user_counter

    # Validación básica
    name = (name or "").strip()
    if not name:
        raise ValueError("El nombre es obligatorio")
    if not password or len(password) < 8:
        raise ValueError("La contraseña debe tener al menos 8 caracteres")

    # Validación del email
    try:
        # Validamos la entrada del email y la normalizamos
        valid = validate_email(email, check_deliverability=False)
        email = valid.email
    except EmailNotValidError as e:
        raise ValueError("Email no válido: " + str(e))

    # Encriptamos la contraseña con bcrypt
    password_hasheada = pwd_context.hash(password)

    user_counter += 1

    return Usuario(
        id_usuario=user_counter,
        name=name,
        email=email,
        password=password_hasheada,
        preferencias=[],
        alergias=[],
        celiaco=False,
    )

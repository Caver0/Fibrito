from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel
import bcrypt
from email_validator import validate_email, EmailNotValidError

from app.models.domain.usuario import Usuario

router = APIRouter()
user_counter = 0


class RegisterUserRequest(BaseModel):
    name: str
    email: str
    password: str


def create_user_payload(name: str, email: str, password: str) -> Usuario:
    global user_counter

    name = (name or "").strip()
    if not name:
        raise ValueError("El nombre es obligatorio")
    if not password or len(password) < 8:
        raise ValueError("La contrasena debe tener al menos 8 caracteres")
    if len(password.encode("utf-8")) > 72:
        raise ValueError("La contrasena no puede superar 72 bytes")

    try:
        valid = validate_email(email, check_deliverability=False)
        email = valid.email
    except EmailNotValidError as e:
        raise ValueError("Email no valido: " + str(e))

    password_hasheada = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(),
    ).decode("utf-8")
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


@router.post("/api/users/register", status_code=status.HTTP_201_CREATED)
async def register_user(payload: RegisterUserRequest, request: Request) -> dict:
    db = request.app.state.db

    try:
        normalized_email = validate_email(payload.email, check_deliverability=False).email
    except EmailNotValidError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Email no valido: {e}",
        ) from e

    existing_user = await db["users"].find_one({"email": normalized_email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con ese email",
        )

    try:
        user = create_user_payload(payload.name, normalized_email, payload.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e

    user_doc = user.get()
    await db["users"].insert_one(user_doc)

    user_doc.pop("password", None)
    user_doc.pop("_id", None)
    return {"message": "Usuario creado correctamente", "user": user_doc}

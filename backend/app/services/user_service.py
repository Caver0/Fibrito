from __future__ import annotations

from enum import Enum
from typing import Any

from bson import ObjectId
from email_validator import EmailNotValidError, validate_email
from pymongo import ReturnDocument
from pymongo.errors import DuplicateKeyError

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.domain.usuario import Usuario


class InvalidUserDataError(ValueError):
    pass


class DuplicateUserError(ValueError):
    pass


class AuthenticationError(ValueError):
    pass


class UserNotFoundError(ValueError):
    pass


LIST_FIELDS = {"preferencias", "alergias", "restricciones_dieteticas"}
OPTIONAL_TEXT_FIELDS = {"sexo", "objetivo", "actividad_fisica"}


def _model_to_dict(model: Any, **kwargs) -> dict[str, Any]:
    if hasattr(model, "model_dump"):
        return model.model_dump(**kwargs)
    return model.dict(**kwargs)


def _normalize_email(email: str) -> str:
    try:
        return validate_email(email, check_deliverability=False).email
    except EmailNotValidError as exc:
        raise InvalidUserDataError(f"Email no valido: {exc}") from exc


def _validate_password(password: str) -> None:
    if not isinstance(password, str):
        raise InvalidUserDataError("La contrasena debe ser una cadena de texto")
    if not password or len(password) < 8:
        raise InvalidUserDataError("La contrasena debe tener al menos 8 caracteres")
    if len(password) > 72:
        raise InvalidUserDataError("La contrasena no puede superar 72 caracteres")
    if len(password.encode("utf-8")) > 72:
        raise InvalidUserDataError("La contrasena no puede superar 72 bytes")


def _clean_required_text(value: str, field_name: str) -> str:
    cleaned = (value or "").strip()
    if not cleaned:
        raise InvalidUserDataError(f"El campo {field_name} es obligatorio")
    return cleaned


def _validate_required_profile_fields(data: dict[str, Any]) -> None:
    required_fields = (
        "edad",
        "sexo",
        "peso",
        "altura",
        "numero_comidas",
    )
    for field_name in required_fields:
        if data.get(field_name) is None:
            raise InvalidUserDataError(f"El campo {field_name} es obligatorio")


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _clean_string_list(values: list[str] | None) -> list[str]:
    if values is None:
        return []
    cleaned_values: list[str] = []
    for value in values:
        cleaned = _clean_optional_text(_stringify_choice(value))
        if cleaned:
            cleaned_values.append(cleaned)
    return cleaned_values


def _stringify_choice(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, str):
        return value
    raise InvalidUserDataError("Se ha recibido un valor no valido en el perfil del usuario")


def serialize_user(user_document: dict[str, Any]) -> dict[str, Any]:
    return Usuario.from_document(user_document).to_public_dict()


async def get_user_by_email(db, email: str) -> dict[str, Any] | None:
    return await db["users"].find_one({"email": email})


async def get_user_by_id(db, user_id: ObjectId) -> dict[str, Any] | None:
    return await db["users"].find_one({"_id": user_id})


def _build_user_from_registration(payload) -> Usuario:
    data = _model_to_dict(payload, exclude_unset=True)
    _validate_required_profile_fields(data)
    password = data.get("password")
    _validate_password(password)

    try:
        password_hash = get_password_hash(password)
    except ValueError as exc:
        raise InvalidUserDataError(str(exc)) from exc

    return Usuario(
        name=_clean_required_text(data["name"], "name"),
        email=_normalize_email(data["email"]),
        password=password_hash,
        preferencias=_clean_string_list(data.get("preferencias")),
        alergias=_clean_string_list(data.get("alergias")),
        celiaco=data.get("celiaco", False),
        edad=data.get("edad"),
        sexo=_clean_optional_text(data.get("sexo")),
        peso=data.get("peso"),
        altura=data.get("altura"),
        objetivo=_clean_optional_text(data.get("objetivo")),
        actividad_fisica=_clean_optional_text(_stringify_choice(data.get("actividad_fisica"))),
        calorias_objetivo=None,
        numero_comidas=data.get("numero_comidas"),
        restricciones_dieteticas=_clean_string_list(
            data.get("restricciones_dieteticas"),
        ),
    )


async def create_user(db, payload) -> dict[str, Any]:
    user = _build_user_from_registration(payload)

    existing_user = await get_user_by_email(db, user.email)
    if existing_user is not None:
        raise DuplicateUserError("Ya existe un usuario con ese email")

    try:
        result = await db["users"].insert_one(user.to_document())
    except DuplicateKeyError as exc:
        raise DuplicateUserError("Ya existe un usuario con ese email") from exc

    created_user = await get_user_by_id(db, result.inserted_id)
    if created_user is None:
        raise UserNotFoundError("No se ha podido recuperar el usuario creado")

    return serialize_user(created_user)


async def authenticate_user(db, email: str, password: str) -> dict[str, Any]:
    normalized_email = _normalize_email(email)
    user = await get_user_by_email(db, normalized_email)

    if user is None or not verify_password(password, user["password"]):
        raise AuthenticationError("Email o contrasena incorrectos")

    return {
        "access_token": create_access_token(str(user["_id"])),
        "token_type": "bearer",
        "user": serialize_user(user),
    }


def _prepare_update_data(payload) -> dict[str, Any]:
    update_data = _model_to_dict(payload, exclude_unset=True)

    for field in LIST_FIELDS:
        if field in update_data:
            update_data[field] = _clean_string_list(update_data[field])

    if "name" in update_data:
        update_data["name"] = _clean_required_text(update_data["name"], "name")

    for field in OPTIONAL_TEXT_FIELDS:
        if field in update_data:
            update_data[field] = _clean_optional_text(_stringify_choice(update_data[field]))

    return update_data


async def update_user(db, user_id: ObjectId, payload) -> dict[str, Any]:
    update_data = _prepare_update_data(payload)

    if not update_data:
        user = await get_user_by_id(db, user_id)
        if user is None:
            raise UserNotFoundError("Usuario no encontrado")
        return serialize_user(user)

    updated_user = await db["users"].find_one_and_update(
        {"_id": user_id},
        {"$set": update_data},
        return_document=ReturnDocument.AFTER,
    )

    if updated_user is None:
        raise UserNotFoundError("Usuario no encontrado")

    return serialize_user(updated_user)


async def delete_user(db, user_id: ObjectId) -> None:
    # Se usa borrado fisico para mantener el modelo simple y consistente en todo el TFG.
    result = await db["users"].delete_one({"_id": user_id})
    if result.deleted_count == 0:
        raise UserNotFoundError("Usuario no encontrado")

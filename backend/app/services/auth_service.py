from bson import ObjectId
from bson.errors import InvalidId
from fastapi import Depends, HTTPException, Request, status
from jose import JWTError

from app.core.security import decode_access_token, oauth2_scheme


async def get_database(request: Request):
    return request.app.state.db


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db=Depends(get_database),
) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se ha podido validar el token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        subject = payload.get("sub")
        if not subject:
            raise credentials_exception
        user_id = ObjectId(subject)
    except (JWTError, InvalidId) as exc:
        raise credentials_exception from exc

    user = await db["users"].find_one({"_id": user_id})
    if user is None:
        raise credentials_exception

    return user

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.models.schemas.user import (
    LoginResponse,
    MessageResponse,
    UserCreateRequest,
    UserLoginRequest,
    UserUpdateRequest,
    UserWithMessageResponse,
    UserPublic,
)
from app.services.auth_service import get_current_user
from app.services.user_service import (
    AuthenticationError,
    DuplicateUserError,
    InvalidUserDataError,
    UserNotFoundError,
    authenticate_user,
    create_user,
    delete_user,
    serialize_user,
    update_user,
)

router = APIRouter(tags=["users"])


@router.post(
    "/api/users/register",
    response_model=UserWithMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(payload: UserCreateRequest, request: Request) -> UserWithMessageResponse:
    db = request.app.state.db

    try:
        created_user = await create_user(db, payload)
    except DuplicateUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except InvalidUserDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return UserWithMessageResponse(
        message="Usuario creado correctamente",
        user=UserPublic(**created_user),
    )


@router.post(
    "/api/users/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
async def login_user(payload: UserLoginRequest, request: Request) -> LoginResponse:
    db = request.app.state.db

    try:
        login_response = await authenticate_user(db, payload.email, payload.password)
    except AuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    except InvalidUserDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return LoginResponse(**login_response)


@router.get(
    "/api/users/me",
    response_model=UserPublic,
    status_code=status.HTTP_200_OK,
)
async def read_current_user(current_user: dict = Depends(get_current_user)) -> UserPublic:
    return UserPublic(**serialize_user(current_user))


@router.put(
    "/api/users/me",
    response_model=UserPublic,
    status_code=status.HTTP_200_OK,
)
async def update_current_user(
    payload: UserUpdateRequest,
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> UserPublic:
    db = request.app.state.db

    try:
        updated_user = await update_user(db, current_user["_id"], payload)
    except InvalidUserDataError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return UserPublic(**updated_user)


@router.delete(
    "/api/users/me",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_current_user(
    request: Request,
    current_user: dict = Depends(get_current_user),
) -> MessageResponse:
    db = request.app.state.db

    try:
        await delete_user(db, current_user["_id"])
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    return MessageResponse(message="Usuario eliminado correctamente")

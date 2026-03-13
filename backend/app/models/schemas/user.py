from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class SchemaBase(BaseModel):
    class Config:
        extra = "forbid"


class ActividadFisica(str, Enum):
    sedentaria = "sedentaria"
    ligera = "ligera"
    moderada = "moderada"
    alta = "alta"
    muy_alta = "muy_alta"


class ObjetivoUsuario(str, Enum):
    ganar_peso = "ganar_peso"
    bajar_peso = "bajar_peso"
    mantener_peso = "mantener_peso"
    dieta_saludable = "dieta_saludable"


class RestriccionDietetica(str, Enum):
    sin_gluten = "sin_gluten"
    sin_lactosa = "sin_lactosa"
    vegetariana = "vegetariana"
    vegana = "vegana"


class UserProfileBase(SchemaBase):
    preferencias: list[str] = Field(
        default_factory=list,
        description="Alimentos que el usuario quiere incluir expresamente en su dieta.",
    )
    alergias: list[str] = Field(default_factory=list)
    celiaco: bool = False
    edad: Optional[int] = Field(default=None, ge=0)
    sexo: Optional[str] = Field(default=None, min_length=1, max_length=30)
    peso: Optional[float] = Field(default=None, gt=0)
    altura: Optional[float] = Field(default=None, gt=0)
    objetivo: Optional[ObjetivoUsuario] = Field(
        default=None,
        description="Objetivo principal del usuario dentro de la aplicacion.",
    )
    actividad_fisica: Optional[ActividadFisica] = Field(
        default=None,
        description="Nivel de actividad fisica del usuario.",
    )
    calorias_objetivo: Optional[int] = Field(default=None, ge=0)
    numero_comidas: Optional[int] = Field(default=None, gt=0)
    restricciones_dieteticas: list[RestriccionDietetica] = Field(
        default_factory=list,
        description="Restricciones dieteticas seleccionables entre un conjunto cerrado.",
    )


class UserCreateRequest(UserProfileBase):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)
    edad: int = Field(..., ge=0)
    sexo: str = Field(..., min_length=1, max_length=30)
    peso: float = Field(..., gt=0)
    altura: float = Field(..., gt=0)
    numero_comidas: int = Field(..., gt=0)


class UserLoginRequest(SchemaBase):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72)


class UserUpdateRequest(SchemaBase):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    preferencias: Optional[list[str]] = None
    alergias: Optional[list[str]] = None
    celiaco: Optional[bool] = None
    edad: Optional[int] = Field(default=None, ge=0)
    sexo: Optional[str] = Field(default=None, min_length=1, max_length=30)
    peso: Optional[float] = Field(default=None, gt=0)
    altura: Optional[float] = Field(default=None, gt=0)
    objetivo: Optional[ObjetivoUsuario] = None
    actividad_fisica: Optional[ActividadFisica] = None
    calorias_objetivo: Optional[int] = Field(default=None, ge=0)
    numero_comidas: Optional[int] = Field(default=None, gt=0)
    restricciones_dieteticas: Optional[list[RestriccionDietetica]] = None


class UserPublic(UserProfileBase):
    id: str
    name: str
    email: EmailStr


class UserWithMessageResponse(SchemaBase):
    message: str
    user: UserPublic


class LoginResponse(SchemaBase):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class MessageResponse(SchemaBase):
    message: str

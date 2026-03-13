from __future__ import annotations

from typing import Any


class Usuario:
    def __init__(
        self,
        name: str,
        email: str,
        password: str,
        preferencias: list[str] | None = None,
        alergias: list[str] | None = None,
        celiaco: bool = False,
        edad: int | None = None,
        sexo: str | None = None,
        peso: float | None = None,
        altura: float | None = None,
        objetivo: str | None = None,
        actividad_fisica: str | None = None,
        calorias_objetivo: int | None = None,
        numero_comidas: int | None = None,
        restricciones_dieteticas: list[str] | None = None,
        mongo_id: Any | None = None,
    ) -> None:
        self.mongo_id = mongo_id
        self.name = name
        self.email = email
        self.password = password
        self.preferencias = list(preferencias) if preferencias is not None else []
        self.alergias = list(alergias) if alergias is not None else []
        self.celiaco = celiaco
        self.edad = edad
        self.sexo = sexo
        self.peso = peso
        self.altura = altura
        self.objetivo = objetivo
        self.actividad_fisica = actividad_fisica
        self.calorias_objetivo = calorias_objetivo
        self.numero_comidas = numero_comidas
        self.restricciones_dieteticas = (
            list(restricciones_dieteticas)
            if restricciones_dieteticas is not None
            else []
        )

    @classmethod
    def from_document(cls, document: dict[str, Any]) -> "Usuario":
        return cls(
            mongo_id=document.get("_id"),
            name=document["name"],
            email=document["email"],
            password=document["password"],
            preferencias=document.get("preferencias"),
            alergias=document.get("alergias"),
            celiaco=document.get("celiaco", False),
            edad=document.get("edad"),
            sexo=document.get("sexo"),
            peso=document.get("peso"),
            altura=document.get("altura"),
            objetivo=document.get("objetivo"),
            actividad_fisica=document.get("actividad_fisica"),
            calorias_objetivo=document.get("calorias_objetivo"),
            numero_comidas=document.get("numero_comidas"),
            restricciones_dieteticas=document.get("restricciones_dieteticas"),
        )

    def to_document(self) -> dict[str, Any]:
        document = {
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "preferencias": self.preferencias,
            "alergias": self.alergias,
            "celiaco": self.celiaco,
            "edad": self.edad,
            "sexo": self.sexo,
            "peso": self.peso,
            "altura": self.altura,
            "objetivo": self.objetivo,
            "actividad_fisica": self.actividad_fisica,
            "calorias_objetivo": self.calorias_objetivo,
            "numero_comidas": self.numero_comidas,
            "restricciones_dieteticas": self.restricciones_dieteticas,
        }
        if self.mongo_id is not None:
            document["_id"] = self.mongo_id
        return document

    def to_public_dict(self) -> dict[str, Any]:
        data = self.to_document()
        data.pop("password", None)
        mongo_id = data.pop("_id", None)
        data["id"] = str(mongo_id) if mongo_id is not None else None
        return data

from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path

import requests

from app.models.domain.alimento import Alimento

SPOONACULAR_BASE_URL = "https://api.spoonacular.com/food/ingredients"
DEFAULT_AMOUNT = 100
DEFAULT_UNIT = "grams"

_GLUTEN_TERMS = (
    "wheat",
    "barley",
    "rye",
    "triticale",
    "spelt",
    "malt",
    "semolina",
    "farina",
)


class SpoonacularError(Exception):
    """Error de integracion con Spoonacular."""


def _load_env_file_if_needed() -> None:
    if os.getenv("SPOONACULAR_API_KEY"):
        return

    current = Path(__file__).resolve()
    env_candidates = (
        current.parents[3] / ".env",  # raiz del repo
        current.parents[2] / ".env",  # carpeta backend
    )

    for env_path in env_candidates:
        if not env_path.exists():
            continue

        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            if key.startswith("export "):
                key = key.removeprefix("export ").strip()
            if not key:
                continue

            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)

        if os.getenv("SPOONACULAR_API_KEY"):
            return


def _to_float(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _nutrients_index(ingredient_payload: dict) -> dict[str, float]:
    nutrients = ingredient_payload.get("nutrition", {}).get("nutrients", [])
    index: dict[str, float] = {}

    if not isinstance(nutrients, list):
        return index

    for nutrient in nutrients:
        if not isinstance(nutrient, dict):
            continue
        name = str(nutrient.get("name", "")).strip().lower()
        if not name:
            continue
        index[name] = _to_float(nutrient.get("amount", 0.0))

    return index


def _infer_celiac_safe(ingredient_payload: dict) -> bool:
    searchable_text = " ".join(
        str(ingredient_payload.get(field, ""))
        for field in ("name", "nameClean", "original")
    ).lower()
    return not any(term in searchable_text for term in _GLUTEN_TERMS)


def ingrediente_a_alimento(
    ingredient_payload: dict,
    id_alimento: int | None = None,
) -> Alimento:
    nutrients = _nutrients_index(ingredient_payload)

    resolved_id = id_alimento if id_alimento is not None else ingredient_payload.get("id")
    if resolved_id is None:
        raise ValueError("No se puede crear Alimento sin id_alimento")
    nombre = str(
        ingredient_payload.get("nameClean")
        or ingredient_payload.get("name")
        or f"ingrediente-{resolved_id}"
    ).strip()

    return Alimento(
        id_alimento=int(resolved_id),
        nombre=nombre,
        calorias=nutrients.get("calories", 0.0),
        carbohidratos=nutrients.get("carbohydrates", 0.0),
        proteinas=nutrients.get("protein", 0.0),
        grasas=nutrients.get("fat", 0.0),
        azucar=nutrients.get("sugar", 0.0),
        fibra=nutrients.get("fiber", 0.0),
        celiaco=_infer_celiac_safe(ingredient_payload),
    )


def obtener_ingrediente_spoonacular(
    ingredient_id: int,
    api_key: str | None = None,
    amount: float = DEFAULT_AMOUNT,
    unit: str = DEFAULT_UNIT,
    timeout: int = 15,
) -> dict:
    _load_env_file_if_needed()
    key = api_key or os.getenv("SPOONACULAR_API_KEY")
    if not key:
        raise ValueError("Debes definir SPOONACULAR_API_KEY en variables de entorno")

    url = f"{SPOONACULAR_BASE_URL}/{ingredient_id}/information"
    params = {"amount": amount, "unit": unit, "apiKey": key}

    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise SpoonacularError(
            f"No se pudo obtener el ingrediente {ingredient_id} de Spoonacular"
        ) from exc

    payload = response.json()
    if not isinstance(payload, dict):
        raise SpoonacularError("Respuesta invalida de Spoonacular")
    return payload


def obtener_alimento_desde_spoonacular(
    ingredient_id: int,
    api_key: str | None = None,
    amount: float = DEFAULT_AMOUNT,
    unit: str = DEFAULT_UNIT,
) -> Alimento:
    ingredient_payload = obtener_ingrediente_spoonacular(
        ingredient_id=ingredient_id,
        api_key=api_key,
        amount=amount,
        unit=unit,
    )
    return ingrediente_a_alimento(ingredient_payload, id_alimento=ingredient_id)


def obtener_alimentos_desde_spoonacular(
    ingredient_ids: Iterable[int],
    api_key: str | None = None,
    amount: float = DEFAULT_AMOUNT,
    unit: str = DEFAULT_UNIT,
) -> list[Alimento]:
    alimentos: list[Alimento] = []
    for ingredient_id in ingredient_ids:
        try:
            alimento = obtener_alimento_desde_spoonacular(
                ingredient_id=ingredient_id,
                api_key=api_key,
                amount=amount,
                unit=unit,
            )
            alimentos.append(alimento)
        except SpoonacularError as exc:
            raise SpoonacularError(
                f"Error procesando el ingrediente {ingredient_id}"
            ) from exc

    return alimentos

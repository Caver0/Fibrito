import argparse
import json
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    # Permite ejecutar el script por ruta desde la raiz del repositorio.
    backend_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(backend_root))

from app.services.spoonacular_alimentos import (
    SpoonacularError,
    obtener_alimentos_desde_spoonacular,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prueba de extraccion de nutrientes desde Spoonacular"
    )
    parser.add_argument(
        "--ingredient-id",
        type=int,
        action="append",
        dest="ingredient_ids",
        required=True,
        help="ID de ingrediente en Spoonacular. Puedes pasar varios usando --ingredient-id varias veces.",
    )
    parser.add_argument(
        "--amount",
        type=float,
        default=100,
        help="Cantidad para calcular nutrientes (por defecto 100).",
    )
    parser.add_argument(
        "--unit",
        type=str,
        default="grams",
        help="Unidad de la cantidad (por defecto grams).",
    )
    parser.add_argument(
        "--api-key",
        type=str,
        default=None,
        help="API key opcional. Si no se pasa, usa SPOONACULAR_API_KEY.",
    )

    args = parser.parse_args()

    try:
        alimentos = obtener_alimentos_desde_spoonacular(
            ingredient_ids=args.ingredient_ids,
            api_key=args.api_key,
            amount=args.amount,
            unit=args.unit,
        )
    except (SpoonacularError, ValueError) as exc:
        raise SystemExit(f"Error: {exc}") from exc

    print(
        json.dumps(
            [alimento.get() for alimento in alimentos],
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()

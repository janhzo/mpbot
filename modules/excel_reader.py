"""
Módulo para lectura de datos de Excel (o MySQL en el futuro).
Devuelve lista de diccionarios normalizados y limpios.
"""

import pandas as pd
from config import EXCEL_PATH, DEMO_LIMIT
from modules.utils import log
import numpy as np

def read_opportunities(limit: int = DEMO_LIMIT) -> list[dict]:
    """
    Lee el Excel de compras ágiles y devuelve oportunidades limpias.

    Args:
        limit (int): Máximo de filas (demo). None = todas.

    Returns:
        list[dict]: Oportunidades con campos:
            - descripcion: str
            - monto: float
            - titulo: str
            - plazo: str
            - etc.
    """
    log(f"Leyendo Excel: {EXCEL_PATH}", "ExcelReader")

    if not EXCEL_PATH.exists():
        log(f"ERROR: Archivo no encontrado: {EXCEL_PATH}", "ExcelReader")
        return []

    try:
        # Leer Excel
        df = pd.read_excel(EXCEL_PATH)
        log(f"{len(df)} filas leídas del Excel.", "ExcelReader")

        # Aplicar límite
        if limit and limit > 0:
            df = df.head(limit)
            log(f"Límite aplicado: {limit} filas.", "ExcelReader")

        # Limpiar columnas
        df.columns = [
            c.strip().lower().replace(" ", "_").replace("á", "a").replace("é", "e")
            for c in df.columns
        ]

        # Reemplazar NaN
        df = df.replace({np.nan: None})

        # Convertir a registros
        records = df.to_dict(orient="records")

        # Normalizar campos clave
        normalized = []
        for r in records:
            opp = {
                "titulo": str(r.get("titulo", r.get("nombre", "Sin título"))).strip(),
                "descripcion": str(
                    r.get("descripcion", r.get("detalle", r.get("objeto", "")))
                ).strip(),
                "monto": _parse_monto(r.get("monto", r.get("monto_disponible", 0))),
                "plazo": str(r.get("plazo", r.get("fecha_cierre", ""))).strip(),
                "rubro": str(r.get("rubro", r.get("categoria", "Otros"))).strip(),
                "fuente": str(r.get("fuente", "Compras Ágiles")).strip(),
            }
            # Copiar campos extra (útil para futuro)
            for k, v in r.items():
                if k not in opp:
                    opp[k] = v
            normalized.append(opp)

        log(f"{len(normalized)} oportunidades normalizadas.", "ExcelReader")
        return normalized

    except Exception as e:
        log(f"ERROR crítico leyendo Excel: {e}", "ExcelReader")
        return []


def _parse_monto(value) -> float:
    """Convierte monto a float, maneja strings con $, comas, etc."""
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.replace("$", "").replace(",", "").replace(" ", "").strip()
        try:
            return float(cleaned)
        except:
            return 0.0
    return 0.0
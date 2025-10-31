from dotenv import load_dotenv
load_dotenv()  # ← CARGA .env AUTOMÁTICAMENTE

"""
Archivo de configuración global del proyecto.
Incluye rutas de archivos, credenciales y parámetros generales.

NOTA: Usa variables de entorno para claves sensibles.
"""

import os
from pathlib import Path

# === Rutas (seguras y relativas al proyecto) ===
BASE_DIR = Path(__file__).resolve().parent  # Raíz del proyecto
DATA_DIR = BASE_DIR / "data"
EXCEL_PATH = DATA_DIR / "compras_agiles.xlsx"

# Validación temprana: ¿existe el archivo?
if not EXCEL_PATH.exists():
    raise FileNotFoundError(
        f"[ERROR] No se encontró el archivo Excel: {EXCEL_PATH}\n"
        f"    Asegúrate de que exista en: {DATA_DIR}"
    )

# === Credenciales (desde .env o variables de entorno) ===
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY or OPENAI_API_KEY == "tu_api_key_aqui":
    raise ValueError(
        "[ERROR] OPENAI_API_KEY no configurada.\n"
        "    → Crea un archivo .env con: OPENAI_API_KEY=sk-...\n"
        "    → O configúrala en tu entorno."
    )

# === Parámetros de ejecución ===
DEMO_LIMIT = 100  # Número máximo de filas a procesar en modo demo

# === Nombres de agentes (para logging y Agentverse) ===
AGENTE_CONSULTOR_NAME = "AgenteConsultor"
AGENTE_ANALISTA_NAME = "AgenteAnalista"
AGENTE_SUPERVISOR_NAME = "AgenteSupervisor"

# === Modelo LLM (configurable) ===
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")  # Por defecto: barato y rápido
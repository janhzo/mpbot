"""
MedAnalytics - Empresa de INSUMOS MÉDICOS
Prioriza licitaciones MÉDICAS aunque el Excel esté sucio:
- Mayúsculas, minúsculas, acentos
- Variantes: jeringa/jeringas
- Monto: $1.234.567 → 1234567
"""

from modules.utils import log
from typing import List, Dict
import math
import re
import unicodedata

# ==============================
# NORMALIZACIÓN DE TEXTO
# ==============================
def normalizar_texto(texto: str) -> str:
    """Elimina acentos, signos, convierte a minúsculas"""
    if not texto:
        return ""
    texto = str(texto).lower()
    # Quitar acentos
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    # Quitar signos
    texto = re.sub(r'[^a-z0-9\s]', ' ', texto)
    # Colapsar espacios
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

# ==============================
# PALABRAS CLAVE MÉDICAS (CON VARIANTE)
# ==============================
PALABRAS_MEDICAS = [
    # Base
    "insumo", "medico", "quirurgico", "reactivo", "medicamento", "jeringa", "guante",
    "mascarilla", "desinfectante", "equipo medico", "oximetro", "termometro",
    "cateter", "sutura", "vendaje", "gasas", "alcohol", "antiseptico",
    "vacuna", "farmaco", "biologico", "laboratorio", "diagnostico", "prueba rapida",
    # Variantes
    "jeringas", "guantes", "mascarillas", "reactivos", "medicamentos",
    "oximetros", "termometros", "cateteres", "suturas", "vendajes",
    "farmacos", "biologicos", "pruebas rapidas", "insumos medicos"
]

# ==============================
# RUBROS MÉDICOS (AMPLIADO)
# ==============================
RUBROS_MEDICOS = [
    "salud", "hospital", "clinica", "laboratorio", "farmacia", "emergencia",
    "insumos medicos", "material medico", "equipamiento medico",
    "salud publica", "atencion medica", "hospitalario", "farmaceutico"
]

# ==============================
# LIMPIAR MONTO
# ==============================
def limpiar_monto(valor) -> float:
    """Convierte '$1.234.567,89' → 1234567.89"""
    if not valor:
        return 0.0
    texto = str(valor)
    # Quitar $ y espacios
    texto = texto.replace("$", "").replace(" ", "")
    # Manejar comas y puntos (formato chileno/español)
    texto = texto.replace(".", "").replace(",", ".")
    try:
        return float(texto)
    except:
        return 0.0

# ==============================
# SCORING MÉDICO
# ==============================
def score_opportunity(opp: dict) -> float:
    """
    Puntaje 0–100:
    - LLM (50)
    - Palabras clave (30)
    - Rubro (10)
    - Monto log (10)
    """
    score = 0.0

    # 1. LLM Score (máx 50)
    llm_score = opp.get("score", 0)
    score += min(llm_score * 0.5, 50)

    # 2. Palabras clave (máx 30)
    texto = normalizar_texto(f"{opp.get('titulo', '')} {opp.get('descripcion', '')}")
    coincidencias = sum(1 for palabra in PALABRAS_MEDICAS if palabra in texto)
    score += min(coincidencias * 6, 30)

    # 3. Rubro médico (máx 10)
    rubro_norm = normalizar_texto(opp.get("rubro", ""))
    if any(r in rubro_norm for r in RUBROS_MEDICOS):
        score += 10

    # 4. Monto logarítmico (máx 10)
    monto_limpio = limpiar_monto(opp.get("monto", 0))
    if monto_limpio > 0:
        log_monto = math.log10(monto_limpio)
        score += min(log_monto, 10)

    # 5. Obligatorio: postular=True
    if not opp.get("postular", False):
        return 0.0

    return round(min(score, 100), 2)

# ==============================
# RANKING FINAL
# ==============================
def rank_opportunities(opportunities: List[dict], top_n: int = 5) -> List[dict]:
    log(f"Analizando {len(opportunities)} licitaciones...", "MedAnalytics")

    # Filtrar postulables
    relevantes = [opp for opp in opportunities if opp.get("postular", False)]
    log(f"{len(relevantes)} marcadas como postulables por LLM.", "MedAnalytics")

    # Puntuar
    for opp in relevantes:
        opp["puntaje"] = score_opportunity(opp)

    # Ordenar
    ranked = sorted(relevantes, key=lambda x: x["puntaje"], reverse=True)
    top = ranked[:top_n]

    log(f"TOP {len(top)} INSUMOS MÉDICOS seleccionados:", "MedAnalytics")
    for i, t in enumerate(top, 1):
        titulo = t.get("titulo", "Sin título")[:60]
        puntaje = t.get("puntaje", 0)
        log(f"  #{i} | {titulo:<60} | Puntaje: {puntaje}/100", "MedAnalytics")

    return top
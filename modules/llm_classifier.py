"""
LLM Classifier - Empresa de INSUMOS MÉDICOS
Clasifica licitaciones para:
- Jeringas, guantes, mascarillas
- Reactivos, medicamentos, fármacos
- Equipos médicos, oxímetros, etc.
RECHAZA todo lo demás.
"""

import json
import openai
from config import OPENAI_API_KEY, LLM_MODEL
from modules.utils import log

# Cliente OpenAI
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# ==============================
# PALABRAS CLAVE MÉDICAS (para validación extra)
# ==============================
PALABRAS_MEDICAS = [
    "jeringa", "guante", "mascarilla", "reactivo", "medicamento", "fármaco",
    "vacuna", "insumo médico", "material quirúrgico", "oxímetro", "termómetro",
    "catéter", "sutura", "vendaje", "desinfectante", "alcohol", "gasas",
    "prueba rápida", "biológico", "laboratorio", "diagnóstico", "hospital"
]

def classify_opportunity(titulo: str, descripcion: str) -> dict:
    """
    Clasifica SOLO oportunidades de INSUMOS MÉDICOS o REMEDIOS.
    Rechaza todo lo demás.
    """
    texto = f"{titulo} {descripcion}".lower()
    tiene_palabra_medica = any(palabra in texto for palabra in PALABRAS_MEDICAS)
    
    log(f"Clasificando: {titulo[:60]}...", "MedClassifier")

    prompt = f"""
    Eres un experto en compras públicas para una EMPRESA DE INSUMOS MÉDICOS.
    Solo aceptamos licitaciones de:
    - Insumos médicos (jeringas, guantes, mascarillas, gasas, etc.)
    - Medicamentos, fármacos, vacunas, reactivos
    - Equipos médicos básicos (termómetros, oxímetros, etc.)

    Si NO es relacionado con salud o insumos médicos → postular: false

    TÍTULO: {titulo}
    DESCRIPCIÓN: {descripcion}

    Responde SOLO en JSON válido:
    {{
        "rubro": "INSUMOS MÉDICOS" | "FÁRMACOS" | "EQUIPOS MÉDICOS" | "OTROS",
        "postular": true/false,
        "viabilidad": "alta" | "media" | "baja",
        "score": 0-100,
        "razon": "explicación breve (máx 120 caracteres)"
    }}

    EJEMPLOS:
    - "Compra de jeringas 3ml" → rubro: "INSUMOS MÉDICOS", postular: true, score: 95
    - "Construcción de puente" → rubro: "OTROS", postular: false, score: 0
    """

    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # Muy determinista
            max_tokens=250
        )

        content = response.choices[0].message.content.strip()
        log(f"Respuesta LLM: {content}", "MedClassifier")

        # Limpiar ```json
        if content.startswith("```"):
            lines = content.splitlines()
            content = "\n".join(lines[1:-1]) if len(lines) > 2 else content

        result = json.loads(content)

        # === VALIDACIÓN EXTRA ===
        if not tiene_palabra_medica:
            result["postular"] = False
            result["score"] = 0
            result["viabilidad"] = "baja"
            result["razon"] = "No contiene palabras clave médicas."
            result["rubro"] = "OTROS"

        # Forzar rubros válidos
        rubro = result.get("rubro", "OTROS").upper()
        if rubro not in ["INSUMOS MÉDICOS", "FÁRMACOS", "EQUIPOS MÉDICOS"]:
            result["rubro"] = "OTROS"

        defaults = {
            "rubro": result.get("rubro", "OTROS"),
            "postular": bool(result.get("postular", False)),
            "viabilidad": result.get("viabilidad", "baja"),
            "score": max(0, min(int(result.get("score", 0)), 100)),
            "razon": result.get("razon", "Sin análisis")[:120]
        }

        log(f"Resultado final: {defaults['rubro']} | postular: {defaults['postular']} | score: {defaults['score']}", "MedClassifier")
        return defaults

    except Exception as e:
        log(f"Error LLM: {e}", "MedClassifier")
        return {
            "rubro": "OTROS",
            "postular": False,
            "viabilidad": "baja",
            "score": 0,
            "razon": "Error en clasificación LLM"
        }
# modules/utils.py
from datetime import datetime
from uuid import uuid4
from uagents_core.contrib.protocols.chat import ChatMessage, TextContent, EndSessionContent
import json
import os

def log(message: str, agent_name: str = "Utils"):
    """
    Imprime logs con timestamp y nombre del agente.
    """
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[{timestamp}] [{agent_name}] {message}")


def create_chat_message(
    text: str,
    end_session: bool = False,
    agent_name: str = "Utils"
) -> ChatMessage:
    """
    Crea un mensaje de chat con texto.
    Opcionalmente cierra la sesión.
    """
    content = [TextContent(type="text", text=text)]
    if end_session:
        content.append(EndSessionContent())
        log("Sesión cerrada.", agent_name)
    return ChatMessage(
        timestamp=datetime.utcnow(),
        msg_id=str(uuid4()),  # ← uuid4() debe ser str
        content=content
    )


def format_json_message(
    data: dict,
    end_session: bool = False,
    agent_name: str = "Utils"
) -> ChatMessage:
    """
    Convierte un dict a JSON y lo envuelve en un ChatMessage.
    """
    try:
        json_text = json.dumps(data, ensure_ascii=False, indent=2)
        log(f"JSON enviado:\n{json_text}", agent_name)
        return create_chat_message(json_text, end_session, agent_name)
    except Exception as e:
        error = f"Error al serializar JSON: {e}"
        log(error, agent_name)
        return create_chat_message(error, agent_name=agent_name)


def save_report_to_file(report_text: str, filename: str = None) -> str:
    """
    Guarda el reporte en disco dentro de data/reports/
    Devuelve la ruta completa del archivo.
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"reporte_insumos_medicos_{timestamp}.txt"

    output_dir = "data/reports"
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_text)
        log(f"Informe guardado en: {filepath}", "Utils")
        return filepath
    except Exception as e:
        log(f"Error al guardar archivo: {e}", "Utils")
        raise
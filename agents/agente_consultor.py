"""
MedConsultor - Empresa de Insumos Médicos
- Lee Excel de licitaciones
- Clasifica con GPT (solo insumos médicos POSTULABLES)
- ENVÍA UNA SOLA VEZ + human_address al MedAnalista ← CORREGIDO
- SIN BUCLE INFINITO
- ASI:One + Agentverse + Chat Protocol
"""

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from uagents_core.contrib.protocols.chat import (
    chat_protocol_spec,
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    StartSessionContent
)
from modules.excel_reader import read_opportunities
from modules.llm_classifier import classify_opportunity
from modules.utils import create_chat_message, log
from config import (
    AGENTE_CONSULTOR_NAME,
    DEMO_LIMIT,
    EXCEL_PATH
)
import json
from datetime import datetime, timezone

# ==============================
# DIRECCIÓN DEL ANALISTA (HARD-CODE)
# ==============================
ANALISTA_ADDRESS = "agent1q09jyj082tfyta9075vx9pdj0f6xj3zzjpk6529a564ffgu2zwd8203u7xj"

# ==============================
# ESTADO DE ENVÍO (EVITA BUCLE)
# ==============================
ya_enviado = False

# ==============================
# Configuración del Agente
# ==============================
agent = Agent(
    name=AGENTE_CONSULTOR_NAME,
    seed=f"{AGENTE_CONSULTOR_NAME}_seed_789",
    port=8000,
    mailbox=True
)
fund_agent_if_low(agent.wallet.address())

# ==============================
# Protocolo de Chat
# ==============================
chat_proto = Protocol(spec=chat_protocol_spec)

# ==============================
# Procesar Excel + LLM (SOLO INSUMOS MÉDICOS POSTULABLES)
# ==============================
def process_opportunities(limit: int = DEMO_LIMIT):
    log(f"Buscando INSUMOS MÉDICOS en: {EXCEL_PATH}", AGENTE_CONSULTOR_NAME)
    rows = read_opportunities(limit=limit)
    if not rows:
        log("No se encontraron licitaciones.", AGENTE_CONSULTOR_NAME)
        return []

    resultados = []
    for r in rows:
        titulo = r.get("titulo", "")
        descripcion = r.get("descripcion", "")

        # Clasificación con LLM
        llm_result = classify_opportunity(titulo, descripcion)
        try:
            if isinstance(llm_result, str):
                llm_result = json.loads(llm_result)
        except:
            llm_result = {"rubro": "desconocido", "postular": False, "razon": "Error LLM"}

        r.update(llm_result)

        # === SOLO GUARDAR SI ES POSTULABLE ===
        if llm_result.get("postular", False):
            resultados.append(r)

    log(f"{len(resultados)} licitaciones MÉDICAS postulables encontradas.", AGENTE_CONSULTOR_NAME)
    return resultados

# ==============================
# Manejo de Mensajes
# ==============================
@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    global ya_enviado
    log(f"Mensaje recibido de {sender}", AGENTE_CONSULTOR_NAME)

    # === ACK OFICIAL ===
    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc),
            acknowledged_msg_id=msg.msg_id
        )
    )

    for item in msg.content:
        # === INICIAR CON CUALQUIER MENSAJE DE TEXTO (SOLO UNA VEZ) ===
        if isinstance(item, TextContent) and not ya_enviado:
            raw_text = item.text.strip()

            # === FILTRAR ACKs Y MENSAJES VACÍOS ===
            if raw_text in ["OK", "ACK", ""]:
                log(f"ACK recibido (como texto) de {sender}", AGENTE_CONSULTOR_NAME)
                continue

            log(f"INICIANDO FLUJO ÚNICO con mensaje: '{raw_text}'", AGENTE_CONSULTOR_NAME)

            # === PROCESAR Y ENVIAR AL ANALISTA (UNA SOLA VEZ) ===
            resultados = process_opportunities()
            if resultados:
                # === AÑADIDO: human_address = sender (tú en ASI:One) ===
                mensaje_analista = create_chat_message(
                    json.dumps({
                        "type": "data",
                        "rows": resultados,
                        "human_address": sender  # ← ¡TÚ!
                    }, ensure_ascii=False, indent=2),
                    agent_name=AGENTE_CONSULTOR_NAME
                )
                await ctx.send(ANALISTA_ADDRESS, mensaje_analista)
                log(f"ENVIADO UNA VEZ: {len(resultados)} oportunidades + human_address", AGENTE_CONSULTOR_NAME)
                ya_enviado = True

                # === RESPUESTA AL HUMANO ===
                top_n = min(5, len(resultados))
                await ctx.send(sender, create_chat_message(
                    f"{len(resultados)} licitaciones médicas enviadas al MedAnalista.\n"
                    f"Esperando TOP {top_n} del MedSupervisor...",
                    agent_name=AGENTE_CONSULTOR_NAME
                ))
            else:
                await ctx.send(sender, create_chat_message(
                    "No se encontraron licitaciones médicas postulables.",
                    agent_name=AGENTE_CONSULTOR_NAME
                ))
                ya_enviado = True

        # === SI YA SE ENVIÓ: INFORMAR ESTADO ===
        elif isinstance(item, TextContent) and ya_enviado:
            await ctx.send(sender, create_chat_message(
                "Ya se procesaron las licitaciones. Esperando reporte del MedSupervisor...",
                agent_name=AGENTE_CONSULTOR_NAME
            ))

        # === INICIAR SESIÓN (opcional) ===
        elif isinstance(item, StartSessionContent):
            await ctx.send(sender, create_chat_message(
                f"¡Hola! Soy {AGENTE_CONSULTOR_NAME}. Escribe cualquier cosa para analizar licitaciones (una vez).",
                agent_name=AGENTE_CONSULTOR_NAME
            ))

# ==============================
# ACKs
# ==============================
@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    log(f"ACK recibido de {sender}", AGENTE_CONSULTOR_NAME)

# ==============================
# Publicar
# ==============================
agent.include(chat_proto, publish_manifest=True)

# ==============================
# Ejecutar
# ==============================
if __name__ == "__main__":
    print(f"\n{AGENTE_CONSULTOR_NAME} - INSUMOS MÉDICOS")
    print(f"  Dirección: {agent.address}")
    print(f"  Puerto: 8000")
    print(f"  Inspector: https://agentverse.ai/inspect/?uri=http://127.0.0.1:8000&address={agent.address}")
    print(f"  Escribe CUALQUIER COSA en ASI:One → se ejecuta UNA SOLA VEZ\n")
    agent.run()
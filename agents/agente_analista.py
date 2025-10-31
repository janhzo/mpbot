"""
MedAnalista - Empresa de Insumos Médicos
- Recibe del MedConsultor
- Prioriza INSUMOS MÉDICOS
- ENVÍA TOP 5 + human_address al MedSupervisor ← CORREGIDO
- 100% ROBUSTO + DIAGNÓSTICO CLARO
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
from modules.analytics import rank_opportunities
from modules.utils import create_chat_message, log
from config import AGENTE_ANALISTA_NAME
import json
from datetime import datetime, timezone
import threading

# ==============================
# DIRECCIÓN DEL SUPERVISOR
# ==============================
SUPERVISOR_ADDRESS = "agent1q2gmu2xd3yalrue7mwd0wkq35xqw48p70djp5274vxyqvnf7cn735wdyuc5"

# ==============================
# Configuración del Agente
# ==============================
agent = Agent(
    name=AGENTE_ANALISTA_NAME,
    seed=f"{AGENTE_ANALISTA_NAME}_seed_123456",
    port=8001,
    mailbox=True
)

# ==============================
# Fondear de forma segura
# ==============================
def fund_wallet_safely():
    try:
        fund_agent_if_low(agent.wallet.address())
        log("Wallet fondeada exitosamente.", AGENTE_ANALISTA_NAME)
    except Exception as e:
        log(f"Error al fondear wallet: {e}", AGENTE_ANALISTA_NAME)

threading.Thread(target=fund_wallet_safely, daemon=True).start()

# ==============================
# Protocolo de Chat
# ==============================
chat_proto = Protocol(spec=chat_protocol_spec)
TOP_N = 5

# ==============================
# Manejo de Mensajes
# ==============================
@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    log(f"Mensaje recibido de {sender}", AGENTE_ANALISTA_NAME)

    # === ENVIAR ACK OFICIAL ===
    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc),
            acknowledged_msg_id=msg.msg_id
        )
    )

    for item in msg.content:
        # === INICIO DE SESIÓN ===
        if isinstance(item, StartSessionContent):
            await ctx.send(sender, create_chat_message(
                f"¡Hola! Soy {AGENTE_ANALISTA_NAME}. Esperando datos del MedConsultor...",
                agent_name=AGENTE_ANALISTA_NAME
            ))
            continue

        # === MENSAJE DE TEXTO ===
        if isinstance(item, TextContent):
            raw_text = item.text.strip()

            # === FILTRAR ACKs, MENSAJES VACÍOS O PEGADOS ===
            if raw_text in ["OK", "ACK", ""]:
                log(f"ACK recibido (como texto) de {sender}", AGENTE_ANALISTA_NAME)
                continue

            if raw_text.startswith("OK") or raw_text.startswith("ACK"):
                json_part = raw_text[2:].strip()
                if json_part.startswith("{"):
                    raw_text = json_part
                    log(f"JSON extraído de mensaje pegado: {raw_text[:100]}...", AGENTE_ANALISTA_NAME)
                else:
                    log(f"Mensaje de control ignorado: {raw_text[:50]}", AGENTE_ANALISTA_NAME)
                    continue

            # === SOLO INTENTAR json.loads() SI EMPIEZA CON { ===
            if not raw_text.startswith("{"):
                log(f"Mensaje ignorado (no es JSON): {raw_text[:100]}...", AGENTE_ANALISTA_NAME)
                continue

            # === PARSEAR JSON SEGURO ===
            try:
                data = json.loads(raw_text)

                # === SOLO ACEPTAR type: "data" DEL CONSULTOR ===
                if data.get("type") != "data":
                    log(f"Tipo no esperado: {data.get('type')}", AGENTE_ANALISTA_NAME)
                    continue

                rows = data.get("rows", [])
                if not rows:
                    await ctx.send(sender, create_chat_message("No se recibieron oportunidades."))
                    continue

                # === EXTRAER human_address DEL CONSULTOR ===
                human_address = data.get("human_address")
                if not human_address:
                    human_address = sender
                    log("ADVERTENCIA: human_address no recibido. Usando sender como fallback.", AGENTE_ANALISTA_NAME)
                else:
                    log(f"Humano original recibido del consultor: {human_address[:12]}...", AGENTE_ANALISTA_NAME)

                # === RANKING ===
                top_oportunidades = rank_opportunities(rows, top_n=TOP_N)
                if not top_oportunidades:
                    await ctx.send(sender, create_chat_message("No hay oportunidades médicas postulables."))
                    continue

                log(f"TOP {len(top_oportunidades)} INSUMOS MÉDICOS calculado", AGENTE_ANALISTA_NAME)

                # === ENVIAR AL SUPERVISOR CON human_address ===
                mensaje_supervisor = create_chat_message(
                    json.dumps({
                        "type": "result",
                        "rubro": "INSUMOS MÉDICOS",
                        "top_oportunidades": top_oportunidades,
                        "human_address": human_address  # ← ¡CLAVE!
                    }, ensure_ascii=False, indent=2),
                    agent_name=AGENTE_ANALISTA_NAME
                )
                try:
                    await ctx.send(SUPERVISOR_ADDRESS, mensaje_supervisor)
                    log(f"TOP {len(top_oportunidades)} + human_address enviado al MedSupervisor", AGENTE_ANALISTA_NAME)
                except Exception as e:
                    error_msg = str(e).lower()
                    if "404" in error_msg or "not found" in error_msg:
                        diag = (
                            f"MEDSUPERVISOR NO REGISTRADO\n"
                            f"Dirección: {SUPERVISOR_ADDRESS}\n"
                            f"Puerto: 8002\n"
                            f"Inicia: python agents\\agente_supervisor.py"
                        )
                    else:
                        diag = f"Error de red: {str(e)[:100]}"
                    log(diag, AGENTE_ANALISTA_NAME)
                    await ctx.send(sender, create_chat_message(diag))
                    continue

                # === RESPUESTA AL CONSULTOR ===
                await ctx.send(sender, create_chat_message(
                    f"TOP {len(top_oportunidades)} insumos médicos enviados al MedSupervisor.\n"
                    f"Esperando reporte final...",
                    agent_name=AGENTE_ANALISTA_NAME
                ))

            except json.JSONDecodeError as e:
                log(f"JSON inválido: {e}\nContenido: {raw_text[:200]}", AGENTE_ANALISTA_NAME)
                await ctx.send(sender, create_chat_message("Error: Datos corruptos."))
            except Exception as e:
                log(f"Error inesperado: {e}", AGENTE_ANALISTA_NAME)
                await ctx.send(sender, create_chat_message(f"Error interno: {e}"))

# ==============================
# ACKs
# ==============================
@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    log(f"ACK recibido de {sender}", AGENTE_ANALISTA_NAME)

# ==============================
# Publicar
# ==============================
agent.include(chat_proto, publish_manifest=True)

# ==============================
# Ejecutar
# ==============================
if __name__ == "__main__":
    print(f"\n{AGENTE_ANALISTA_NAME} - INSUMOS MÉDICOS")
    print(f"  Dirección: {agent.address}")
    print(f"  Puerto: 8001")
    print(f"  Inspector: https://agentverse.ai/inspect/?uri=http://127.0.0.1:8001&address={agent.address}")
    print(f"  Esperando licitaciones del MedConsultor...\n")
    print(f"  SUPERVISOR DEBE ESTAR EN: {SUPERVISOR_ADDRESS} (puerto 8002)\n")
    
    agent.run()
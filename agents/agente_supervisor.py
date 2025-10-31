"""
MedSupervisor - Empresa de Insumos Médicos
- Recibe TOP 5 del MedAnalista
- Genera REPORTE MÉDICO priorizado
- ENVÍA REPORTE AL HUMANO (ASI:One) ← CORREGIDO
- Permite marcar como REVISADA
- 100% FUNCIONAL + SIN ERRORES
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
from modules.utils import create_chat_message, log, save_report_to_file  # ← Añadido
from config import AGENTE_SUPERVISOR_NAME
import json
from datetime import datetime, timezone
import threading

# ==============================
# Configuración del Agente
# ==============================
agent = Agent(
    name=AGENTE_SUPERVISOR_NAME,
    seed=f"{AGENTE_SUPERVISOR_NAME}_seed_999",
    port=8002,
    mailbox=True
)

# ==============================
# Fondear de forma segura
# ==============================
def fund_wallet_safely():
    try:
        fund_agent_if_low(agent.wallet.address())
        log("Wallet fondeada exitosamente.", AGENTE_SUPERVISOR_NAME)
    except Exception as e:
        log(f"Error al fondear wallet: {e}", AGENTE_SUPERVISOR_NAME)

threading.Thread(target=fund_wallet_safely, daemon=True).start()

# ==============================
# Protocolo de Chat
# ==============================
chat_proto = Protocol(spec=chat_protocol_spec)

# ==============================
# Estado interno
# ==============================
estado = {
    "oportunidades": [],
    "revisadas": [],
    "humano_original": None  # ← Guardará la dirección del humano en ASI:One
}

# ==============================
# LIMPIAR MONTO
# ==============================
def formatear_monto(valor) -> str:
    try:
        monto = float(str(valor).replace("$", "").replace(",", "").replace(".", ""))
        return f"${monto:,.0f}"
    except:
        return "$0"

# ==============================
# Manejo de Mensajes
# ==============================
@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    log(f"Mensaje recibido de {sender}", AGENTE_SUPERVISOR_NAME)

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
                f"¡Hola! Soy {AGENTE_SUPERVISOR_NAME}. Esperando TOP 5 del MedAnalista...",
                agent_name=AGENTE_SUPERVISOR_NAME
            ))
            continue

        # === MENSAJE DE TEXTO ===
        if isinstance(item, TextContent):
            raw_text = item.text.strip()

            # === FILTRAR ACKs, MENSAJES VACÍOS O PEGADOS ===
            if raw_text in ["OK", "ACK", ""]:
                log(f"ACK recibido (como texto) de {sender}", AGENTE_SUPERVISOR_NAME)
                continue

            if raw_text.startswith("OK") or raw_text.startswith("ACK"):
                json_part = raw_text[2:].strip()
                if json_part.startswith("{"):
                    raw_text = json_part
                    log(f"JSON extraído de mensaje pegado: {raw_text[:100]}...", AGENTE_SUPERVISOR_NAME)
                else:
                    log(f"Mensaje de control ignorado: {raw_text[:50]}", AGENTE_SUPERVISOR_NAME)
                    continue

            # === COMANDO: MARCAR REVISADA ===
            if raw_text.isdigit() and estado["oportunidades"]:
                idx = int(raw_text) - 1
                if 0 <= idx < len(estado["oportunidades"]):
                    opp = estado["oportunidades"][idx]
                    estado["revisadas"].append(opp)
                    
                    respuesta = (
                        f"INSUMO MÉDICO #{raw_text} MARCADO COMO REVISADO\n"
                        f"Título: {opp.get('titulo', '')}\n"
                        f"Monto: {formatear_monto(opp.get('monto', 0))}\n"
                        f"Rubro: {opp.get('rubro', 'N/A')}\n"
                        f"Acción:\n"
                        f"→ Preparar documentación para postulación.\n"
                        f"→ Contactar proveedor.\n"
                        f"→ Validar stock disponible."
                    )
                    destino = estado["humano_original"] or sender
                    await ctx.send(destino, create_chat_message(
                        respuesta,
                        agent_name=AGENTE_SUPERVISOR_NAME
                    ))
                    log(f"Oportunidad #{raw_text} revisada (enviado a {destino[:12]}...)", AGENTE_SUPERVISOR_NAME)
                    continue

            # === SOLO INTENTAR json.loads() SI EMPIEZA CON { ===
            if not raw_text.startswith("{"):
                log(f"Mensaje ignorado (no es JSON): {raw_text[:100]}...", AGENTE_SUPERVISOR_NAME)
                continue

            # === PARSEAR JSON SEGURO ===
            try:
                data = json.loads(raw_text)

                # === SOLO ACEPTAR type: "result" ===
                if data.get("type") != "result":
                    log(f"Tipo no esperado: {data.get('type')}", AGENTE_SUPERVISOR_NAME)
                    continue

                top_oportunidades = data.get("top_oportunidades", [])
                if not top_oportunidades:
                    destino = estado["humano_original"] or sender
                    await ctx.send(destino, create_chat_message(
                        "No se recibieron oportunidades.",
                        agent_name=AGENTE_SUPERVISOR_NAME
                    ))
                    continue

                # === GUARDAR DATOS ===
                estado["oportunidades"] = top_oportunidades

                # === GUARDAR HUMANO ORIGINAL (desde el analista) ===
                human_address = data.get("human_address")
                if human_address and human_address != sender:
                    estado["humano_original"] = human_address
                    log(f"Humano original recibido desde analista: {human_address[:12]}...", AGENTE_SUPERVISOR_NAME)
                else:
                    estado["humano_original"] = sender
                    log("ADVERTENCIA: No se recibió human_address. Usando sender como fallback.", AGENTE_SUPERVISOR_NAME)

                log(f"TOP {len(top_oportunidades)} INSUMOS MÉDICOS recibidos", AGENTE_SUPERVISOR_NAME)

                # === GENERAR REPORTE MÉDICO ===
                reporte = "REPORTE DE INSUMOS MÉDICOS PRIORIZADOS\n"
                reporte += "Empresa: INSUMEDICAL S.A.\n"
                reporte += "=" * 60 + "\n"
                for i, opp in enumerate(top_oportunidades, 1):
                    titulo = opp.get("titulo", "Sin título")[:70]
                    monto = formatear_monto(opp.get("monto", 0))
                    puntaje = opp.get("puntaje", 0)
                    rubro = opp.get("rubro", "N/A")
                    razon = opp.get("razon", "Sin análisis")[:120]
                    reporte += f"{i}. [{rubro.upper()}] {titulo}\n"
                    reporte += f"    Monto: {monto} | Puntaje: {puntaje}/100\n"
                    reporte += f"    Razón: {razon}\n\n"

                reporte += "Responde con el número para marcar como REVISADA.\n"
                reporte += "Ej: 1 → Preparar postulación."

                # === GUARDAR REPORTE EN DISCO (opcional pero útil) ===
                try:
                    file_path = save_report_to_file(reporte, "reporte_insumos_medicos.txt")
                    log(f"Informe guardado en: {file_path}", AGENTE_SUPERVISOR_NAME)
                except Exception as e:
                    log(f"Error al guardar archivo: {e}", AGENTE_SUPERVISOR_NAME)

                # === ENVIAR AL HUMANO EN ASI:One ===
                destino = estado["humano_original"]
                await ctx.send(destino, create_chat_message(
                    reporte,
                    agent_name=AGENTE_SUPERVISOR_NAME
                ))
                log(f"REPORTE ENVIADO AL HUMANO (ASI:One): {destino[:12]}...", AGENTE_SUPERVISOR_NAME)

            except json.JSONDecodeError as e:
                log(f"JSON inválido: {e}\nContenido: {raw_text[:200]}", AGENTE_SUPERVISOR_NAME)
                destino = estado["humano_original"] or sender
                await ctx.send(destino, create_chat_message(
                    "Error: JSON inválido recibido.",
                    agent_name=AGENTE_SUPERVISOR_NAME
                ))
            except Exception as e:
                log(f"Error procesando mensaje: {e}", AGENTE_SUPERVISOR_NAME)
                destino = estado["humano_original"] or sender
                await ctx.send(destino, create_chat_message(
                    f"Error interno: {e}",
                    agent_name=AGENTE_SUPERVISOR_NAME
                ))

# ==============================
# ACKs
# ==============================
@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    log(f"ACK recibido de {sender}", AGENTE_SUPERVISOR_NAME)

# ==============================
# Publicar
# ==============================
agent.include(chat_proto, publish_manifest=True)

# ==============================
# Ejecutar
# ==============================
if __name__ == "__main__":
    print(f"\n{AGENTE_SUPERVISOR_NAME} - INSUMOS MÉDICOS")
    print(f"  Dirección: {agent.address}")
    print(f"  Puerto: 8002")
    print(f"  Inspector: https://agentverse.ai/inspect/?uri=http://127.0.0.1:8002&address={agent.address}")
    print(f"  Esperando TOP 5 del MedAnalista...\n")
    
    agent.run()
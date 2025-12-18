# app.py — WhatsApp bot (Flask + Twilio) — STABLE VERSION

import logging
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

from intents import detect_intent
from db import (
    init_db,
    save_message,
    get_user_state,
    set_user_state,
    create_support_ticket,
    save_support_description,
    save_support_urgency,
    log_flow_event
)

# ------------------------
# States
# ------------------------

STATE_MENU = "MENU"
STATE_SUPPORT_DESC = "SUPPORT_DESC"
STATE_SUPPORT_URGENCY = "SUPPORT_URGENCY"

# ------------------------
# App setup
# ------------------------

app = Flask(__name__)
init_db()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ------------------------
# Webhook
# ------------------------

@app.route("/whatsapp", methods=["POST"])
def whatsapp_bot():
    response = MessagingResponse()
    msg = response.message()

    try:
        incoming_msg = request.values.get("Body", "").strip()
        incoming_lower = incoming_msg.lower()
        phone = request.values.get("From")

        logging.info(f"From={phone} | Message={incoming_msg!r}")

        save_message(phone, incoming_msg)
        state = get_user_state(phone)

        # ------------------------
        # GLOBAL COMMANDS
        # ------------------------

        if incoming_lower in ("menu", "start"):
            set_user_state(phone, STATE_MENU)
            msg.body(
                "📋 *Menu*\n"
                "1️⃣ Preços\n"
                "2️⃣ Suporte\n"
                "3️⃣ Falar com um atendente"
            )
            return str(response)

        # ------------------------
        # STATE: MENU
        # ------------------------

        if state == STATE_MENU:
            if incoming_lower == "1":
                set_user_state(phone, None)
                msg.body(
                    "💰 *Preços*\n"
                    "Plano Básico: R$ 50/mês\n"
                    "Plano Pro: R$ 120/mês"
                )
                return str(response)

            if incoming_lower == "2":
                create_support_ticket(phone)
                log_flow_event(phone, "SUPPORT_START")
                set_user_state(phone, STATE_SUPPORT_DESC)
                msg.body("🛠 Descreva seu problema, por favor.")
                return str(response)

            if incoming_lower == "3":
                set_user_state(phone, None)
                msg.body("👤 Um atendente humano entrará em contato.")
                return str(response)

            # fallback seguro no menu
            msg.body("❗ Por favor, escolha 1, 2 ou 3.")
            return str(response)

        # ------------------------
        # STATE: SUPPORT DESC
        # ------------------------

        if state == STATE_SUPPORT_DESC:
            save_support_description(phone, incoming_msg)
            log_flow_event(phone, "SUPPORT_DESCRIPTION")
            set_user_state(phone, STATE_SUPPORT_URGENCY)

            msg.body("⚠️ Qual a urgência do problema? (baixa / média / alta)")
            return str(response)

        # ------------------------
        # STATE: SUPPORT URGENCY
        # ------------------------

        if state == STATE_SUPPORT_URGENCY:
            if incoming_lower not in ("baixa", "media", "média", "alta"):
                msg.body("Por favor, responda com: baixa, média ou alta.")
                return str(response)

            save_support_urgency(phone, incoming_lower)
            log_flow_event(phone, "SUPPORT_URGENCY", incoming_lower)
            log_flow_event(phone, "SUPPORT_DONE")

            set_user_state(phone, None)
            msg.body("✅ Chamado registrado com sucesso!")
            return str(response)

        # ------------------------
        # INTENTS (NO STATE)
        # ------------------------

        intent, confidence = detect_intent(incoming_msg)
        logging.info(f"INTENT={intent} CONFIDENCE={confidence}")

        if confidence < 0.25:
            intent = None

        if intent == "GREETING":
            msg.body("Olá! 👋 Digite *menu* para ver as opções.")

        elif intent == "SERVICES":
            msg.body(
                "Oferecemos:\n"
                "🤖 Chatbots para WhatsApp\n"
                "⚙️ Automações\n"
                "📊 Integrações com sistemas"
            )

        elif intent == "PRICING":
            msg.body(
                "💰 *Preços*\n"
                "Plano Básico: R$ 50/mês\n"
                "Plano Pro: R$ 120/mês"
            )

        elif intent == "SUPPORT":
            create_support_ticket(phone)
            log_flow_event(phone, "SUPPORT_START")
            set_user_state(phone, STATE_SUPPORT_DESC)
            msg.body("🛠 Descreva seu problema, por favor.")

        elif intent == "HUMAN":
            msg.body("👤 Um atendente humano entrará em contato.")

        else:
            log_flow_event(phone, "UNKNOWN_MESSAGE", incoming_msg)
            msg.body(
                "❓ Não entendi sua mensagem.\n"
                "Digite *menu* para ver as opções."
            )

        return str(response)

    except Exception as e:
        logging.exception("Unhandled error")
        msg.body(
            "⚠️ Ocorreu um erro inesperado.\n"
            "Por favor, tente novamente em alguns instantes."
        )
        return str(response)


# ------------------------
# Run
# ------------------------

if __name__ == "__main__":
    app.run()

import os
import logging
import requests

from dotenv import load_dotenv

from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo
)

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes
)

# ==========================================
# CARGAR VARIABLES
# ==========================================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
WEBAPP_URL = os.getenv("WEBAPP_URL")

# ==========================================
# LOGS
# ==========================================

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# ==========================================
# SUPABASE RPC
# ==========================================

def init_user(
    telegram_id: int,
    username: str,
    first_name: str,
    referrer_id
):
    try:

        url = f"{SUPABASE_URL}/rest/v1/rpc/init_user_tma"

        headers = {
            "apikey": SUPABASE_SERVICE_ROLE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "p_telegram_id": telegram_id,
            "p_username": username,
            "p_first_name": first_name,
            "p_referrer_id": referrer_id
        }

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30
        )

        logger.info(f"Supabase: {response.status_code}")

        return response.ok

    except Exception as e:
        logger.error(f"ERROR SUPABASE: {e}")
        return False

# ==========================================
# START
# ==========================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        user = update.effective_user

        telegram_id = user.id
        username = user.username or "sin_username"
        first_name = user.first_name or "Usuario"

        referrer_id = None

        if context.args:

            try:

                possible_referrer = int(context.args[0])

                if possible_referrer != telegram_id:
                    referrer_id = possible_referrer

                    logger.info(
                        f"Referido detectado: "
                        f"{telegram_id} <- {referrer_id}"
                    )

            except Exception:
                pass

        init_user(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            referrer_id=referrer_id
        )

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    text="🚀 ABRIR MINI APP",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ])

        await update.message.reply_text(
            (
                "🚀 Bienvenido a MINER TRX FREE\n\n"
                "Gana TRX completando tareas, minería cloud, "
                "Crypto Mines y ruleta de premios.\n\n"
                "👥 Invita amigos y recibe automáticamente "
                "el 15% de sus ganancias.\n\n"
                "👇 Abre la aplicación para comenzar."
            ),
            reply_markup=keyboard
        )

        logger.info(
            f"Usuario procesado: "
            f"{telegram_id}"
        )

    except Exception as e:

        logger.error(f"ERROR START: {e}")

# ==========================================
# MAIN
# ==========================================

def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    logger.info("BOT INICIADO")

    app.run_polling()

if __name__ == "__main__":
    main()
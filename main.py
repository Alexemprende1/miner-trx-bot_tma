import os
import logging
import requests
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo
)
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
WEBAPP_URL = os.environ["WEBAPP_URL"]
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_ROLE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PORT = int(os.environ.get("PORT", "10000"))


def init_user(
    telegram_id: int,
    username: str,
    first_name: str,
    referrer_id: int | None
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
                "🚀 ¡Bienvenido a MINER TRX FREE!

💎 Mina TRX gratis desde Telegram.

🎮 Disfruta de:
• ⛏️ Minería Cloud
• 💣 Crypto Mines
• 🎡 Ruleta de premios
• 📋 Tareas diarias

👥 Invita a tus amigos y recibe automáticamente el 15% de sus ganancias.

👇 Pulsa el botón de abajo para abrir la Mini App y comenzar a ganar TRX."
            ),
            reply_markup=keyboard
        )

        logger.info(
            f"Usuario procesado: {telegram_id}"
        )

    except Exception as e:

        logger.error(f"ERROR START: {e}")


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()

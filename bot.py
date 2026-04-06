import os
import io
import base64
import logging
from pathlib import Path

import anthropic
from PIL import Image
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

SYSTEM_PROMPT = Path(__file__).parent.joinpath("system_prompt.md").read_text()

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Per-user conversation history (in-memory, resets on restart)
conversations: dict[int, list[dict]] = {}
MAX_HISTORY = 20  # keep last 20 messages per user


def get_history(user_id: int) -> list[dict]:
    if user_id not in conversations:
        conversations[user_id] = []
    return conversations[user_id]


def add_to_history(user_id: int, role: str, content):
    history = get_history(user_id)
    history.append({"role": role, "content": content})
    # Trim to keep memory bounded
    if len(history) > MAX_HISTORY:
        conversations[user_id] = history[-MAX_HISTORY:]


def resize_image(image_bytes: bytes, max_size: int = 1024) -> bytes:
    """Resize image to save Vision API tokens."""
    img = Image.open(io.BytesIO(image_bytes))
    if max(img.size) > max_size:
        img.thumbnail((max_size, max_size), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversations.pop(user_id, None)
    await update.message.reply_text(
        "Hey! I'm Seoul Guide AI.\n\n"
        "Ask me anything about living in Korea, or send me a photo "
        "of something you can't read (bills, menus, signs, contracts).\n\n"
        "I'll tell you what it is and what to do about it."
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    add_to_history(user_id, "user", user_text)

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=get_history(user_id),
        )
        reply = response.content[0].text
        add_to_history(user_id, "assistant", reply)
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        await update.message.reply_text(
            "Sorry, something went wrong. Try again in a moment."
        )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    caption = update.message.caption or "What is this? Please explain and tell me what to do."

    # Download the largest available photo
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    image_bytes = await file.download_as_bytearray()

    # Resize to save tokens
    resized = resize_image(bytes(image_bytes))
    b64_image = base64.b64encode(resized).decode("utf-8")

    user_content = [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": b64_image,
            },
        },
        {"type": "text", "text": caption},
    ]

    add_to_history(user_id, "user", user_content)

    await update.message.reply_text("Looking at your photo...")

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=get_history(user_id),
        )
        reply = response.content[0].text
        add_to_history(user_id, "assistant", reply)
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Claude Vision API error: {e}")
        await update.message.reply_text(
            "Sorry, I couldn't process that image. Try again or send a clearer photo."
        )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversations.pop(user_id, None)
    await update.message.reply_text("Conversation reset. Ask me anything!")


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info("Seoul Guide AI bot started")
    app.run_polling()


if __name__ == "__main__":
    main()

import os
import io
import json
import base64
import logging
from datetime import datetime, timezone
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
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_CHAT_ID", "0"))
COMMUNITY_GROUP_LINK = os.environ.get("COMMUNITY_GROUP_LINK", "")

SYSTEM_PROMPT = Path(__file__).parent.joinpath("system_prompt.md").read_text()
FEEDBACK_DIR = Path(__file__).parent / "feedback"
FEEDBACK_DIR.mkdir(exist_ok=True)

BOT_USERNAME = None  # Set on startup

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Per-user conversation history (in-memory, resets on restart)
conversations: dict[int, list[dict]] = {}
MAX_HISTORY = 20


def get_history(user_id: int) -> list[dict]:
    if user_id not in conversations:
        conversations[user_id] = []
    return conversations[user_id]


def add_to_history(user_id: int, role: str, content):
    history = get_history(user_id)
    history.append({"role": role, "content": content})
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


def is_group_chat(update: Update) -> bool:
    return update.effective_chat.type in ("group", "supergroup")


def is_bot_mentioned(update: Update) -> bool:
    """Check if the bot is mentioned in a group message."""
    if not BOT_USERNAME:
        return False
    text = update.message.text or update.message.caption or ""
    return f"@{BOT_USERNAME}" in text


def share_link() -> str:
    """Generate a share deep link for the bot."""
    if BOT_USERNAME:
        return f"\n\n---\nKnow someone in Korea? Share this bot: https://t.me/{BOT_USERNAME}"
    return ""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversations.pop(user_id, None)

    group_line = ""
    if COMMUNITY_GROUP_LINK:
        group_line = f"\nJoin our community: {COMMUNITY_GROUP_LINK}\n"

    await update.message.reply_text(
        "Hey! I'm Seoul Guide AI.\n\n"
        "Ask me anything about living in Korea, or send me a photo "
        "of something you can't read (bills, menus, signs, contracts).\n\n"
        "I'll tell you what it is and what to do about it.\n"
        f"{group_line}\n"
        "Commands:\n"
        "/reset - Start a new conversation\n"
        "/feedback - Submit a correction or tip"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # In groups, only respond when mentioned
    if is_group_chat(update) and not is_bot_mentioned(update):
        return

    user_id = update.effective_user.id
    user_text = update.message.text

    # Strip bot mention from text in groups
    if is_group_chat(update) and BOT_USERNAME:
        user_text = user_text.replace(f"@{BOT_USERNAME}", "").strip()

    if not user_text:
        return

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
        await update.message.reply_text(reply + share_link())
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        await update.message.reply_text(
            "Sorry, something went wrong. Try again in a moment."
        )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # In groups, only respond when mentioned in caption
    if is_group_chat(update) and not is_bot_mentioned(update):
        return

    user_id = update.effective_user.id
    caption = update.message.caption or "What is this? Please explain and tell me what to do."

    # Strip bot mention from caption in groups
    if is_group_chat(update) and BOT_USERNAME:
        caption = caption.replace(f"@{BOT_USERNAME}", "").strip() or "What is this? Please explain and tell me what to do."

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    image_bytes = await file.download_as_bytearray()

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
        await update.message.reply_text(reply + share_link())
    except Exception as e:
        logger.error(f"Claude Vision API error: {e}")
        await update.message.reply_text(
            "Sorry, I couldn't process that image. Try again or send a clearer photo."
        )


async def feedback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = " ".join(context.args) if context.args else ""

    if not text:
        await update.message.reply_text(
            "Usage: /feedback <your correction or tip>\n\n"
            "Example: /feedback The gas bill payment info is outdated. "
            "You can now pay through Kakao Pay directly."
        )
        return

    # Save feedback to file
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user.id,
        "username": user.username or "",
        "first_name": user.first_name or "",
        "text": text,
        "chat_type": update.effective_chat.type,
    }

    filename = f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{user.id}.json"
    (FEEDBACK_DIR / filename).write_text(json.dumps(entry, ensure_ascii=False, indent=2))

    logger.info(f"Feedback from {user.id} (@{user.username}): {text}")

    # Notify admin
    if ADMIN_CHAT_ID:
        admin_msg = (
            f"New feedback from @{user.username or user.first_name} "
            f"(ID: {user.id}):\n\n{text}"
        )
        try:
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg)
        except Exception as e:
            logger.error(f"Failed to notify admin: {e}")

    await update.message.reply_text(
        "Thanks for the feedback! We'll review it and update our knowledge base."
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversations.pop(user_id, None)
    await update.message.reply_text("Conversation reset. Ask me anything!")


async def post_init(application: Application):
    """Fetch bot username after startup."""
    global BOT_USERNAME
    bot = await application.bot.get_me()
    BOT_USERNAME = bot.username
    logger.info(f"Bot started as @{BOT_USERNAME}")


def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("feedback", feedback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info("Seoul Guide AI bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

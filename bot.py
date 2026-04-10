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
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
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
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Pain signal keywords — used to tag high-intensity queries
PAIN_SIGNALS: dict[str, list[str]] = {
    "urgency": ["emergency", "urgent", "asap", "right now", "today", "help me", "stuck",
                 "deadline", "leaving in", "expiring", "last day"],
    "financial": ["deposit", "refund", "scam", "fraud", "won't pay", "lost money",
                   "보증금", "사기", "jeonse", "전세"],
    "legal": ["police", "lawyer", "court", "immigration", "fine", "penalty", "arrested",
              "contract", "sued", "violation", "overstay"],
    "medical": ["hospital", "emergency room", "ambulance", "injury", "sick", "pain",
                "doctor", "pharmacy", "insurance claim", "병원", "응급"],
    "bureaucratic": ["rejected", "denied", "won't accept", "expired", "missed deadline",
                      "wrong document", "application failed", "거부"],
    "distress": ["don't know what to do", "no one to ask", "alone", "scared", "desperate",
                  "please help", "confused", "lost", "stranded"],
}


def detect_pain_signals(text: str) -> list[str]:
    """Return list of matched pain signal categories."""
    text_lower = text.lower()
    return [category for category, keywords in PAIN_SIGNALS.items()
            if any(kw in text_lower for kw in keywords)]


def log_query(
    user_id: int,
    chat_type: str,
    msg_type: str,
    user_text: str,
    response_text: str,
    has_photo: bool = False,
):
    """Append a query log entry to today's JSONL file."""
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "chat_type": chat_type,
        "msg_type": msg_type,
        "user_text": user_text,
        "has_photo": has_photo,
        "pain_signals": detect_pain_signals(user_text),
        "response_excerpt": response_text[:200],
    }
    log_file = LOGS_DIR / f"queries_{datetime.now(timezone.utc).strftime('%Y%m%d')}.jsonl"
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.error(f"Failed to write query log: {e}")

BOT_USERNAME = None  # Set on startup

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# Per-user conversation history (in-memory, resets on restart)
conversations: dict[int, list[dict]] = {}
MAX_HISTORY = 20

# Per-user profile (stage selection, metadata)
user_profiles: dict[int, dict] = {}


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

    keyboard = [
        [InlineKeyboardButton("Planning to move to Korea", callback_data="stage_planning")],
        [InlineKeyboardButton("Just arrived (first 2 months)", callback_data="stage_arrived")],
        [InlineKeyboardButton("Already living here", callback_data="stage_living")],
        [InlineKeyboardButton("Leaving Korea soon", callback_data="stage_leaving")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Hey! I'm Seoul Guide AI -- think of me as your Korean friend "
        "who knows how everything works here.\n\n"
        "To give you the best help, tell me where you're at:",
        reply_markup=reply_markup,
    )


async def handle_stage_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    stage = query.data  # e.g. "stage_planning"

    user_profiles[user_id] = {
        "stage": stage,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    group_line = ""
    if COMMUNITY_GROUP_LINK:
        group_line = f"\nJoin our community: {COMMUNITY_GROUP_LINK}\n"

    welcome_messages = {
        "stage_planning": (
            "Nice, so you're thinking about moving to Korea! Great choice.\n\n"
            "I can help you with:\n"
            "- Visa types and what documents to prepare\n"
            "- Finding housing from abroad (tips that actually work)\n"
            "- What to bring vs. what to buy here\n\n"
            "Got a document you're not sure about? Snap a photo and send it "
            "to me -- I'll translate and explain it."
        ),
        "stage_arrived": (
            "Welcome to Korea! The first weeks are a whirlwind, "
            "but I've got you.\n\n"
            "Here's the critical sequence you need to nail:\n"
            "SIM card -> ARC (Alien Registration Card) -> Bank account -> Phone plan\n\n"
            "Want me to walk you through it step by step? Just ask.\n\n"
            "And whenever you see something you can't read -- a sign, a bill, "
            "a form at the office -- just take a photo and send it here. "
            "I'll tell you exactly what it says and what to do."
        ),
        "stage_living": (
            "Hey, fellow Korea resident! You know the basics, "
            "so let's make daily life easier.\n\n"
            "I'm here for:\n"
            "- Translating anything you photograph (bills, notices, menus, mail)\n"
            "- Answering random \"how does this work in Korea\" questions\n"
            "- Navigating bureaucracy when things get confusing\n\n"
            "Just text me a question or send a photo anytime."
        ),
        "stage_leaving": (
            "Leaving Korea? There's more to wrap up than you'd think. "
            "Let me help you not leave money on the table.\n\n"
            "Key things to handle:\n"
            "- National pension refund (you can get it back!)\n"
            "- Deposit (보증금) recovery\n"
            "- Insurance cancellation\n"
            "- Bank account closure / overseas transfer\n\n"
            "Ask me about any of these, or send a photo of paperwork "
            "you need help with. I also have a departure checklist if you want it."
        ),
    }

    message = welcome_messages.get(stage, "Welcome!")
    commands = (
        "\n\nCommands:\n"
        "/reset - Start a new conversation\n"
        "/feedback - Submit a correction or tip"
    )

    await query.edit_message_text(
        text=message + group_line + commands + share_link()
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
        log_query(user_id, update.effective_chat.type, "text", user_text, reply)
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
        log_query(user_id, update.effective_chat.type, "photo", caption, reply, has_photo=True)
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


async def export_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send today's query log to admin as a file."""
    if update.effective_user.id != ADMIN_CHAT_ID:
        return

    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    log_file = LOGS_DIR / f"queries_{today}.jsonl"

    if not log_file.exists() or log_file.stat().st_size == 0:
        await update.message.reply_text("No logs for today yet.")
        return

    await update.message.reply_document(
        document=open(log_file, "rb"),
        filename=f"queries_{today}.jsonl",
        caption=f"Query logs for {today}",
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
    app.add_handler(CommandHandler("export", export_logs))
    app.add_handler(CallbackQueryHandler(handle_stage_selection))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    logger.info("Seoul Guide AI bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

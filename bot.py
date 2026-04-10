import os
import io
import json
import base64
import logging
from datetime import datetime, timedelta, timezone
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
CONTEXT_LIB = Path(__file__).parent / "context-library"
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


# --- Context-library retrieval ---

# Guide index: keyword triggers → file path
GUIDE_INDEX: list[tuple[list[str], str]] = [
    (["bank", "account", "계좌", "atm", "shinhan", "hana", "woori", "kb"],
     "banking/open-account.md"),
    (["card", "payment", "kakao pay", "naver pay", "wowpass", "credit card", "remittance", "send money", "wise", "송금"],
     "banking/cards-payments.md"),
    (["subway", "bus", "taxi", "ktx", "train", "t-money", "transportation", "transport", "교통"],
     "daily-life/transportation.md"),
    (["delivery", "baemin", "coupang eats", "배달", "package", "택배"],
     "daily-life/delivery.md"),
    (["utility", "utilities", "gas bill", "electricity", "water bill", "garbage", "recycling", "trash", "internet", "분리수거", "공과금"],
     "daily-life/utilities.md"),
    (["cost of living", "budget", "how much", "expensive", "salary", "생활비", "monthly cost", "rent price"],
     "daily-life/cost-of-living.md"),
    (["phone", "sim", "verification", "본인인증", "identity", "인증", "esim"],
     "daily-life/phone-verification.md"),
    (["hospital", "doctor", "clinic", "emergency", "ambulance", "sick", "injury", "병원", "english speaking doctor"],
     "healthcare/find-hospital.md"),
    (["insurance", "nhis", "health insurance", "보험", "national health"],
     "healthcare/insurance.md"),
    (["pharmacy", "medicine", "drug", "약국", "tylenol", "cold medicine", "fever", "pain relief", "상비약", "편의점 약"],
     "healthcare/pharmacy-essentials.md"),
    (["apartment", "housing", "rent", "studio", "officetel", "goshiwon", "집", "방", "zigbang", "dabang", "부동산"],
     "housing/find-apartment.md"),
    (["jeonse", "wolse", "전세", "월세", "deposit", "보증금", "lease", "landlord", "contract"],
     "housing/jeonse-wolse.md"),
    (["arrival", "first week", "just arrived", "moving to korea", "checklist", "what to do first"],
     "onboarding/arrival-checklist.md"),
    (["leaving korea", "departure", "pension refund", "퇴직", "severance", "연금", "going home", "last month"],
     "onboarding/departure-checklist.md"),
    (["arc", "alien registration", "residence card", "외국인등록"],
     "visa/arc-guide.md"),
    (["visa", "비자", "e-2", "e-7", "d-2", "f-1", "f-2", "f-5", "f-6", "d-10", "digital nomad", "overstay", "address report", "주소"],
     "visa/visa-types.md"),
    (["workplace", "office", "nunchi", "눈치", "hierarchy", "hoesik", "회식", "bullying", "hagwon", "teacher", "epik", "contract"],
     "workplace/culture-communication.md"),
    (["concert", "ticket", "kpop", "k-pop", "interpark", "melon ticket", "fansign", "music show", "music bank", "inkigayo", "idol"],
     "entertainment/kpop-concerts-tickets.md"),
    (["olive young", "oliveyoung", "올리브영", "k-beauty", "skincare", "sunscreen", "serum", "mask", "cosmetic", "makeup"],
     "shopping/oliveyoung-guide.md"),
]

# Pre-load all guide contents at startup
_guide_cache: dict[str, str] = {}

def _load_guide(path: str) -> str:
    if path not in _guide_cache:
        full = CONTEXT_LIB / path
        if full.exists():
            _guide_cache[path] = full.read_text()
        else:
            _guide_cache[path] = ""
    return _guide_cache[path]

def find_relevant_guides(text: str, max_guides: int = 2) -> str:
    """Match user text against guide index and return content of top matches."""
    text_lower = text.lower()
    scored: list[tuple[int, str]] = []
    for keywords, path in GUIDE_INDEX:
        hits = sum(1 for kw in keywords if kw in text_lower)
        if hits > 0:
            scored.append((hits, path))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:max_guides]
    if not top:
        return ""
    parts = []
    for _, path in top:
        content = _load_guide(path)
        if content:
            parts.append(f"\n--- Reference: {path} ---\n{content}")
    return "\n".join(parts)


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


# --- Proactive timeline reminders per stage ---

STAGE_REMINDERS: dict[str, list[tuple[timedelta, str]]] = {
    "stage_arrived": [
        (
            timedelta(days=1),
            "Hey! Have you gotten a SIM card yet? That's step 1. "
            "If you need help, just ask or send me a photo of whatever you're looking at.",
        ),
        (
            timedelta(days=3),
            "Quick check — have you booked your ARC appointment on HiKorea? "
            "The sooner you book, the sooner you get your bank account and phone plan sorted. "
            "Need help? Just ask.",
        ),
        (
            timedelta(days=7),
            "It's been a week! By now you should have: "
            "\u2705 SIM card, \u2705 ARC appointment booked. "
            "Next up: bank account (once ARC arrives). "
            "Send me a photo of any document you can't read.",
        ),
        (
            timedelta(days=14),
            "Two weeks in! Your ARC should be arriving soon. "
            "Once you have it, I can walk you through opening a bank account. "
            "Which bank are you thinking?",
        ),
        (
            timedelta(days=30),
            "One month in Korea! How's it going? "
            "If you haven't set up NHIS (health insurance) yet, now's the time. "
            "Ask me about it.",
        ),
    ],
    "stage_planning": [
        (
            timedelta(days=1),
            "Getting ready for Korea? The most important thing to sort out first is your visa. "
            "Tell me your situation and I'll help figure out which visa type fits.",
        ),
        (
            timedelta(days=7),
            "One week into planning! Have you checked out our arrival checklist? "
            "It covers everything you need to do in your first 60 days. "
            "Just ask 'arrival checklist' and I'll walk you through it.",
        ),
    ],
    "stage_leaving": [
        (
            timedelta(days=1),
            "Starting your departure prep? The #1 thing people forget: "
            "national pension refund (\uad6d\ubbfc\uc5f0\uae08). "
            "You can get ALL your contributions back. Ask me how.",
        ),
        (
            timedelta(days=7),
            "Reminder: give your landlord written notice (\ub0b4\uc6a9\uc99d\uba85) "
            "for deposit return. The earlier the better. "
            "Need help with the process? Just ask.",
        ),
    ],
    "stage_living": [
        (
            timedelta(days=1),
            "Remember — anytime you see something in Korean you can't read, "
            "just snap a photo and send it here. Bills, letters, signs, menus — "
            "I'll explain what it says and what to do.",
        ),
    ],
}


async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    """Job callback that sends a scheduled reminder message."""
    job = context.job
    await context.bot.send_message(
        chat_id=job.data["chat_id"],
        text=job.data["message"] + share_link(),
    )


def cancel_user_reminders(user_id: int, job_queue) -> int:
    """Cancel all pending reminder jobs for a user. Returns count of cancelled jobs."""
    prefix = f"reminder_{user_id}_"
    cancelled = 0
    for job in job_queue.jobs():
        if job.name and job.name.startswith(prefix):
            job.schedule_removal()
            cancelled += 1
    return cancelled


def schedule_stage_reminders(user_id: int, chat_id: int, stage: str, job_queue):
    """Schedule all reminders for a given stage."""
    reminders = STAGE_REMINDERS.get(stage, [])
    for delay, message in reminders:
        job_name = f"reminder_{user_id}_{int(delay.total_seconds())}"
        job_queue.run_once(
            send_reminder,
            when=delay,
            data={"chat_id": chat_id, "message": message},
            name=job_name,
        )
    if reminders:
        logger.info(
            f"Scheduled {len(reminders)} reminders for user {user_id} (stage={stage})"
        )


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
        "Hey! I'm Living in Korea -- think of me as your Korean friend "
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

    # Cancel any existing reminders, then schedule new ones for selected stage
    cancel_user_reminders(user_id, context.job_queue)
    chat_id = query.message.chat_id
    schedule_stage_reminders(user_id, chat_id, stage, context.job_queue)

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

    # Retrieve relevant guides based on user query
    guides_context = find_relevant_guides(user_text)
    system = SYSTEM_PROMPT
    if guides_context:
        system = SYSTEM_PROMPT + "\n\n## Reference Guides (use this info to answer)\n" + guides_context

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system=system,
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

    # Retrieve relevant guides based on caption
    guides_context = find_relevant_guides(caption)
    system = SYSTEM_PROMPT
    if guides_context:
        system = SYSTEM_PROMPT + "\n\n## Reference Guides (use this info to answer)\n" + guides_context

    try:
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            system=system,
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
    cancelled = cancel_user_reminders(user_id, context.job_queue)
    if cancelled:
        logger.info(f"Cancelled {cancelled} pending reminders for user {user_id}")
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

    logger.info("Living in Korea bot starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

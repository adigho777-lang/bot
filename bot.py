# -*- coding: utf-8 -*-
"""
EduUnlocked Key Generator Bot - @EduUnlocked_keys_bot
- Anyone can generate key BUT must be channel member first
- Channel: t.me/Edu_Unlocked
- Auto-deletes expired keys every hour
"""

import sys
import random
import string
import logging
import asyncio
from datetime import datetime, timezone, timedelta

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes
)
from telegram.error import BadRequest

import firebase_admin
from firebase_admin import credentials, firestore

# CONFIG
BOT_TOKEN = "8704845066:AAGGnpdDBeLakcFtWzppJtDA-ua9oVUlZ7c"
ADMIN_IDS = [1747637476]          # Admin IDs (can check/revoke keys)
FIREBASE_CRED_PATH = "serviceAccountKey.json"
CHANNEL_USERNAME = "@Edu_Unlocked"
CHANNEL_LINK = "https://t.me/Edu_Unlocked"

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

cred = credentials.Certificate(FIREBASE_CRED_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()


def generate_key() -> str:
    chars = string.ascii_uppercase + string.digits
    return f"NT-{''.join(random.choices(chars, k=8))}"


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


async def is_channel_member(bot, user_id: int) -> bool:
    """Check if user is member of the channel"""
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in [
            ChatMember.MEMBER,
            ChatMember.ADMINISTRATOR,
            ChatMember.OWNER,
        ]
    except BadRequest:
        return False
    except Exception as e:
        logger.error(f"Channel check error: {e}")
        return False


# ─── Auto-delete expired keys ─────────────────────────────────
async def cleanup_expired_keys(context: ContextTypes.DEFAULT_TYPE):
    try:
        now = datetime.now(timezone.utc)
        expired = db.collection('_app_keys').where('isUsed', '==', True).stream()
        deleted = 0
        for doc in expired:
            data = doc.to_dict()
            expires_at = data.get('expiresAt')
            if expires_at:
                exp = expires_at
                if hasattr(exp, 'tzinfo') and exp.tzinfo is None:
                    exp = exp.replace(tzinfo=timezone.utc)
                if now > exp:
                    doc.reference.delete()
                    deleted += 1
        if deleted > 0:
            logger.info(f"Auto-deleted {deleted} expired keys")
    except Exception as e:
        logger.error(f"Cleanup error: {e}")


# ─── /start ───────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    name = user.first_name or "Student"

    # Admins bypass channel check
    if is_admin(user.id):
        await _show_main_menu(update.message.reply_text, name, user.id)
        return

    # Check channel membership
    is_member = await is_channel_member(context.bot, user.id)

    if not is_member:
        keyboard = [
            [InlineKeyboardButton("📢 Join EduUnlocked Channel", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ I've Joined - Check Again", callback_data="check_membership")],
        ]
        await update.message.reply_text(
            f"👋 *Hello {name}!*\n\n"
            "🎓 *Welcome to EduUnlocked Bot*\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ *Step Required!*\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "To get your *Free Access Key*, you must:\n\n"
            "1️⃣ Join our Telegram Channel\n"
            "2️⃣ Come back and generate your key\n\n"
            "📢 *Why join?*\n"
            "   🔔 Get notified about new batches\n"
            "   📚 Free study materials\n"
            "   🎯 Exam tips & tricks\n\n"
            "👇 *Join the channel first:*",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # User is a member - show generate button
    await _show_main_menu(update.message.reply_text, name, user.id)


async def _show_main_menu(reply_func, name: str, user_id: int):
    keyboard = [[InlineKeyboardButton("🔑 Generate My Key", callback_data="genkey")]]
    if is_admin(user_id):
        keyboard.append([
            InlineKeyboardButton("📋 Check Key", callback_data="prompt_check"),
            InlineKeyboardButton("🗑️ Revoke Key", callback_data="prompt_revoke"),
        ])
        keyboard.append([
            InlineKeyboardButton("🧹 Clean Expired Keys", callback_data="cleanup"),
        ])

    await reply_func(
        f"👋 *Hello {name}!*\n\n"
        "🎓 *Welcome to EduUnlocked Bot*\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📱 *NextToppers Learning App*\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "� *Your key unlocks:*\n"
        "   📚 All Batches & Courses\n"
        "   🎥 Video Lectures\n"
        "   � PDF Notes\n"
        "   🏆 Live Classes\n\n"
        "⚠️ *Key Rules:*\n"
        "   ⏱️ Valid for *24 hours only*\n"
        "   🔒 Single-use per key\n"
        "   🗑️ Auto-deleted after expiry\n\n"
        "👇 *Tap below to get your key!*",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ─── Button Callbacks ─────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    user_id = user.id
    data = query.data

    if data == "check_membership":
        is_member = await is_channel_member(context.bot, user_id)
        if not is_member:
            keyboard = [
                [InlineKeyboardButton("� Join EduUnlocked Channel", url=CHANNEL_LINK)],
                [InlineKeyboardButton("✅ I've Joined - Check Again", callback_data="check_membership")],
            ]
            await query.edit_message_text(
                "❌ *Not a member yet!*\n\n"
                "You haven't joined the channel.\n\n"
                "Please join *@Edu_Unlocked* first, then click check again.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            name = user.first_name or "Student"
            keyboard = [[InlineKeyboardButton("🔑 Generate My Key", callback_data="genkey")]]
            if is_admin(user_id):
                keyboard.append([
                    InlineKeyboardButton("📋 Check Key", callback_data="prompt_check"),
                    InlineKeyboardButton("🗑️ Revoke Key", callback_data="prompt_revoke"),
                ])
            await query.edit_message_text(
                f"✅ *Welcome {name}!*\n\n"
                "🎉 You are now a channel member!\n\n"
                "You can now generate your access key.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    elif data == "genkey":
        # Check membership again before generating
        is_member = await is_channel_member(context.bot, user_id)
        if not is_member:
            keyboard = [
                [InlineKeyboardButton("📢 Join EduUnlocked Channel", url=CHANNEL_LINK)],
                [InlineKeyboardButton("✅ I've Joined - Check Again", callback_data="check_membership")],
            ]
            await query.edit_message_text(
                "❌ *Channel membership required!*\n\n"
                "You must join *@Edu_Unlocked* to generate a key.",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        key = generate_key()
        db.collection('_app_keys').document(key).set({
            'key': key,
            'isUsed': False,
            'createdAt': firestore.SERVER_TIMESTAMP,
            'createdBy': str(user_id),
            'createdByUsername': user.username or '',
            'expiresAt': None,
            'usedAt': None,
        })

        keyboard = [
            [InlineKeyboardButton("🔑 Generate Another Key", callback_data="genkey")],
            [InlineKeyboardButton("🏠 Back to Menu", callback_data="back_menu")],
        ]
        await query.edit_message_text(
            "✅ *Key Generated Successfully!*\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"�  `{key}`\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "📋 *How to use:*\n"
            "1️⃣ Copy the key above\n"
            "2️⃣ Open *NextToppers App*\n"
            "3️⃣ Enter the key on Key screen\n"
            "4️⃣ Enjoy 24 hours of access! 🎉\n\n"
            "⏱️ *Expires: 24 hours after first use*\n"
            "🗑️ *Auto-deleted from system after expiry*",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "back_menu":
        name = user.first_name or "Student"
        await _show_main_menu(query.edit_message_text, name, user_id)

    elif data == "prompt_check":
        if not is_admin(user_id): return
        await query.edit_message_text(
            "� *Check Key Status*\n\nSend: `/checkkey NT-XXXXXXXX`",
            parse_mode='Markdown'
        )

    elif data == "prompt_revoke":
        if not is_admin(user_id): return
        await query.edit_message_text(
            "🗑️ *Revoke a Key*\n\nSend: `/revokekey NT-XXXXXXXX`",
            parse_mode='Markdown'
        )

    elif data == "cleanup":
        if not is_admin(user_id): return
        await query.edit_message_text("🧹 *Cleaning expired keys...*", parse_mode='Markdown')
        await cleanup_expired_keys(context)
        await query.edit_message_text(
            "✅ *Cleanup Complete!*\n\nAll expired keys deleted from Firebase.",
            parse_mode='Markdown'
        )


# ─── /checkkey ────────────────────────────────────────────────
async def checkkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Not authorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: `/checkkey NT-XXXXXXXX`", parse_mode='Markdown')
        return

    key = context.args[0].strip().upper()
    doc = db.collection('_app_keys').document(key).get()
    if not doc.exists:
        await update.message.reply_text(f"❌ Key `{key}` not found.", parse_mode='Markdown')
        return

    d = doc.to_dict()
    is_used = d.get('isUsed', False)
    expires_at = d.get('expiresAt')

    if not is_used:
        status = "🟢 Fresh — not used yet"
    elif expires_at is None:
        status = "🟡 Used (expiry pending)"
    else:
        now = datetime.now(timezone.utc)
        exp = expires_at
        if hasattr(exp, 'tzinfo') and exp.tzinfo is None:
            exp = exp.replace(tzinfo=timezone.utc)
        if now < exp:
            remaining = exp - now
            hours = int(remaining.total_seconds() // 3600)
            mins = int((remaining.total_seconds() % 3600) // 60)
            status = f"🟡 Active — {hours}h {mins}m remaining"
        else:
            status = "🔴 Expired"

    await update.message.reply_text(
        f"🔍 *Key Status*\n\n🔑 `{key}`\n📊 {status}",
        parse_mode='Markdown'
    )


# ─── /revokekey ───────────────────────────────────────────────
async def revokekey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Not authorized.")
        return
    if not context.args:
        await update.message.reply_text("Usage: `/revokekey NT-XXXXXXXX`", parse_mode='Markdown')
        return

    key = context.args[0].strip().upper()
    doc_ref = db.collection('_app_keys').document(key)
    if not doc_ref.get().exists:
        await update.message.reply_text(f"❌ Key `{key}` not found.", parse_mode='Markdown')
        return

    doc_ref.delete()
    await update.message.reply_text(
        f"✅ Key `{key}` revoked and deleted! 🗑️", parse_mode='Markdown')


async def error_handler(update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")


async def run_bot():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("checkkey", checkkey))
    app.add_handler(CommandHandler("revokekey", revokekey))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_error_handler(error_handler)

    # Auto cleanup every hour
    app.job_queue.run_repeating(cleanup_expired_keys, interval=3600, first=60)

    logger.info("Bot running - @EduUnlocked_keys_bot")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )
    await asyncio.Event().wait()


if __name__ == '__main__':
    asyncio.run(run_bot())

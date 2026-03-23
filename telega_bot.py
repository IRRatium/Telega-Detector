#!/usr/bin/env python3
"""
Telega Detector Bot
Проверяет, использует ли пользователь Telega (VK)
"""

import time
import logging
import requests
from functools import lru_cache
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ─── Config ───────────────────────────────────────────────────────────────────

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

CALLS_BASE_URL = "https://calls.okcdn.ru"
CALLS_API_KEY  = "CHKIPMKGDIHBABABA"
SESSION_DATA   = '{"device_id":"telega_alert","version":2,"client_version":"android_8","client_type":"SDK_ANDROID"}'

CACHE_TTL = 6 * 60 * 60  # 6 часов
_cache: dict[str, tuple[bool | None, float]] = {}

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
log = logging.getLogger(__name__)

# ─── Telega lookup ────────────────────────────────────────────────────────────

def _get_session_key() -> str | None:
    """Анонимный логин в OK Calls API."""
    try:
        r = requests.post(
            f"{CALLS_BASE_URL}/api/auth/anonymLogin",
            data={
                "application_key": CALLS_API_KEY,
                "session_data": SESSION_DATA,
            },
            headers={"Accept": "application/json"},
            timeout=12,
        )
        r.raise_for_status()
        return r.json().get("session_key") or None
    except Exception as e:
        log.warning(f"anonymLogin failed: {e}")
        return None


def _query_external_id(session_key: str, user_id: int) -> bool | None:
    """Проверяем user_id через getOkIdsByExternalIds."""
    try:
        r = requests.post(
            f"{CALLS_BASE_URL}/api/vchat/getOkIdsByExternalIds",
            data={
                "application_key": CALLS_API_KEY,
                "session_key": session_key,
                "externalIds": f'[{{"id":"{user_id}","ok_anonym":false}}]',
            },
            headers={"Accept": "application/json"},
            timeout=12,
        )
        r.raise_for_status()
        ids = r.json().get("ids") or []
        for item in ids:
            ext = (item or {}).get("external_user_id") or {}
            if str(ext.get("id") or "") == str(user_id):
                return True
        return False
    except Exception as e:
        log.warning(f"getOkIdsByExternalIds failed: {e}")
        return None


def is_telega_user(user_id: int) -> bool | None:
    """
    Возвращает:
      True  — использует Telega
      False — не использует
      None  — не удалось проверить (ошибка API)
    """
    key = str(user_id)
    cached = _cache.get(key)
    if cached is not None:
        value, ts = cached
        if time.time() - ts < CACHE_TTL:
            log.info(f"Cache hit for {user_id}: {value}")
            return value

    session_key = _get_session_key()
    if not session_key:
        return None

    result = _query_external_id(session_key, user_id)
    if result is not None:
        _cache[key] = (result, time.time())
    return result

# ─── Bot handlers ─────────────────────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔍 *Telega IQ Detector*\n\n"
        "Отправь мне:\n"
        "• Числовой Telegram ID: `123456789`\n"
        "• Юзернейм: `@username` (нужен числовой ID)\n"
        "• Перешли сообщение от пользователя\n\n"
        "Узнаем, хватает ли у него IQ 🧠",
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ℹ️ *Как пользоваться*\n\n"
        "1. Узнай числовой ID пользователя (через @userinfobot)\n"
        "2. Отправь его мне: `123456789`\n"
        "3. Или перешли любое сообщение от нужного человека\n\n"
        "Результат придёт через пару секунд ⚡",
        parse_mode="Markdown",
    )


async def handle_forward(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Обработка пересланных сообщений."""
    msg = update.message
    if not msg.forward_from:
        await msg.reply_text("❌ Не удалось получить ID из пересланного сообщения.\nВозможно, у пользователя закрыт форвард. Введи ID вручную.")
        return

    user_id = msg.forward_from.id
    first_name = msg.forward_from.first_name or "Пользователь"
    await _check_and_reply(msg, user_id, first_name)


async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Обработка числового ID."""
    text = update.message.text.strip()

    # Убираем @ если юзернейм
    if text.startswith("@"):
        await update.message.reply_text(
            "⚠️ Username не работает напрямую — нужен числовой ID.\n"
            "Используй @userinfobot чтобы узнать его.",
        )
        return

    # Проверяем что это число
    try:
        user_id = int(text)
    except ValueError:
        await update.message.reply_text("❌ Это не похоже на Telegram ID. Пришли число, например: `123456789`", parse_mode="Markdown")
        return

    if user_id <= 0:
        await update.message.reply_text("❌ ID должен быть положительным числом.")
        return

    await _check_and_reply(update.message, user_id, f"ID {user_id}")


async def _check_and_reply(message, user_id: int, display_name: str):
    """Общая логика проверки и ответа."""
    wait_msg = await message.reply_text("⏳ Проверяю...")

    result = is_telega_user(user_id)

    if result is True:
        text = (
            f"🤡 *{display_name}*\n\n"
            f"Использует **Telega** от VK\n\n"
            f"IQ: **< 30** 🧠📉\n"
            f"Доброволец слежки, данные уже у кого надо 👀\n\n"
            f"_[dontusetelega.lol]_"
        )
    elif result is False:
        text = (
            f"✅ *{display_name}*\n\n"
            f"Telega **не использует**\n\n"
            f"IQ: **> 30** 🧠📈\n"
            f"Нормальный человек, уважаю 👍"
        )
    else:
        text = (
            f"⚠️ *{display_name}*\n\n"
            f"Не удалось проверить — API недоступен.\n"
            f"Попробуй позже."
        )

    await wait_msg.delete()
    await message.reply_text(text, parse_mode="Markdown")

# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Укажи BOT_TOKEN в переменной окружения или в коде!")
        return

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))

    # Пересланные сообщения
    app.add_handler(MessageHandler(filters.FORWARDED, handle_forward))

    # Числовой ID текстом
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    log.info("Bot started 🤖")
    app.run_polling()


if __name__ == "__main__":
    main()

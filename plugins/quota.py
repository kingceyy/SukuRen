# SukunaRenamer — gestion des quotas (pub + premium admin)

from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import (
    InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, CallbackQuery
)

from helper.database import zeexdev
from config import Config, rkn

import datetime


def _fmt_expiry(next_expiry):
    if not next_expiry:
        return "Aucun quota gratuit en attente d'expiration."
    delta = next_expiry - datetime.datetime.now()
    hours = max(0, int(delta.total_seconds() // 3600))
    minutes = max(0, int((delta.total_seconds() % 3600) // 60))
    return f"⏳ Prochain lot gratuit expire dans : {hours}h {minutes}min"


def webapp_quota_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Obtenir des quotas (regarder une pub)", web_app=WebAppInfo(url=Config.WEBAPP_URL))],
        [InlineKeyboardButton("👑 Plans premium", callback_data="upgrade")],
        [InlineKeyboardButton("◀️ Retour", callback_data="start")]
    ])


# ===================== COMMANDE UTILISATEUR =====================

@Client.on_message(filters.private & filters.command(["mesquotas", "quotas", "myquota"]))
async def mesquotas(client, message):
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    user_id = message.from_user.id
    if not await zeexdev.is_user_exist(user_id):
        return await message.reply_text("Fais d'abord /start pour invoquer le domaine.")

    balance = await zeexdev.get_quota_balance(user_id)
    text = rkn.QUOTA_INFO_TXT.format(
        user=message.from_user.mention,
        free=balance["free"],
        premium=balance["premium"],
        total=balance["total"],
        expiry_line=_fmt_expiry(balance["next_expiry"])
    )
    await message.reply_text(text, reply_markup=webapp_quota_button())


@Client.on_callback_query(filters.regex("^mesquotas$"))
async def mesquotas_cb(client, query: CallbackQuery):
    await client.send_chat_action(query.message.chat.id, ChatAction.TYPING)
    user_id = query.from_user.id
    balance = await zeexdev.get_quota_balance(user_id)
    text = rkn.QUOTA_INFO_TXT.format(
        user=query.from_user.mention,
        free=balance["free"],
        premium=balance["premium"],
        total=balance["total"],
        expiry_line=_fmt_expiry(balance["next_expiry"])
    )
    await query.message.edit_text(text, reply_markup=webapp_quota_button())


@Client.on_callback_query(filters.regex("^get_quota$"))
async def get_quota_cb(client, query: CallbackQuery):
    await client.send_chat_action(query.message.chat.id, ChatAction.TYPING)
    text = rkn.QUOTA_EARN_INTRO_TXT.format(per_ad=Config.QUOTA_PER_AD, expiry=Config.QUOTA_EXPIRY_HOURS)
    await query.message.edit_text(text, reply_markup=webapp_quota_button())


# ===================== COMMANDE ADMIN =====================

@Client.on_message(filters.private & filters.command("quota") & filters.user(Config.ADMIN))
async def quota_admin(client, message):
    args = message.text.split()

    if len(args) < 2:
        return await message.reply_text(rkn.QUOTA_ADMIN_USAGE)

    action = args[1].lower()

    if action == "info":
        if len(args) != 3:
            return await message.reply_text("Utilisation : `/quota info user_id`")
        try:
            target_id = int(args[2])
        except ValueError:
            return await message.reply_text("ID utilisateur invalide.")
        if not await zeexdev.is_user_exist(target_id):
            return await message.reply_text("Cet utilisateur n'existe pas dans la base.")
        balance = await zeexdev.get_quota_balance(target_id)
        return await message.reply_text(
            f"👤 <code>{target_id}</code>\n"
            f"🩸 Gratuits : <code>{balance['free']}</code>\n"
            f"👑 Premium : <code>{balance['premium']}</code>\n"
            f"⚡ Total : <code>{balance['total']}</code>\n"
            f"{_fmt_expiry(balance['next_expiry'])}"
        )

    if action not in ("add", "remove", "set"):
        return await message.reply_text(rkn.QUOTA_ADMIN_USAGE)

    if len(args) != 4:
        return await message.reply_text(rkn.QUOTA_ADMIN_USAGE)

    try:
        target_id = int(args[2])
        amount = int(args[3])
    except ValueError:
        return await message.reply_text("ID utilisateur ou montant invalide.")

    if not await zeexdev.is_user_exist(target_id):
        return await message.reply_text("Cet utilisateur n'a jamais démarré le bot (/start).")

    if amount < 0:
        return await message.reply_text("Le montant doit être positif.")

    if action == "add":
        await zeexdev.add_premium_quota(target_id, amount)
    elif action == "remove":
        await zeexdev.remove_premium_quota(target_id, amount)
    elif action == "set":
        await zeexdev.set_premium_quota(target_id, amount)

    balance = await zeexdev.get_quota_balance(target_id)
    await message.reply_text(
        f"✅ Fait. Solde premium de <code>{target_id}</code> : <code>{balance['premium']}</code> "
        f"(total disponible : <code>{balance['total']}</code>)"
    )

    try:
        await client.send_message(
            target_id,
            f"👑 L'administrateur t'a crédité des quotas premium (n'expirent jamais).\n"
            f"Ton nouveau solde premium : <code>{balance['premium']}</code>"
        )
    except Exception:
        pass

from pyrogram import Client, filters, enums 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import UserNotParticipant
import datetime

from config import Config
from helper.database import zeexdev

async def not_subscribed(_, client, message):
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await zeexdev.add_user(client, message)
    if not Config.FORCE_SUB:
        return False
    try:             
        user = await client.get_chat_member(Config.FORCE_SUB, message.from_user.id) 
        if user.status in {enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.LEFT}:
            return True 
        else:
            return False                
    except UserNotParticipant:
        pass
    return True

async def handle_banned_user_status(bot, message):
    await bot.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await zeexdev.add_user(bot, message) 
    user_id = message.from_user.id
    ban_status = await zeexdev.get_ban_status(user_id)
    if ban_status["is_banned"]:
        if (datetime.date.today() - datetime.date.fromisoformat(ban_status["banned_on"])).days > ban_status["ban_duration"]:
            await zeexdev.remove_ban(user_id)
        else:
            return await message.reply_text("Désolé, vous êtes banni ! Veuillez contacter @ZeeXDevBot") 
    await message.continue_propagation()
    
@Client.on_message(filters.private)
async def _(bot, message):
    await handle_banned_user_status(bot, message)
    
@Client.on_message(filters.private & filters.create(not_subscribed))
async def forces_sub(client, message):
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    buttons = [
        [InlineKeyboardButton(text="📢 Rejoindre le canal 📢", url=f"https://t.me/Godanimes")],
        [InlineKeyboardButton(text="🔄 Rejoins le 2eme", url=f"https://t.me/{Config.FORCE_SUB}")]
    ]
    text = "**Vous n'êtes pas membre de notre canal. Veuillez rejoindre notre canal de mise à jour pour continuer.**"
    try:
        user = await client.get_chat_member(Config.FORCE_SUB, message.from_user.id)    
        if user.status == enums.ChatMemberStatus.BANNED:                                   
            return await client.send_message(message.from_user.id, text="Désolé, vous êtes banni et ne pouvez pas utiliser ce bot")  
        elif user.status == enums.ChatMemberStatus.LEFT:
            return await message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    except UserNotParticipant:                       
        return await message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    return await message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
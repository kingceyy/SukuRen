import random
import asyncio
import datetime
import pytz
import time
import psutil
import shutil

from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery, WebAppInfo

from helper.database import zeexdev
from config import Config, rkn
from helper.utils import humanbytes
from plugins import __version__ as _bot_version_, __developer__, __database__, __library__, __language__, __programer__

upgrade_button = InlineKeyboardMarkup([[        
        InlineKeyboardButton('👑 Négocier avec l\'admin', url="https://t.me/Kingcey"),
         ],[
        InlineKeyboardButton("⚡ Obtenir des quotas gratuits", web_app=WebAppInfo(url=Config.WEBAPP_URL))
        ],[
        InlineKeyboardButton("Retour", callback_data = "start")
]])

upgrade_trial_button = InlineKeyboardMarkup([[        
        InlineKeyboardButton('👑 Négocier avec l\'admin', url="https://t.me/Kingcey"),
         ],[
        InlineKeyboardButton("essai premium - 12 heures ✓", callback_data = "give_trial"),
        ],[
        InlineKeyboardButton("⚡ Obtenir des quotas gratuits", web_app=WebAppInfo(url=Config.WEBAPP_URL))
        ],[
        InlineKeyboardButton("Retour", callback_data = "start")
]])

start_button = InlineKeyboardMarkup([[        
        InlineKeyboardButton('Mises à jour', url='https://t.me/itz_kingcey'),
        InlineKeyboardButton('Support', url='https://t.me/+u5qxRjapSF05YTBk')
        ],[
        InlineKeyboardButton('À propos', callback_data='about'),
        InlineKeyboardButton('Aide', callback_data='help')
        ],[
        InlineKeyboardButton('⚡ Mes quotas', callback_data='mesquotas'),
        InlineKeyboardButton('👑 Premium', callback_data='upgrade')
         ]])
        
@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    await zeexdev.add_user(client, message) 
    if Config.RKN_PIC:
        await message.reply_photo(Config.RKN_PIC, caption=rkn.START_TXT.format(user.mention), reply_markup=start_button)       
    else:
        await message.reply_text(text=rkn.START_TXT.format(user.mention), reply_markup=start_button, disable_web_page_preview=True)

@Client.on_message(filters.private & filters.command("myplan"))
async def myplan(client, message):
    user_id = message.from_user.id
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    user = message.from_user.mention
    balance = await zeexdev.get_quota_balance(user_id)
    user_data = await zeexdev.get_user_data(user_id)
    type = user_data.get('usertype', "Gratuit") if user_data else "Gratuit"

    if await zeexdev.has_premium_access(user_id):
        data = await zeexdev.get_user(user_id)
        expiry_str_in_ist = data.get("expiry_time")
        time_left_str = expiry_str_in_ist - datetime.datetime.now()
        await message.reply_text(
            f"👤 utilisateur :- {user}\n⚡ ID utilisateur :- <code>{user_id}</code>\n"
            f"Plan :- <code>{type}</code>\n\n"
            f"🩸 Quotas gratuits :- <code>{balance['free']}</code>\n"
            f"👑 Quotas premium :- <code>{balance['premium']}</code>\n"
            f"⚡ Total :- <code>{balance['total']}</code>\n\n"
            f"⏰ Temps restant premium : {time_left_str}\n⌛️ Date d'expiration : {expiry_str_in_ist}",
            quote=True
        )
    else:
        await message.reply_text(
            f"👤 utilisateur :- {user}\n⚡ ID utilisateur :- <code>{user_id}</code>\n"
            f"Plan :- <code>{type}</code>\n\n"
            f"🩸 Quotas gratuits :- <code>{balance['free']}</code>\n"
            f"👑 Quotas premium :- <code>{balance['premium']}</code>\n"
            f"⚡ Total :- <code>{balance['total']}</code>\n\n"
            f"Si tu veux plus de quotas, regarde une pub ou passe premium 👇",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⚡ Obtenir des quotas", web_app=WebAppInfo(url=Config.WEBAPP_URL))
            ],[
                InlineKeyboardButton("👑 voir les plans premium 👑", callback_data='upgrade')
            ]]),
            quote=True
        )


@Client.on_message(filters.private & filters.command("plans"))
async def plans(client, message):
    user = message.from_user
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    free_trial_status = await zeexdev.get_free_trial_status(user.id)
    if not await zeexdev.has_premium_access(user.id):
        if not free_trial_status:
            await message.reply_text(text=rkn.UPGRADE.format(Config.QUOTA_EXPIRY_HOURS), reply_markup=upgrade_trial_button, disable_web_page_preview=True)
        else:
            await message.reply_text(text=rkn.UPGRADE.format(Config.QUOTA_EXPIRY_HOURS), reply_markup=upgrade_button, disable_web_page_preview=True)
    else:
        await message.reply_text(text=rkn.UPGRADE.format(Config.QUOTA_EXPIRY_HOURS), reply_markup=upgrade_button, disable_web_page_preview=True)
   
  
@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data 
    if data == "start":
        await client.send_chat_action(query.message.chat.id, ChatAction.TYPING)
        await query.message.edit_text(
            text=rkn.START_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=start_button)
        
    elif data == "help":
        await client.send_chat_action(query.message.chat.id, ChatAction.TYPING)
        await query.message.edit_text(
            text=rkn.HELP_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("miniature", callback_data="thumbnail"),
                InlineKeyboardButton("légende", callback_data="caption")
                ],[          
                InlineKeyboardButton("nom de fichier personnalisé", callback_data="custom_file_name")    
                ],[          
                InlineKeyboardButton("à propos", callback_data="about"),
                InlineKeyboardButton("métadonnées", callback_data="digital_meta_data")
                                     ],[
                InlineKeyboardButton("Retour", callback_data="start")
                  ]]))         
        
    elif data == "about":
        await client.send_chat_action(query.message.chat.id, ChatAction.TYPING)
        await query.message.edit_text(
            text=rkn.ABOUT_TXT.format(client.mention, __developer__, __programer__, __library__, __language__, __database__, _bot_version_),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("CineFlixi", callback_data="source_code"),
                InlineKeyboardButton("état du bot", callback_data="bot_status")
                ],[
                InlineKeyboardButton("statut en direct", callback_data="live_status"),
                InlineKeyboardButton("amélioration", callback_data="upgrade")
                ],[   
                InlineKeyboardButton("Retour", callback_data="start")
           ]]))    
        
    elif data == "upgrade":
        await client.send_chat_action(query.message.chat.id, ChatAction.TYPING)
        free_trial_status = await zeexdev.get_free_trial_status(query.from_user.id)
        if not await zeexdev.has_premium_access(query.from_user.id):
            if not free_trial_status:
                await query.message.edit_text(text=rkn.UPGRADE.format(Config.QUOTA_EXPIRY_HOURS), disable_web_page_preview=True, reply_markup=upgrade_trial_button)   
            else:
                await query.message.edit_text(text=rkn.UPGRADE.format(Config.QUOTA_EXPIRY_HOURS), disable_web_page_preview=True, reply_markup=upgrade_button)
        else:
            await query.message.edit_text(text=rkn.UPGRADE.format(Config.QUOTA_EXPIRY_HOURS), disable_web_page_preview=True, reply_markup=upgrade_button)
           
    elif data == "give_trial":
        await client.send_chat_action(query.message.chat.id, ChatAction.TYPING)
        await query.message.delete()
        free_trial_status = await zeexdev.get_free_trial_status(query.from_user.id)
        if not free_trial_status:            
            await zeexdev.give_free_trail(query.from_user.id)
            new_text = "<b>👹 Ton essai premium a été activé pour 12 heures, et 50 quotas premium t'ont été offerts.</b>"
        else:
            new_text = "<b>🤣 Tu as déjà utilisé ton essai gratuit. Passe premium ici 👉 /plans</b>"
        await client.send_message(query.from_user.id, text=new_text)

    elif data == "thumbnail":
        await client.send_chat_action(query.message.chat.id, ChatAction.TYPING)
        await query.message.edit_text(
            text=rkn.THUMBNAIL,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
             InlineKeyboardButton("Retour", callback_data="help")]])) 
      
    elif data == "caption":
        await client.send_chat_action(query.message.chat.id, ChatAction.TYPING)
        await query.message.edit_text(
            text=rkn.CAPTION,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
             InlineKeyboardButton("Retour", callback_data="help")]])) 
      
    elif data == "custom_file_name":
        await client.send_chat_action(query.message.chat.id, ChatAction.TYPING)
        await query.message.edit_text(
            text=rkn.CUSTOM_FILE_NAME,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
             InlineKeyboardButton("Retour", callback_data="help")]])) 
      
    elif data == "digital_meta_data":
        await client.send_chat_action(query.message.chat.id, ChatAction.TYPING)
        await query.message.edit_text(
            text=rkn.DIGITAL_METADATA,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
             InlineKeyboardButton("Retour", callback_data="help")]])) 
      
    elif data == "bot_status":
        await client.send_chat_action(query.message.chat.id, ChatAction.TYPING)
        total_users = await zeexdev.total_users_count()
        total_premium_users = await zeexdev.total_premium_users_count()
        uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - client.uptime))    
        sent = humanbytes(psutil.net_io_counters().bytes_sent)
        recv = humanbytes(psutil.net_io_counters().bytes_recv)
        await query.message.edit_text(
            text=rkn.BOT_STATUS.format(uptime, total_users, total_premium_users, sent, recv),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
             InlineKeyboardButton("Retour", callback_data="about")]])) 
      
    elif data == "live_status":
        await client.send_chat_action(query.message.chat.id, ChatAction.TYPING)
        currentTime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - client.uptime))    
        total, used, free = shutil.disk_usage(".")
        total = humanbytes(total)
        used = humanbytes(used)
        free = humanbytes(free)
        sent = humanbytes(psutil.net_io_counters().bytes_sent)
        recv = humanbytes(psutil.net_io_counters().bytes_recv)
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        await query.message.edit_text(
            text=rkn.LIVE_STATUS.format(currentTime, cpu_usage, ram_usage, total, used, disk_usage, free, sent, recv),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
             InlineKeyboardButton("Retour", callback_data="about")]])) 
      
    elif data == "source_code":
        await client.send_chat_action(query.message.chat.id, ChatAction.TYPING)
        await query.message.edit_text(
            text=rkn.DEV_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("💞 Rejoindre 💞", url="https://t.me/CineFlixi")
            ],[
                InlineKeyboardButton("🔒 Fermer", callback_data="close"),
                InlineKeyboardButton("◀️ Retour", callback_data="start")
                 ]])          
        )
    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
            await query.message.continue_propagation()
        except:
            await query.message.delete()
            await query.message.continue_propagation()

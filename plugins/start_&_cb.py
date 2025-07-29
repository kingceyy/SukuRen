import random
import asyncio
import datetime
import pytz
import time
import psutil
import shutil

from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery

from helper.database import zeexdev
from config import Config, rkn
from helper.utils import humanbytes
from plugins import __version__ as _bot_version_, __developer__, __database__, __library__, __language__, __programer__

upgrade_button = InlineKeyboardMarkup([[        
        InlineKeyboardButton('acheter premium ✓', user_id=int(6705898491)),
         ],[
        InlineKeyboardButton("Retour", callback_data = "start")
]])

upgrade_trial_button = InlineKeyboardMarkup([[        
        InlineKeyboardButton('acheter premium ✓', user_id=int(6705898491)),
         ],[
        InlineKeyboardButton("essai - 12 heures ✓", callback_data = "give_trial"),
        InlineKeyboardButton("Retour", callback_data = "start")
]])

start_button = InlineKeyboardMarkup([[        
        InlineKeyboardButton('Mises à jour', url='https://t.me/ZeeXDev'),
        InlineKeyboardButton('Support', url='https://t.me/BTZF_CHAT')
        ],[
        InlineKeyboardButton('À propos', callback_data='about'),
        InlineKeyboardButton('Aide', callback_data='help')
        ],[
        InlineKeyboardButton('💸 passer à premium 💸', callback_data='upgrade')
         ]])
        
@Client.on_message(filters.private & filters.command("start"))
async def start(client, message):
    user = message.from_user
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    await digital_botz.add_user(client, message) 
    if Config.RKN_PIC:
        await message.reply_photo(Config.RKN_PIC, caption=rkn.START_TXT.format(user.mention), reply_markup=start_button)       
    else:
        await message.reply_text(text=rkn.START_TXT.format(user.mention), reply_markup=start_button, disable_web_page_preview=True)

@Client.on_message(filters.private & filters.command("myplan"))
async def myplan(client, message):
    user_id = message.from_user.id
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    user = message.from_user.mention        
    await digital_botz.reset_uploadlimit_access(user_id)        
    if await digital_botz.has_premium_access(user_id):
        user_data = await digital_botz.get_user_data(user_id)
        limit = user_data.get('uploadlimit', 0)
        used = user_data.get('used_limit', 0)
        remain = int(limit)- int(used)
        type = user_data.get('usertype', "Gratuit")
            
        data = await digital_botz.get_user(user_id)
        expiry_str_in_ist = data.get("expiry_time")
        time_left_str = expiry_str_in_ist - datetime.datetime.now()
        
        await message.reply_text(f"👤 utilisateur :- {user}\n⚡ ID utilisateur :- <code>{user_id}</code>\nPlan :- `{type}`\nLimite de téléchargement quotidienne :- `{humanbytes(limit)}`\nUtilisé aujourd'hui :- `{humanbytes(used)}\n`Restant :- `{humanbytes(remain)}`\n⏰ Temps restant : {time_left_str}\n⌛️ Date d'expiration : {expiry_str_in_ist}", quote=True)
    else:
        user_data = await digital_botz.get_user_data(user_id)
        limit = user_data.get('uploadlimit', 0)
        used = user_data.get('used_limit', 0)
        remain = int(limit)- int(used)
        type = user_data.get('usertype', "Gratuit")
        await message.reply_text(f"👤 utilisateur :- {user}\n⚡ ID utilisateur :- <code>{user_id}</code>\nPlan :- `{type}`\nLimite de téléchargement quotidienne :- `{humanbytes(limit)}`\nUtilisé aujourd'hui :- `{humanbytes(used)}\n`Restant :- `{humanbytes(remain)}`\n⏰ Date d'expiration :- illimité\n\nSi vous souhaitez prendre un abonnement premium, cliquez sur le bouton ci-dessous 👇",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("💸 voir les plans premium 💸", callback_data='upgrade')]]), quote=True)			 
 

@Client.on_message(filters.private & filters.command("plans"))
async def plans(client, message):
    user = message.from_user
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    free_trial_status = await digital_botz.get_free_trial_status(user.id)
    if not await digital_botz.has_premium_access(user.id):
        if not free_trial_status:
            await message.reply_text(text=rkn.UPGRADE.format(user.mention), reply_markup=upgrade_trial_button, disable_web_page_preview=True)
        else:
            await message.reply_text(text=rkn.UPGRADE.format(user.mention), reply_markup=upgrade_button, disable_web_page_preview=True)
    else:
        await message.reply_text(text=rkn.UPGRADE.format(user.mention), reply_markup=upgrade_button, disable_web_page_preview=True)
   
  
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
                InlineKeyboardButton("ZeeXClub", callback_data="source_code"),
                InlineKeyboardButton("état du bot", callback_data="bot_status")
                ],[
                InlineKeyboardButton("statut en direct", callback_data="live_status"),
                InlineKeyboardButton("amélioration", callback_data="upgrade")
                ],[   
                InlineKeyboardButton("Retour", callback_data="start")
           ]]))    
        
    elif data == "upgrade":
        await client.send_chat_action(query.message.chat.id, ChatAction.TYPING)
        free_trial_status = await digital_botz.get_free_trial_status(query.from_user.id)
        if not await digital_botz.has_premium_access(query.from_user.id):
            if not free_trial_status:
                await query.message.edit_text(text=rkn.UPGRADE, disable_web_page_preview=True, reply_markup=upgrade_trial_button)   
            else:
                await query.message.edit_text(text=rkn.UPGRADE, disable_web_page_preview=True, reply_markup=upgrade_button)
        else:
            await query.message.edit_text(text=rkn.UPGRADE, disable_web_page_preview=True, reply_markup=upgrade_button)
           
    elif data == "give_trial":
        await client.send_chat_action(query.message.chat.id, ChatAction.TYPING)
        await query.message.delete()
        free_trial_status = await digital_botz.get_free_trial_status(query.from_user.id)
        if not free_trial_status:            
            await digital_botz.give_free_trail(query.from_user.id)
            new_text = "**Votre essai premium a été ajouté pour 12 heures.\n\nVous pouvez utiliser l'essai gratuit pendant 12 heures à partir de maintenant 😀\n\nआप अब से 𝟷𝟸 घण्टा के लिए निःशुल्क ट्रायल का उपयोग कर सकते हैं 😀**"
        else:
            new_text = "**🤣 Vous avez déjà utilisé l'essai gratuit. Veuillez acheter un abonnement ici 👉 /plans**"
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
        total_users = await digital_botz.total_users_count()
        total_premium_users = await digital_botz.total_premium_users_count()
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
                InlineKeyboardButton("💞 Rejoindre 💞", url="https://t.me/ZeeXClub")
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

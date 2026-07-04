from config import Config
from helper.database import zeexdev
from helper.utils import get_seconds, humanbytes
import os, sys, time, asyncio, logging, datetime, pytz, traceback, html

from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@Client.on_message(filters.command(["stats", "status"]) & filters.user(Config.ADMIN))
async def get_stats(bot, message):
    total_users = await zeexdev.total_users_count()
    total_premium_users = await zeexdev.total_premium_users_count()
    uptime = time.strftime("%Hh%Mm%Ss", time.gmtime(time.time() - bot.uptime))    
    start_t = time.time()
    rkn = await message.reply('<b>Traitement en cours...</b>')    
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    await rkn.edit(text=f"<b>--Statut du Bot--</b> \n\n<b>⌚ Temps de fonctionnement:</b> {uptime} \n<b>🐌 Latence actuelle:</b> <code>{time_taken_s:.3f} ms</code> \n<b>👭 Utilisateurs totaux:</b> <code>{total_users}</code>\n<b>💸 Utilisateurs premium:</b> <code>{total_premium_users}</code>")

@Client.on_message(filters.command('logs') & filters.user(Config.ADMIN))
async def log_file(b, m):
    try:
        await m.reply_document('BotLog.txt')
    except Exception as e:
        await m.reply(str(e))

@Client.on_message(filters.command(["addpremium", "add_premium"]) & filters.user(Config.ADMIN))
async def add_premium(client, message):
    if len(message.command) == 5:
        time_zone = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))
        current_time = time_zone.strftime("%d-%m-%Y\n⏱ Heure d'ajout : %I:%M:%S %p") 
        user_id = int(message.command[1])
        user = await client.get_users(user_id)
        time = message.command[3]+" "+message.command[4]
        plan_type = message.command[2]
        
        if plan_type == "Pro":
            limit = 107374182400
            type = "Pro"
        elif plan_type == "UltraPro":
            limit = 1073741824000
            type = "UltraPro"
            
        seconds = await get_seconds(time)
        if seconds > 0:
            expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
            user_data = {"id": user_id, "expiry_time": expiry_time}
            await zeexdev.addpremium(user_id, user_data, limit, type)
            
            expiry_str_in_ist = expiry_time.astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y\n⏱ Heure d'expiration : %I:%M:%S %p")
            
            await message.reply_text(
                f"Abonnement premium ajouté avec succès ✅\n\n👤 Utilisateur : {user.mention}\n⚡ ID : <code>{user_id}</code>\nPlan : <code>{type}</code>\nLimite quotidienne : <code>{humanbytes(limit)}</code>\n⏰ Accès premium : <code>{time}</code>\n\n⏳ Date d'ajout : {current_time}\n\n⌛ Date d'expiration : {expiry_str_in_ist}", 
                quote=True, 
                disable_web_page_preview=True
            )
            
            await client.send_message(
                chat_id=user_id,
                text=f"👋 Bonjour {user.mention},\nMerci pour votre abonnement premium.\nProfitez-en ! ✨🎉\n\n⏰ Accès premium : <code>{time}</code>\nPlan : <code>{type}</code>\nLimite quotidienne : <code>{humanbytes(limit)}</code>\n⏳ Date d'ajout : {current_time}\n\n⌛ Date d'expiration : {expiry_str_in_ist}", 
                disable_web_page_preview=True              
            )
            return
            
        await message.reply_text("Format de durée invalide. Utilisez '1 jour', '1 heure', '1 min', '1 mois' ou '1 année'", quote=True)
        return
        
    await message.reply_text(
        "Utilisation : /addpremium user_id Type_Plan (ex: <code>Pro</code>, <code>UltraPro</code>) durée (ex: '1 jour', '1 heure', '1 min', '1 mois' ou '1 année')", 
        quote=True
    )

@Client.on_message(filters.command(["removepremium", "remove_premium"]) & filters.user(Config.ADMIN))
async def remove_premium(bot, message):
    if len(message.command) == 2:
        user_id = int(message.command[1])
        user = await bot.get_users(user_id)
        if await zeexdev.has_premium_access(user_id):
            await zeexdev.remove_premium(user_id)
            await message.reply_text(f"L'abonnement premium de {user.mention} a été supprimé avec succès.", quote=True)
            await bot.send_message(
                chat_id=user_id, 
                text=f"<b>Bonjour {user.mention},\n\n✨ Votre compte a été retiré de notre plan premium\n\nVérifiez votre plan avec /myplan</b>"
            )
        else:
            await message.reply_text("Impossible de retirer l'abonnement premium !\nÊtes-vous sûr qu'il s'agit d'un ID utilisateur premium ?", quote=True)
    else:
        await message.reply_text("Utilisation : /remove_premium user_id", quote=True)

@Client.on_message(filters.private & filters.command("restart") & filters.user(Config.ADMIN))
async def restart_bot(b, m):
    rkn = await b.send_message(text="<b>🔄 Processus arrêtés. Redémarrage du bot en cours...</b>", chat_id=m.chat.id)
    stats = {"failed": 0, "success": 0, "deactivated": 0, "blocked": 0}
    start_time = time.time()
    total_users = await zeexdev.total_users_count()
    
    async for user in await zeexdev.get_all_users():
        try:
            await b.send_message(
                user['_id'],
                f"Bonjour {(await b.get_users(user['_id'])).mention}\n\n<b>🔄 Processus arrêtés. Redémarrage du bot en cours...\n\n✅ Le bot a redémarré. Vous pouvez maintenant l'utiliser.</b>"
            )
            stats["success"] += 1
        except InputUserDeactivated:
            stats["deactivated"] += 1
            await zeexdev.delete_user(user['_id'])
        except UserIsBlocked:
            stats["blocked"] += 1
            await zeexdev.delete_user(user['_id'])
        except Exception:
            stats["failed"] += 1
            await zeexdev.delete_user(user['_id'])
            
        if not sum(stats.values()) % 20:
            await rkn.edit(
                f"<u>Redémarrage en cours:</u>\n\n• Utilisateurs totaux: {total_users}\n• Réussis: {stats['success']}\n• Bloqués: {stats['blocked']}\n• Comptes désactivés: {stats['deactivated']}\n• Échecs: {stats['failed']}"
            )
    
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await rkn.edit(
        f"Redémarrage terminé en: {completed_in}\n\n• Utilisateurs totaux: {total_users}\n• Réussis: {stats['success']}\n• Bloqués: {stats['blocked']}\n• Comptes désactivés: {stats['deactivated']}\n• Échecs: {stats['failed']}"
    )
    os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_message(filters.private & filters.command("ban") & filters.user(Config.ADMIN))
async def ban(c: Client, m: Message):
    if len(m.command) == 1:
        await m.reply_text(
            f"Utilisez cette commande pour bannir un utilisateur.\n\n"
            f"Utilisation:\n\n"
            f"<code>/ban user_id durée raison</code>\n\n"
            f"Ex: <code>/ban 1234567 28 Utilisation abusive.</code>\n"
            f"Cela bannira l'utilisateur 1234567 pendant 28 jours pour 'Utilisation abusive'.",
            quote=True
        )
        return

    try:
        user_id = int(m.command[1])
        ban_duration = int(m.command[2])
        ban_reason = ' '.join(m.command[3:])
        
        try:
            await c.send_message(
                user_id,              
                f"Vous êtes banni de ce bot pour <b>{ban_duration}</b> jour(s) pour la raison <i>{ban_reason}</i> \n\n"
                f"<b>Message de l'administrateur</b>"
            )
        except:
            traceback.print_exc()

        await zeexdev.ban_user(user_id, ban_duration, ban_reason)
        await m.reply_text(f"Utilisateur {user_id} banni pour {ban_duration} jours. Raison: {ban_reason}", quote=True)
    except:
        await m.reply_text(
            f"Erreur !\n\n<code>{html.escape(traceback.format_exc())}</code>",
            quote=True
        )

@Client.on_message(filters.private & filters.command("unban") & filters.user(Config.ADMIN))
async def unban(c: Client, m: Message):
    if len(m.command) == 1:
        await m.reply_text(
            f"Utilisez cette commande pour débannir un utilisateur.\n\n"
            f"Utilisation:\n\n<code>/unban user_id</code>\n\n"
            f"Ex: <code>/unban 1234567</code>",
            quote=True
        )
        return

    try:
        user_id = int(m.command[1])
        await zeexdev.remove_ban(user_id)
        try:
            await c.send_message(user_id, "Votre bannissement a été levé !")
        except:
            pass
        await m.reply_text(f"Utilisateur {user_id} débanni", quote=True)
    except:
        await m.reply_text(
            f"Erreur !\n\n<code>{html.escape(traceback.format_exc())}</code>",
            quote=True
        )

@Client.on_message(filters.private & filters.command("banned_users") & filters.user(Config.ADMIN))
async def _banned_users(_, m: Message):
    banned_users = []
    async for user in await zeexdev.get_all_banned_users():
        banned_users.append(
            f"> <b>ID</b>: <code>{user['id']}</code>, <b>Durée</b>: <code>{user['ban_status']['ban_duration']}</code>, "
            f"<b>Date</b>: <code>{user['ban_status']['banned_on']}</code>, <b>Raison</b>: <code>{user['ban_status']['ban_reason']}</code>"
        )
    
    reply_text = f"Utilisateurs bannis: <code>{len(banned_users)}</code>\n\n" + "\n\n".join(banned_users)
    
    if len(reply_text) > 4096:
        with open('banned-users.txt', 'w') as f:
            f.write(reply_text)
        await m.reply_document('banned-users.txt', True)
        os.remove('banned-users.txt')
    else:
        await m.reply_text(reply_text, True)

@Client.on_message(filters.command("broadcast") & filters.user(Config.ADMIN) & filters.reply)
async def broadcast_handler(bot: Client, m: Message):
    await bot.send_message(Config.LOG_CHANNEL, f"{m.from_user.mention} a démarré une diffusion...")
    broadcast_msg = m.reply_to_message
    stats_msg = await m.reply_text("Diffusion en cours..!")
    
    stats = {"done": 0, "failed": 0, "success": 0}
    start_time = time.time()
    total_users = await zeexdev.total_users_count()
    
    async for user in await zeexdev.get_all_users():
        status = await send_msg(user['_id'], broadcast_msg)
        
        if status == 200:
            stats["success"] += 1
        else:
            stats["failed"] += 1
            if status == 400:
                await zeexdev.delete_user(user['_id'])
                
        stats["done"] += 1
        
        if not stats["done"] % 20:
            await stats_msg.edit(
                f"Progression de la diffusion: \nUtilisateurs totaux {total_users} \nTerminé: {stats['done']} / {total_users}\nSuccès: {stats['success']}\nÉchecs: {stats['failed']}"
            )
    
    completed_in = datetime.timedelta(seconds=int(time.time() - start_time))
    await stats_msg.edit(
        f"Diffusion terminée en: <code>{completed_in}</code>.\n\nUtilisateurs totaux {total_users}\nTerminé: {stats['done']} / {total_users}\nSuccès: {stats['success']}\nÉchecs: {stats['failed']}"
    )

async def send_msg(user_id, message):
    try:
        await message.copy(chat_id=int(user_id))
        return 200
    except FloodWait as e:
        await asyncio.sleep(e.value)
        return await send_msg(user_id, message)
    except (InputUserDeactivated, UserIsBlocked, PeerIdInvalid):
        return 400
    except Exception:
        return 500
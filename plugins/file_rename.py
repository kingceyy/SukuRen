from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType, ChatAction, ParseMode
from pyrogram.errors import FloodWait
from pyrogram.file_id import FileId
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, WebAppInfo

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image

from helper.utils import progress_for_pyrogram, convert, humanbytes, add_prefix_suffix, remove_path
from helper.database import zeexdev
from config import Config, rkn

from asyncio import sleep
import os, time, asyncio, re

UPLOAD_TEXT = """Téléversement en cours..."""
DOWNLOAD_TEXT = """Téléchargement en cours..."""

app = Client("4gb_FileRenameBot", api_id=Config.API_ID, api_hash=Config.API_HASH, session_string=Config.STRING_SESSION, parse_mode=ParseMode.HTML)


def _quota_low_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⚡ Obtenir 15 quotas (pub)", web_app=WebAppInfo(url=Config.WEBAPP_URL))],
        [InlineKeyboardButton("👑 Plans premium", callback_data="plans")]
    ])


@Client.on_message(filters.private & (filters.document | filters.audio | filters.video))
async def rename_start(client, message):
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    user_id = message.from_user.id
    rkn_file = getattr(message, message.media.value)
    filename = rkn_file.file_name
    filesize = humanbytes(rkn_file.file_size)
    mime_type = rkn_file.mime_type
    dcid = FileId.decode(rkn_file.file_id).dc_id
    extension_type = mime_type.split('/')[0]

    # 1 quota = 1 fichier renommé, quelle que soit sa taille
    balance = await zeexdev.get_quota_balance(user_id)
    if balance["total"] < 1:
        return await message.reply_text(
            rkn.QUOTA_LOW_TXT.format(remain=balance["total"], per_ad=Config.QUOTA_PER_AD, expiry=Config.QUOTA_EXPIRY_HOURS),
            reply_markup=_quota_low_markup()
        )

    # La taille de fichier reste une limite technique (API Bot Telegram), pas économique
    if await zeexdev.has_premium_access(user_id):
        if not Config.STRING_SESSION and rkn_file.file_size > 2000 * 1024 * 1024:
            return await message.reply_text("Désolé, ce bot ne supporte pas les fichiers de plus de 2Go")
    else:
        if rkn_file.file_size > 2000 * 1024 * 1024:
            return await message.reply_text("Pour renommer des fichiers de plus de 2Go, tu dois passer premium. /plans")

    try:
        await message.reply_text(
            text=f"<b><i>Information sur le fichier</i></b>\n\n◈ Nom original : <code>{filename}</code>\n\n◈ Extension : <code>{extension_type.upper()}</code>\n◈ Taille : <code>{filesize}</code>\n◈ Type MIME : <code>{mime_type}</code>\n◈ DC ID : <code>{dcid}</code>\n\nVeuillez entrer le nouveau nom de fichier avec son extension...",
            reply_to_message_id=message.id,  
            reply_markup=ForceReply(True)
        )
        await sleep(30)
    except FloodWait as e:
        await sleep(e.value)
        await message.reply_text(
            text=f"<b><i>Information sur le fichier</i></b>\n\n◈ Nom original : <code>{filename}</code>\n\n◈ Extension : <code>{extension_type.upper()}</code>\n◈ Taille : <code>{filesize}</code>\n◈ Type MIME : <code>{mime_type}</code>\n◈ DC ID : <code>{dcid}</code>\n\nVeuillez entrer le nouveau nom de fichier avec son extension...",
            reply_to_message_id=message.id,  
            reply_markup=ForceReply(True)
        )
    except:
        pass

@Client.on_message(filters.private & filters.reply)
async def refunc(client, message):
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    reply_message = message.reply_to_message
    if (reply_message.reply_markup) and isinstance(reply_message.reply_markup, ForceReply):
        new_name = message.text 
        await message.delete()
        msg = await client.get_messages(message.chat.id, reply_message.id)
        file = msg.reply_to_message
        media = getattr(file, file.media.value)
        
        if not "." in new_name:
            extn = media.file_name.rsplit('.', 1)[-1] if "." in media.file_name else "mkv"
            new_name = f"{new_name}.{extn}"
        
        await reply_message.delete()

        button = [[InlineKeyboardButton("📁 Document", callback_data="upload_document")]]
        if file.media in [MessageMediaType.VIDEO, MessageMediaType.DOCUMENT]:
            button.append([InlineKeyboardButton("🎥 Vidéo", callback_data="upload_video")])
        elif file.media == MessageMediaType.AUDIO:
            button.append([InlineKeyboardButton("🎵 Audio", callback_data="upload_audio")])
            
        await message.reply(
            text=f"<b>Sélectionnez le type de fichier de sortie</b>\n<b>• Nom du fichier :</b> <code>{new_name}</code>",
            reply_to_message_id=file.id,
            reply_markup=InlineKeyboardMarkup(button)
        )

@Client.on_callback_query(filters.regex("upload"))
async def doc(bot, update):
    action = {
        "document": ChatAction.UPLOAD_DOCUMENT,
        "video": ChatAction.UPLOAD_VIDEO,
        "audio": ChatAction.UPLOAD_AUDIO
    }[update.data.split("_")[1]]
    
    await bot.send_chat_action(update.message.chat.id, action)
    rkn_processing = await update.message.edit("<code>Traitement en cours...</code>")
    
    if not os.path.isdir("Metadata"):
        os.mkdir("Metadata")

    user_id = update.message.chat.id
    new_name = update.message.text

    # Le nom est toujours encadré par <code>...</code> dans le message envoyé par refunc() :
    # "<b>• Nom du fichier :</b> <code>nom.ext</code>". On extrait ce contenu par regex
    # plutôt que de dépendre d'un séparateur texte fragile.
    backtick_match = re.search(r"<code>(.+?)</code>", new_name)
    if not backtick_match:
        return await rkn_processing.edit("⚠️ Impossible de retrouver le nom de fichier. Recommence l'opération.")
    new_filename_ = backtick_match.group(1)

    # Vérification de sécurité : le quota peut avoir été consommé entre-temps (autre fichier en parallèle)
    balance = await zeexdev.get_quota_balance(user_id)
    if balance["total"] < 1:
        return await rkn_processing.edit(
            rkn.QUOTA_LOW_TXT.format(remain=balance["total"], per_ad=Config.QUOTA_PER_AD, expiry=Config.QUOTA_EXPIRY_HOURS),
            reply_markup=_quota_low_markup()
        )

    try:
        prefix = await zeexdev.get_prefix(user_id)
        suffix = await zeexdev.get_suffix(user_id)
        new_filename = add_prefix_suffix(new_filename_, prefix, suffix)
    except Exception as e:
        return await rkn_processing.edit(f"⚠️ Erreur lors de l'ajout du préfixe/suffixe\n\nContactez le support : @Kingcey\nErreur : {e}")

    file = update.message.reply_to_message
    media = getattr(file, file.media.value)
    
    file_path = f"Renames/{new_filename}"
    metadata_path = f"Metadata/{new_filename}"

    await rkn_processing.edit("<code>Téléchargement...</code>")
    await bot.send_chat_action(update.message.chat.id, ChatAction.UPLOAD_DOCUMENT)
    
    try:
        dl_path = await bot.download_media(
            message=file, 
            file_name=file_path, 
            progress=progress_for_pyrogram, 
            progress_args=(DOWNLOAD_TEXT, rkn_processing, time.time())
        )
    except Exception as e:
        return await rkn_processing.edit(str(e))

    metadata_mode = await zeexdev.get_metadata_mode(user_id)
    if metadata_mode:
        metadata = await zeexdev.get_metadata_code(user_id)
        if metadata:
            await bot.send_chat_action(update.message.chat.id, ChatAction.TYPING)
            await rkn_processing.edit("Métadonnées détectées\n\n<i><b>Veuillez patienter...</b></i>\n<b>Ajout des métadonnées au fichier...</b>")
            cmd = f"""ffmpeg -i {dl_path} {metadata} {metadata_path}"""
            
            process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await process.communicate()
            er = stderr.decode()
            if er:
                return await rkn_processing.edit(f"Erreur : {er}")
            
            await rkn_processing.edit("<b>Métadonnées ajoutées avec succès ✅</b>\n\n<b>Tentative de téléversement...</b>")
    else:
        await rkn_processing.edit("<code>Tentative de téléversement...</code>")
        
    duration = 0
    try:
        parser = createParser(file_path)
        metadata = extractMetadata(parser)
        if metadata.has("duration"):
            duration = metadata.get('duration').seconds
        parser.close()
    except:
        pass
        
    ph_path = None
    c_caption = await zeexdev.get_caption(user_id)
    c_thumb = await zeexdev.get_thumbnail(user_id)

    if c_caption:
        try:
            caption = c_caption.format(
                filename=new_filename, 
                filesize=humanbytes(media.file_size), 
                duration=convert(duration))
        except Exception as e:
            return await rkn_processing.edit(f"Erreur dans votre légende : {e}")
    else:
        caption = f"<b>{new_filename}</b>"
 
    if media.thumbs or c_thumb:
        ph_path = await bot.download_media(c_thumb) if c_thumb else await bot.download_media(media.thumbs[0].file_id)
        Image.open(ph_path).convert("RGB").save(ph_path)
        img = Image.open(ph_path)
        img.resize((320, 320))
        img.save(ph_path, "JPEG")

    file_type = update.data.split("_")[1]
    await bot.send_chat_action(update.message.chat.id, action)
    
    if media.file_size > 2000 * 1024 * 1024:
        try:
            if file_type == "document":
                filw = await app.send_document(
                    Config.LOG_CHANNEL,
                    document=metadata_path if metadata_mode else file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))
            elif file_type == "video":
                filw = await app.send_video(
                    Config.LOG_CHANNEL,
                    video=metadata_path if metadata_mode else file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))
            elif file_type == "audio":
                filw = await app.send_audio(
                    Config.LOG_CHANNEL,
                    audio=metadata_path if metadata_mode else file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))

            await bot.copy_message(update.from_user.id, filw.chat.id, filw.id)
            await bot.delete_messages(filw.chat.id, filw.id)
        except Exception as e:
            await remove_path(ph_path, file_path, dl_path, metadata_path)
            return await rkn_processing.edit(f"Erreur : {e}")
    else:
        try:
            if file_type == "document":
                await bot.send_document(
                    update.message.chat.id,
                    document=metadata_path if metadata_mode else file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))
            elif file_type == "video":
                await bot.send_video(
                    update.message.chat.id,
                    video=metadata_path if metadata_mode else file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))
            elif file_type == "audio":
                await bot.send_audio(
                    update.message.chat.id,
                    audio=metadata_path if metadata_mode else file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=(UPLOAD_TEXT, rkn_processing, time.time()))
        except Exception as e:
            await remove_path(ph_path, file_path, dl_path, metadata_path)
            return await rkn_processing.edit(f"Erreur : {e}")

    # Le fichier est bien parti : on consomme le quota maintenant (jamais avant, jamais sur échec)
    await zeexdev.consume_quota(user_id, 1)
    new_balance = await zeexdev.get_quota_balance(user_id)

    await remove_path(ph_path, file_path, dl_path, metadata_path)
    await rkn_processing.edit(f"Téléversement terminé avec succès ✅\n\n⚡ Quotas restants : <code>{new_balance['total']}</code>")

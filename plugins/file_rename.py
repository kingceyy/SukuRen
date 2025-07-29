from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType, ChatAction
from pyrogram.errors import FloodWait
from pyrogram.file_id import FileId
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from PIL import Image

from helper.utils import progress_for_pyrogram, convert, humanbytes, add_prefix_suffix, remove_path
from helper.database import zeexdev
from config import Config

from asyncio import sleep
import os, time, asyncio

UPLOAD_TEXT = """Téléversement en cours..."""
DOWNLOAD_TEXT = """Téléchargement en cours..."""

app = Client("4gb_FileRenameBot", api_id=Config.API_ID, api_hash=Config.API_HASH, session_string=Config.STRING_SESSION)

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

    await zeexdev.reset_uploadlimit_access(user_id)
    user_data = await zeexdev.get_user_data(user_id)
    limit = user_data.get('uploadlimit', 0)
    used = user_data.get('used_limit', 0)
    remain = int(limit) - int(used)
    
    if remain < int(rkn_file.file_size):
        return await message.reply_text(
            f"100% de la limite quotidienne {humanbytes(limit)} atteinte.\n\nTaille du fichier : {humanbytes(rkn_file.file_size)}\nVotre utilisation : {humanbytes(used)}\n\nIl vous reste seulement **{humanbytes(remain)}**.\nVeuillez passer à un abonnement premium.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🪪 Passer à Premium", callback_data="plans")]])
        )
         
    if await zeexdev.has_premium_access(user_id):
        if not Config.STRING_SESSION and rkn_file.file_size > 2000 * 1024 * 1024:
            return await message.reply_text("Désolé, ce bot ne supporte pas les fichiers de plus de 2Go")
    else:
        if rkn_file.file_size > 2000 * 1024 * 1024:
            return await message.reply_text("Pour renommer des fichiers de plus de 4Go, vous devez passer à un abonnement premium. /plans")

    try:
        await message.reply_text(
            text=f"**__Information sur le fichier__\n\n◈ Nom original : `{filename}`\n\n◈ Extension : `{extension_type.upper()}`\n◈ Taille : `{filesize}`\n◈ Type MIME : `{mime_type}`\n◈ DC ID : `{dcid}`\n\nVeuillez entrer le nouveau nom de fichier avec son extension...__**",
            reply_to_message_id=message.id,  
            reply_markup=ForceReply(True)
        )
        await sleep(30)
    except FloodWait as e:
        await sleep(e.value)
        await message.reply_text(
            text=f"**__Information sur le fichier__\n\n◈ Nom original : `{filename}`\n\n◈ Extension : `{extension_type.upper()}`\n◈ Taille : `{filesize}`\n◈ Type MIME : `{mime_type}`\n◈ DC ID : `{dcid}`\n\nVeuillez entrer le nouveau nom de fichier avec son extension...__**",
            reply_to_message_id=message.id,  
            reply_markup=ForceReply(True)
        )
    except:
        pass

@Client.on_message(filters.private & filters.reply))
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
            text=f"**Sélectionnez le type de fichier de sortie**\n**• Nom du fichier :** `{new_name}`",
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
    rkn_processing = await update.message.edit("`Traitement en cours...`")
    
    if not os.path.isdir("Metadata"):
        os.mkdir("Metadata")

    user_id = update.message.chat.id
    new_name = update.message.text
    new_filename_ = new_name.split(":-")[1]
    user_data = await zeexdev.get_user_data(user_id)

    try:
        prefix = await zeexdev.get_prefix(user_id)
        suffix = await zeexdev.get_suffix(user_id)
        new_filename = add_prefix_suffix(new_filename_, prefix, suffix)
    except Exception as e:
        return await rkn_processing.edit(f"⚠️ Erreur lors de l'ajout du préfixe/suffixe\n\nContactez le support : @RknDeveloperr\nErreur : {e}")

    file = update.message.reply_to_message
    media = getattr(file, file.media.value)
    
    file_path = f"Renames/{new_filename}"
    metadata_path = f"Metadata/{new_filename}"

    limit = user_data.get('uploadlimit', 0)
    used = user_data.get('used_limit', 0)

    await rkn_processing.edit("`Téléchargement...`")
    await bot.send_chat_action(update.message.chat.id, ChatAction.UPLOAD_DOCUMENT)
    total_used = int(used) + int(media.file_size)
    await zeexdev.set_used_limit(user_id, total_used)
    
    try:
        dl_path = await bot.download_media(
            message=file, 
            file_name=file_path, 
            progress=progress_for_pyrogram, 
            progress_args=(DOWNLOAD_TEXT, rkn_processing, time.time())
        )
    except Exception as e:
        await zeexdev.set_used_limit(user_id, used)
        return await rkn_processing.edit(str(e))

    metadata_mode = await zeexdev.get_metadata_mode(user_id)
    if metadata_mode:
        metadata = await zeexdev.get_metadata_code(user_id)
        if metadata:
            await bot.send_chat_action(update.message.chat.id, ChatAction.TYPING)
            await rkn_processing.edit("Métadonnées détectées\n\n__**Veuillez patienter...**__\n**Ajout des métadonnées au fichier...**")
            cmd = f"""ffmpeg -i {dl_path} {metadata} {metadata_path}"""
            
            process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            stdout, stderr = await process.communicate()
            er = stderr.decode()
            if er:
                return await rkn_processing.edit(f"Erreur : {er}")
            
            await rkn_processing.edit("**Métadonnées ajoutées avec succès ✅**\n\n**Tentative de téléversement...**")
    else:
        await rkn_processing.edit("`Tentative de téléversement...`")
        
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
            await zeexdev.set_used_limit(user_id, used)
            return await rkn_processing.edit(f"Erreur dans votre légende : {e}")
    else:
        caption = f"**{new_filename}**"
 
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
            await zeexdev.set_used_limit(user_id, used)
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
            await zeexdev.set_used_limit(user_id, used)
            await remove_path(ph_path, file_path, dl_path, metadata_path)
            return await rkn_processing.edit(f"Erreur : {e}")

    await remove_path(ph_path, file_path, dl_path, metadata_path)
    await rkn_processing.edit("Téléversement terminé avec succès ✅")

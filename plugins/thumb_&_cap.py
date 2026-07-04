from pyrogram import Client, filters 
from pyrogram.enums import ChatAction
from helper.database import zeexdev

@Client.on_message(filters.private & filters.command('set_caption'))
async def add_caption(client, message):
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    rkn = await message.reply_text("<i><b>Veuillez patienter</b></i>")
    if len(message.command) == 1:
       return await rkn.edit("""<i><b>Indiquez la légende</b></i>

Exemple : <code>/set_caption {filename}
💾 Taille : {filesize}
⏰ Durée : {duration}</code>""")
    caption = message.text.split(" ", 1)[1]
    await zeexdev.set_caption(message.from_user.id, caption=caption)
    await rkn.edit("<i><b>✅ Légende enregistrée</b></i>")
   
@Client.on_message(filters.private & filters.command(['del_caption', 'delete_caption', 'delcaption']))
async def delete_caption(client, message):
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    rkn = await message.reply_text("<i><b>Veuillez patienter</b></i>")
    caption = await zeexdev.get_caption(message.from_user.id)  
    if not caption:
       return await rkn.edit("<i><b>😔 Vous n'avez aucune légende</b></i>")
    await zeexdev.set_caption(message.from_user.id, caption=None)
    await rkn.edit("<i><b>❌️ Légende supprimée</b></i>")
                                       
@Client.on_message(filters.private & filters.command(['see_caption', 'view_caption']))
async def see_caption(client, message):
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    rkn = await message.reply_text("<i><b>Veuillez patienter</b></i>")
    caption = await zeexdev.get_caption(message.from_user.id)  
    if caption:
       await rkn.edit(f"<b>Votre légende :</b>\n\n<code>{caption}</code>")
    else:
       await rkn.edit("<i><b>😔 Vous n'avez aucune légende</b></i>")

@Client.on_message(filters.private & filters.command(['view_thumb', 'viewthumb']))
async def viewthumb(client, message):
    await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
    rkn = await message.reply_text("<i><b>Veuillez patienter</b></i>")
    thumb = await zeexdev.get_thumbnail(message.from_user.id)
    if thumb:
        await client.send_photo(chat_id=message.chat.id, photo=thumb)
        await rkn.delete()
    else:
        await rkn.edit("😔 <i><b>Vous n'avez aucune miniature</b></i>") 
        
@Client.on_message(filters.private & filters.command(['del_thumb', 'delete_thumb', 'delthumb']))
async def removethumb(client, message):
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    rkn = await message.reply_text("<i><b>Veuillez patienter</b></i>")
    thumb = await zeexdev.get_thumbnail(message.from_user.id)
    if thumb:
        await zeexdev.set_thumbnail(message.from_user.id, file_id=None)
        await rkn.edit("❌️ <i><b>Miniature supprimée</b></i>")
        return
    await rkn.edit("😔 <i><b>Vous n'avez aucune miniature</b></i>")


@Client.on_message(filters.private & filters.photo)
async def addthumbs(client, message):
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    rkn = await message.reply_text("<i><b>Veuillez patienter</b></i>")
    await zeexdev.set_thumbnail(message.from_user.id, file_id=message.photo.file_id)                
    await rkn.edit("✅️ <i><b>Miniature enregistrée</b></i>")

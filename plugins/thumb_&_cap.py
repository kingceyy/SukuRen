from pyrogram import Client, filters 
from pyrogram.enums import ChatAction
from helper.database import zeexdev

@Client.on_message(filters.private & filters.command('set_caption'))
async def add_caption(client, message):
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    rkn = await message.reply_text("__**Veuillez patienter**__")
    if len(message.command) == 1:
       return await rkn.edit("""**__Indiquez la légende__\n
Exemple : `/set_caption {filename}\n
💾 Taille : {filesize}\n
⏰ Durée : {duration}`**""")
    caption = message.text.split(" ", 1)[1]
    await zeexdev.set_caption(message.from_user.id, caption=caption)
    await rkn.edit("__**✅ Légende enregistrée**__")
   
@Client.on_message(filters.private & filters.command(['del_caption', 'delete_caption', 'delcaption']))
async def delete_caption(client, message):
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    rkn = await message.reply_text("__**Veuillez patienter**__")
    caption = await zeexdev.get_caption(message.from_user.id)  
    if not caption:
       return await rkn.edit("__**😔 Vous n'avez aucune légende**__")
    await zeexdev.set_caption(message.from_user.id, caption=None)
    await rkn.edit("__**❌️ Légende supprimée**__")
                                       
@Client.on_message(filters.private & filters.command(['see_caption', 'view_caption']))
async def see_caption(client, message):
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    rkn = await message.reply_text("__**Veuillez patienter**__")
    caption = await zeexdev.get_caption(message.from_user.id)  
    if caption:
       await rkn.edit(f"**Votre légende :**\n\n`{caption}`")
    else:
       await rkn.edit("__**😔 Vous n'avez aucune légende**__")

@Client.on_message(filters.private & filters.command(['view_thumb', 'viewthumb']))
async def viewthumb(client, message):
    await client.send_chat_action(message.chat.id, ChatAction.UPLOAD_PHOTO)
    rkn = await message.reply_text("__**Veuillez patienter**__")
    thumb = await zeexdev.get_thumbnail(message.from_user.id)
    if thumb:
        await client.send_photo(chat_id=message.chat.id, photo=thumb)
        await rkn.delete()
    else:
        await rkn.edit("😔 __**Vous n'avez aucune miniature**__") 
        
@Client.on_message(filters.private & filters.command(['del_thumb', 'delete_thumb', 'delthumb']))
async def removethumb(client, message):
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    rkn = await message.reply_text("__**Veuillez patienter**__")
    thumb = await zeexdev.get_thumbnail(message.from_user.id)
    if thumb:
        await zeexdev.set_thumbnail(message.from_user.id, file_id=None)
        await rkn.edit("❌️ __**Miniature supprimée**__")
        return
    await rkn.edit("😔 __**Vous n'avez aucune miniature**__")


@Client.on_message(filters.private & filters.photo)
async def addthumbs(client, message):
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    rkn = await message.reply_text("__**Veuillez patienter**__")
    await zeexdev.set_thumbnail(message.from_user.id, file_id=message.photo.file_id)                
    await rkn.edit("✅️ __**Miniature enregistrée**__")
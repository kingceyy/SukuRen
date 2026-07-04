from pyrogram import Client, filters, enums
from helper.database import zeexdev

@Client.on_message(filters.private & filters.command('set_prefix'))
async def add_prefix(client, message):
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    if len(message.command) == 1:
        return await message.reply_text("<i><b>Donnez le préfixe</b></i>\n\nExemple:- <code>/set_prefix @Rkn_Bots</code>")
    
    prefix = message.text.split(" ", 1)[1]
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    RknDev = await message.reply_text("Veuillez patienter...", reply_to_message_id=message.id)
    await zeexdev.set_prefix(message.from_user.id, prefix)
    await RknDev.edit("<i><b>✅ Préfixe enregistré</b></i>")

@Client.on_message(filters.private & filters.command('del_prefix'))
async def delete_prefix(client, message):
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    RknDev = await message.reply_text("Veuillez patienter...", reply_to_message_id=message.id)
    prefix = await zeexdev.get_prefix(message.from_user.id)
    
    if not prefix:
        return await RknDev.edit("<i><b>😔 Vous n'avez aucun préfixe</b></i>")
    
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await zeexdev.set_prefix(message.from_user.id, None)
    await RknDev.edit("<i><b>❌️ Préfixe supprimé</b></i>")

@Client.on_message(filters.private & filters.command('see_prefix'))
async def see_prefix(client, message):
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    RknDev = await message.reply_text("Veuillez patienter...", reply_to_message_id=message.id)
    prefix = await zeexdev.get_prefix(message.from_user.id)
    
    if prefix:
        await RknDev.edit(f"<b>Votre préfixe:-</b>\n\n<code>{prefix}</code>")
    else:
        await RknDev.edit("<i><b>😔 Vous n'avez aucun préfixe</b></i>")

@Client.on_message(filters.private & filters.command('set_suffix'))
async def add_suffix(client, message):
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    if len(message.command) == 1:
        return await message.reply_text("<i><b>Donnez le suffixe</b></i>\n\nExemple:- <code>/set_suffix @Rkn_Bots</code>")
    
    suffix = message.text.split(" ", 1)[1]
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    RknDev = await message.reply_text("Veuillez patienter...", reply_to_message_id=message.id)
    await zeexdev.set_suffix(message.from_user.id, suffix)
    await RknDev.edit("<i><b>✅ Suffixe enregistré</b></i>")

@Client.on_message(filters.private & filters.command('del_suffix'))
async def delete_suffix(client, message):
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    RknDev = await message.reply_text("Veuillez patienter...", reply_to_message_id=message.id)
    suffix = await zeexdev.get_suffix(message.from_user.id)
    
    if not suffix:
        return await RknDev.edit("<i><b>😔 Vous n'avez aucun suffixe</b></i>")
    
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    await zeexdev.set_suffix(message.from_user.id, None)
    await RknDev.edit("<i><b>❌️ Suffixe supprimé</b></i>")

@Client.on_message(filters.private & filters.command('see_suffix'))
async def see_suffix(client, message):
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    RknDev = await message.reply_text("Veuillez patienter...", reply_to_message_id=message.id)
    suffix = await zeexdev.get_suffix(message.from_user.id)
    
    if suffix:
        await RknDev.edit(f"<b>Votre suffixe:-</b>\n\n<code>{suffix}</code>")
    else:
        await RknDev.edit("<i><b>😔 Vous n'avez aucun suffixe</b></i>")

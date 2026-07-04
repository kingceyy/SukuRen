from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from pyrogram.enums import ChatAction
from helper.database import zeexdev
from config import rkn

# Constantes pour les boutons (en majuscules selon les conventions PEP8)
METADATA_TRUE = [
    [InlineKeyboardButton('Métadonnées activées', callback_data='metadata_1'),
     InlineKeyboardButton('✅', callback_data='metadata_1')],
    [InlineKeyboardButton('Définir métadonnées personnalisées', callback_data='custom_metadata')]
]

METADATA_FALSE = [
    [InlineKeyboardButton('Métadonnées désactivées', callback_data='metadata_0'),
     InlineKeyboardButton('❌', callback_data='metadata_0')],
    [InlineKeyboardButton('Définir métadonnées personnalisées', callback_data='custom_metadata')]
]

# Marqueur stable utilisé pour reconnaître notre propre prompt ForceReply
# (voir metadata_reply() plus bas et refunc() dans file_rename.py, qui délègue
# ici via continue_propagation() quand ce n'est pas son propre prompt de renommage).
METADATA_PROMPT_MARKER = "Métadonnées personnalisées"

@Client.on_message(filters.private & filters.command('metadata'))
async def handle_metadata(bot: Client, message: Message):
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    RknDev = await message.reply_text("<i><b>Veuillez patienter...</b></i>", reply_to_message_id=message.id)
    
    bool_metadata = await zeexdev.get_metadata_mode(message.from_user.id)
    user_metadata = await zeexdev.get_metadata_code(message.from_user.id)
    
    keyboard = METADATA_TRUE if bool_metadata else METADATA_FALSE
    await RknDev.edit(
        f"Vos métadonnées actuelles :-\n\n➜ <code>{user_metadata}</code>",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@Client.on_callback_query(filters.regex(r'^(metadata_\d|custom_metadata)$'))  # Regex plus stricte
async def query_metadata(bot: Client, query: CallbackQuery):
    try:
        data = query.data
        
        if data.startswith('metadata_'):
            await bot.send_chat_action(query.message.chat.id, ChatAction.TYPING)
            new_state = data.split('_')[1] == '1'
            user_metadata = await zeexdev.get_metadata_code(query.from_user.id)
            
            await zeexdev.set_metadata_mode(query.from_user.id, bool_meta=new_state)
            
            keyboard = METADATA_TRUE if new_state else METADATA_FALSE
            await query.message.edit(
                f"Vos métadonnées actuelles :-\n\n➜ <code>{user_metadata}</code>",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        elif data == 'custom_metadata':
            await bot.send_chat_action(query.message.chat.id, ChatAction.TYPING)
            await query.message.delete()

            # Remplace l'ancien bot.ask() (pyromod) par un simple ForceReply, comme
            # pour le renommage de fichier. Plus de dépendance externe fragile, plus
            # de risque de collision de version avec la lib Pyrogram sous-jacente.
            await bot.send_message(
                chat_id=query.from_user.id,
                text=rkn.SEND_METADATA,
                disable_web_page_preview=True,
                reply_markup=ForceReply(True)
            )
                
    except Exception as e:
        print(f"Error in query_metadata: {e}")
        await query.message.reply_text("❌ Une erreur s'est produite. Veuillez réessayer.")


@Client.on_message(filters.private & filters.reply & filters.text)
async def metadata_reply(bot: Client, message: Message):
    reply_message = message.reply_to_message

    is_metadata_prompt = (
        reply_message.reply_markup
        and isinstance(reply_message.reply_markup, ForceReply)
        and reply_message.text
        and METADATA_PROMPT_MARKER in reply_message.text
    )
    if not is_metadata_prompt:
        return await message.continue_propagation()

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    RknDev = await message.reply_text("<i><b>Veuillez patienter...</b></i>", reply_to_message_id=message.id)

    await zeexdev.set_metadata_code(message.from_user.id, metadata_code=message.text)
    await RknDev.edit("<b>Votre code de métadonnées a été défini avec succès ✅</b>")

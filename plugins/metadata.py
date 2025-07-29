from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ChatAction  # Pour les indicateurs visuels
from helper.database import zeexdev
from pyromod.exceptions import ListenerTimeout
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

@Client.on_message(filters.private & filters.command('metadata'))
async def handle_metadata(bot: Client, message: Message):
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    RknDev = await message.reply_text("**Veuillez patienter...**", reply_to_message_id=message.id)
    
    bool_metadata = await zeexdev.get_metadata_mode(message.from_user.id)
    user_metadata = await zeexdev.get_metadata_code(message.from_user.id)
    
    keyboard = METADATA_TRUE if bool_metadata else METADATA_FALSE
    await RknDev.edit(
        f"Vos métadonnées actuelles :-\n\n➜ `{user_metadata}`",
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
                f"Vos métadonnées actuelles :-\n\n➜ `{user_metadata}`",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            
        elif data == 'custom_metadata':
            await bot.send_chat_action(query.message.chat.id, ChatAction.TYPING)
            await query.message.delete()
            
            try:
                metadata_msg = await bot.ask(
                    text=rkn.SEND_METADATA,
                    chat_id=query.from_user.id,
                    filters=filters.text,
                    timeout=30,
                    disable_web_page_preview=True
                )
                
                await bot.send_chat_action(query.message.chat.id, ChatAction.TYPING)
                RknDev = await query.message.reply_text("**Veuillez patienter...**", reply_to_message_id=metadata_msg.id)
                
                await zeexdev.set_metadata_code(query.from_user.id, metadata_code=metadata_msg.text)
                await RknDev.edit("**Votre code de métadonnées a été défini avec succès ✅**")
                
            except ListenerTimeout:
                await query.message.reply_text(
                    "⚠️ Erreur !\n\n**Temps de requête écoulé.**\nRedémarrez avec /metadata",
                    reply_to_message_id=query.message.id
                )
                
    except Exception as e:
        print(f"Error in query_metadata: {e}")
        await query.message.reply_text("❌ Une erreur s'est produite. Veuillez réessayer.")
# (c) @RknDeveloperr — modifié pour SukunaRenamer

"""
Apache License 2.0
Copyright (c) 2022 @Digital_Botz
"""

# extra imports
import math, time, re, datetime, pytz, os, hashlib, hmac, json
from urllib.parse import parse_qsl
from config import Config, rkn 

# pyrogram imports
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 5.00) == 0 or current == total:        
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "{0}{1}".format(
            ''.join(["▣" for i in range(math.floor(percentage / 5))]),
            ''.join(["▢" for i in range(20 - math.floor(percentage / 5))])
        )            
        tmp = progress + rkn.RKN_PROGRESS.format( 
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),            
            estimated_total_time if estimated_total_time != '' else "0 s"
        )
        try:
            await message.edit(
                text=f"{ud_type}\n\n{tmp}",               
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✖️ 𝙰𝙽𝙽𝚄𝙻𝙴𝚁 ✖️", callback_data="close")]])                                               
            )
        except:
            pass

def humanbytes(size):    
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'ʙ'


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "ᴅ, ") if days else "") + \
        ((str(hours) + "ʜ, ") if hours else "") + \
        ((str(minutes) + "ᴍ, ") if minutes else "") + \
        ((str(seconds) + "ꜱ, ") if seconds else "") + \
        ((str(milliseconds) + "ᴍꜱ, ") if milliseconds else "")
    return tmp[:-2] 

def convert(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60      
    return "%d:%02d:%02d" % (hour, minutes, seconds)

async def send_log(b, u):
    if Config.LOG_CHANNEL is not None:
        curr = datetime.datetime.now(pytz.timezone("Africa/Lome"))
        date = curr.strftime('%d %B, %Y')
        time_ = curr.strftime('%I:%M:%S %p')
        await b.send_message(
            Config.LOG_CHANNEL,
            f"<b>--Nᴏᴜᴠᴇᴀᴜ Vᴀɪssᴇᴀᴜ--</b>\n\nUtilisateur: {u.mention}\nId: <code>{u.id}</code>\nUn: @{u.username}\n\nDate: {date}\nHeure: {time_}\n\nPar: {b.mention}"
        )

async def get_seconds(time_string):
    def extract_value_and_unit(ts):
        value = ""
        unit = ""
        index = 0
        while index < len(ts) and ts[index].isdigit():
            value += ts[index]
            index += 1
        unit = ts[index:].lstrip()
        if value:
            value = int(value)
        return value, unit
    value, unit = extract_value_and_unit(time_string)
    if unit == 's':
        return value
    elif unit == 'min':
        return value * 60
    elif unit == 'hour':
        return value * 3600
    elif unit == 'day':
        return value * 86400
    elif unit == 'month':
        return value * 86400 * 30
    elif unit == 'year':
        return value * 86400 * 365
    else:
        return 0
        
def add_prefix_suffix(input_string, prefix='', suffix=''):
    pattern = r'(?P<filename>.*?)(\.\w+)?$'
    match = re.search(pattern, input_string)
    if match:
        filename = match.group('filename')
        extension = match.group(2) or ''
        if prefix == None:
            if suffix == None:
                return f"{filename}{extension}"
            return f"{filename} {suffix}{extension}"
        elif suffix == None:
            if prefix == None:
               return f"{filename}{extension}"
            return f"{prefix} {filename}{extension}"
        else:
            return f"{prefix} {filename} {suffix}{extension}"
    else:
        return input_string

async def remove_path(ph_path, file_path, dl_path, metadata_path):
    if os.path.lexists(ph_path):
        os.remove(ph_path)
    if os.path.lexists(file_path):
        os.remove(file_path)
    if os.path.lexists(dl_path):
        os.remove(dl_path)
    if os.path.lexists(metadata_path):
        os.remove(metadata_path)


# ===================== VÉRIFICATION TELEGRAM WEBAPP INIT DATA =====================
# Doc officielle : https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
# Empêche quiconque de forger une requête vers l'API de récompense sans avoir réellement
# ouvert la Mini App depuis un compte Telegram valide.

def verify_telegram_init_data(init_data: str, bot_token: str, max_age_seconds: int = 86400):
    """Retourne {"user": {...}, "auth_date": int, "raw": {...}} si valide, sinon None."""
    if not init_data or not bot_token:
        return None
    try:
        parsed = dict(parse_qsl(init_data, strict_parsing=True))
    except Exception:
        return None

    received_hash = parsed.pop('hash', None)
    if not received_hash:
        return None

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        return None

    try:
        auth_date = int(parsed.get('auth_date', 0))
    except ValueError:
        return None

    if max_age_seconds and (time.time() - auth_date) > max_age_seconds:
        return None

    user = None
    if parsed.get('user'):
        try:
            user = json.loads(parsed['user'])
        except Exception:
            return None

    if not user or not user.get('id'):
        return None

    return {"user": user, "auth_date": auth_date, "raw": parsed}

# Rkn Developer 
# Don't Remove Credit 😔

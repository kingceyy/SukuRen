import re, os, time
id_pattern = re.compile(r'^.\d+$') 

class Config(object):
    # Configuration client ZeeXDev
    API_ID = os.environ.get("API_ID", "25926022")
    API_HASH = os.environ.get("API_HASH", "30db27d9e56d854fb5e943723268db32")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7312727906:AAFrkZ712b6mg0Fwgfsx7dZNSJbIm5s210M") 

    # Session string requise pour compte premium
    STRING_SESSION = os.environ.get("STRING_SESSION", "")
    
    # Configuration base de données
    DB_NAME = os.environ.get("DB_NAME","TELEGRAMBOTS")     
    DB_URL = os.environ.get("DB_URL","mongodb+srv://Ethan:Ethan123@telegrambots.lva9j.mongodb.net/?retryWrites=true&w=majority&appName=TELEGRAMBOTS")
 
    # Autres configurations
    RKN_PIC = os.environ.get("RKN_PIC", "https://www.imghippo.com/i/xDs7558uYw.jpg")
    ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '8140299716').split()]
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002698474966"))

    # Limite d'upload gratuite
    FREE_UPLOAD_LIMIT = 6442450944 # Calcul 6*1024*1024*1024
    
    # Abonnement forcé
    try:
        FORCE_SUB = int(os.environ.get("FORCE_SUB", "Godanimes")) 
    except:
        FORCE_SUB = os.environ.get("FORCE_SUB", "ZeeXDev")
        
    # Configuration réponse web     
    PORT = int(os.environ.get("PORT", "8080"))
    BOT_UPTIME = time.time()

class rkn(object):
    # Configuration texte
    START_TXT = """<b>Bonjour, {}👋

C'est Zoro Renamet Bot. un des plus puissants bots de renommage de fichiers qui soit. avec moi, renommer tout avec une facilité et une rapidité de dingue

<blockquote>Créé par : @ZeeXDev 💞</blockquote></b>"""

    ABOUT_TXT = """<b>╭───────────⍟
├🤖 Mon nom : {}
├🖥️ Développeurs : {}
├👨‍💻 Programmeur : {}
├📕 Bibliothèque : {}
├✏️ Langage : {}
├💾 Base de données : {}
├📊 Version : V6.0</b>     
╰───────────────⍟ """

    HELP_TXT = """
<b>•></b> /start - Démarrer le bot

✏️ <b><u>Comment renommer un fichier</u></b>
<b>•></b> Envoyez un fichier et indiquez le nouveau nom
<b>•></b> Sélectionnez le format [document, vidéo, audio]           
ℹ️ Aide supplémentaire : <a href=https://t.me/DigitalBotz_Support>Groupe de support</a>
"""

    UPGRADE= """
•⪼ ★Forfaits     -    ⏳Durée -  💸Prix - Limite 
•⪼ 🏆Pro -    1 mois -   179₹ - 100Go
•⪼ 💎 Ultra Pro  -   1 mois -   199₹ - 1000Go

- Remise de 9₹ sur tous les forfaits
    """
    
    THUMBNAIL = """
🌌 <b><u>Comment définir une miniature</u></b>

<b>•></b> Envoyez une photo pour la définir comme miniature
<b>•></b> /del_thumb - Supprimer votre miniature
<b>•></b> /view_thumb - Voir votre miniature actuelle
"""
    
    CAPTION= """
📑 <b><u>Comment définir une légende personnalisée</u></b>

<b>•></b> /set_caption - Définir une légende
<b>•></b> /see_caption - Voir votre légende
<b>•></b> /del_caption - Supprimer votre légende

Exemple : `/set_caption 📕 Nom : {filename}
💾 Taille : {filesize}
⏰ Durée : {duration}`
"""
    
    BOT_STATUS = """
⚡️ État du bot ⚡️

⌚️ Temps actif : `{}`
👭 Utilisateurs : `{}`
💸 Utilisateurs premium : `{}`
֍ Upload : `{}`
⊙ Download : `{}`
"""
    
    LIVE_STATUS = """
⚡ État du serveur ⚡

Temps actif : `{}`
CPU : `{}%`
RAM : `{}%` 
Espace total : `{}`
Espace utilisé : `{} {}%`
Espace libre : `{}`
Upload : `{}`
Download : `{}`
V𝟹.𝟶.𝟶 [STABLE]
"""
    
    DIGITAL_METADATA = """
❪ Métadonnées personnalisées ❫

- /metadata - Définir/modifier vos métadonnées

Exemple :
<code>-map 0 -c:s copy -c:a copy -c:v copy -metadata title="Powered By:- @ZeeXDev" -metadata author="@ZeeXClub" -metadata:s:s title="Subtitled By :- @ZeeXDev" -metadata:s:a title="By :- @ZeeXDev" -metadata:s:v title="By:- @ZeeXClub"</code>

📥 Aide : @ZeeXDev
"""
    
    CUSTOM_FILE_NAME = """
<u>🖋️ Nom de fichier personnalisé</u>

Vous pouvez ajouter un préfixe et suffixe à vos fichiers

➢ /set_prefix - Ajouter un préfixe
➢ /see_prefix - Voir votre préfixe
➢ /del_prefix - Supprimer votre préfixe
➢ /set_suffix - Ajouter un suffixe
➢ /see_suffix - Voir votre suffixe
➢ /del_suffix - Supprimer votre suffixe

Exemple : `/set_suffix @ZeeXDev`
Exemple : `/set_prefix @ZeeXDev`
"""
    
    DEV_TXT = """<b><u>⛔️⛔️⛔️MESSAGE URGENT‼️‼️‼️ </u>

Rejoignez Notre Groupe de film & de séries. Dans ce groupe, il faut juste écrire le nom du film ou de la série, pour le recevoir

<u>EXEMPLE:</u>

 <code>-Loki 
Warrior
Hulk
Squid Game</code>

En écrivant le nom, Un bot va vous l'envoyé. il faut et seulement écrire le nom du film.


<a href='t.me/ZeeXClub'>Rejoindre le groupe</a>
<a href='t.me/ZeeXClub'>Rejoindre le groupe</a>
<a href='t.me/ZeeXClub'>Rejoindre le groupe</a>


pour tout Problème contactez moi : <a href='t.me/ZeeXDevBot'>◡‌⃝ㅤ🇰ιηg¢єу</a></b>"""
    
    SEND_METADATA = """
❪ Métadonnées personnalisées ❫

Exemple :
<code>-map 0 -c:s copy -c:a copy -c:v copy -metadata title="Powered By:- @ZeeXDev" -metadata author="@ZeeXClub" -metadata:s:s title="Subtitled By :- @ZeeXDev" -metadata:s:a title="By :- @ZeeXDev" -metadata:s:v title="By:- @Kingcey"</code>

📥 Aide : @ZeeXDev
"""
    
    RKN_PROGRESS = """<b>\n
╭━━━━❰TRAITEMENT EN COURS...❱━➣
┣⪼ 🗃️ Taille: {1} | {2}
┣⪼ ⏳️ Progression : {0}%
┣⪼ 🚀 Vitesse: {3}/s
┣⪼ ⏰️ Temps restant: {4}
╰━━━━━━━━━━━━━━━➣ </b>"""
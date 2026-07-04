import re, os, time
id_pattern = re.compile(r'^.\d+$') 

class Config(object):
    # Configuration client
    API_ID = os.environ.get("API_ID", "25926022")
    API_HASH = os.environ.get("API_HASH", "30db27d9e56d854fb5e943723268db32")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7312727906:AAFrkZ712b6mg0Fwgfsx7dZNSJbIm5s210M") 

    # Session string requise pour compte premium (fichiers > 2Go)
    STRING_SESSION = os.environ.get("STRING_SESSION", "")
    
    # Configuration base de données
    DB_NAME = os.environ.get("DB_NAME","TELEGRAMBOTS")     
    DB_URL = os.environ.get("DB_URL","mongodb+srv://Ethan:Ethan123@telegrambots.lva9j.mongodb.net/?retryWrites=true&w=majority&appName=TELEGRAMBOTS")
 
    # Autres configurations
    RKN_PIC = os.environ.get("RKN_PIC", "https://www.imghippo.com/i/xDs7558uYw.jpg")
    ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '8140299716').split()]
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1002698474966"))

    # Abonnement forcé
    try:
        FORCE_SUB = int(os.environ.get("FORCE_SUB", "cineflixi")) 
    except:
        FORCE_SUB = os.environ.get("FORCE_SUB", "itz_kingcey")
        
    # Configuration réponse web     
    PORT = int(os.environ.get("PORT", "8080"))
    BOT_UPTIME = time.time()

    # ===================== SYSTÈME DE QUOTAS (SukunaRenamer) =====================
    # 1 quota = 1 fichier renommé. Les quotas gagnés par pub expirent, pas les quotas premium.
    QUOTA_PER_AD = int(os.environ.get("QUOTA_PER_AD", "15"))            # quotas offerts par pub complète
    QUOTA_EXPIRY_HOURS = int(os.environ.get("QUOTA_EXPIRY_HOURS", "35"))  # durée de vie des quotas gratuits
    AD_COOLDOWN_SECONDS = int(os.environ.get("AD_COOLDOWN_SECONDS", "45"))  # anti-spam entre 2 pubs
    AD_SESSION_MAX_AGE = int(os.environ.get("AD_SESSION_MAX_AGE", "600"))  # durée de validité d'un jeton de session pub (10 min)
    FREE_QUOTA_ON_SIGNUP = int(os.environ.get("FREE_QUOTA_ON_SIGNUP", "10"))  # petit cadeau de bienvenue

    # ===================== MINI APP / PUBLICITÉS =====================
    WEBAPP_URL = os.environ.get("WEBAPP_URL", "https://sukurenam.vercel.app")
    ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "https://sukurenam.vercel.app")
    ADSGRAM_BLOCK_ID = os.environ.get("ADSGRAM_BLOCK_ID", "37226")
    MONETAG_ZONE_ID = os.environ.get("MONETAG_ZONE_ID", "REMPLACE_PAR_TA_ZONE_MONETAG")

    # Taille max en upload local (limite technique liée à l'API Bot Telegram, pas au quota)
    FREE_UPLOAD_LIMIT = 2000 * 1024 * 1024  # 2 Go


class rkn(object):
    # ===================== TEXTES — THÈME RYOMEN SUKUNA =====================

    START_TXT = """<b>Ryomen Sukuna Fukuma Mizushi.
20 doigts, une seule volonté : la puissance.

Salut, {} 👁️

Je suis SukunaRenamer, le Roi des Malédictions du renommage de fichiers sur Telegram. Ce que les autres bots mettent une éternité à faire, je le fais en un claquement de doigts.

Envoie-moi n'importe quel fichier, donne-lui un nouveau nom, et regarde ma malédiction opérer.

<blockquote>⛩️ Domaine : @Kingcey</blockquote></b>"""

    ABOUT_TXT = """<b>╭───────────⍟
├👹 Nom : {}
├⛩️ Domaine Malveillant : {}
├👑 Roi des malédictions : {}
├📕 Technique innée : {}
├✏️ Langage rituel : {}
├💾 Sceau de stockage : {}
├📊 Version : V1.0 「Ryoiki Tenkai」</b>     
╰───────────────⍟ """

    HELP_TXT = """
<b>👹 Grimoire de Sukuna</b>

<b>•></b> /start — Invoquer le bot
<b>•></b> /mesquotas — Voir tes quotas restants
<b>•></b> /plans — Devenir un vaisseau premium

✏️ <b><u>Comment renommer un fichier</u></b>
<b>•></b> Envoie-moi un fichier (1 quota = 1 fichier)
<b>•></b> Donne-moi le nouveau nom
<b>•></b> Choisis le format [document, vidéo, audio]
<b>•></b> Je l'exécute. Aussi simple que ça.

⚡ Plus de quotas ? Regarde une pub, je t'en offre 15 de plus.

ℹ️ Aide : <a href=https://t.me/DigitalBotz_Support>Groupe de support</a>
"""

    UPGRADE = """
👑 <b>Devenir un vaisseau premium de Sukuna</b>

Les quotas premium n'expirent jamais et te suivent partout — même quand les malédictions gratuites se dissipent après {}h.

•⪼ 🩸 Réserve — quotas premium sans expiration, prix libre
•⪼ 👁️ Statut Vaisseau — accès prioritaire + limite de fichiers relevée

Contacte l'administrateur pour négocier ton tribut de quotas, ou regarde une pub pour obtenir des quotas gratuits immédiatement.
    """
    
    THUMBNAIL = """
🌌 <b><u>Sceau visuel (miniature)</u></b>

<b>•></b> Envoie une photo pour la définir comme miniature
<b>•></b> /del_thumb — Briser le sceau
<b>•></b> /view_thumb — Contempler ton sceau actuel
"""
    
    CAPTION = """
📑 <b><u>Incantation personnalisée (légende)</u></b>

<b>•></b> /set_caption — Graver ta légende
<b>•></b> /see_caption — Lire ta légende
<b>•></b> /del_caption — Effacer ta légende

Exemple : <code>/set_caption 📕 Nom : {filename}
💾 Taille : {filesize}
⏰ Durée : {duration}</code>
"""
    
    BOT_STATUS = """
👹 État du Domaine 👹

⌚️ Éveillé depuis : <code>{}</code>
👭 Vaisseaux enregistrés : <code>{}</code>
💸 Vaisseaux premium : <code>{}</code>
֍ Malédictions envoyées : <code>{}</code>
⊙ Malédictions reçues : <code>{}</code>
"""
    
    LIVE_STATUS = """
⚡ Pouls du Domaine ⚡

Éveillé depuis : <code>{}</code>
Énergie maudite (CPU) : <code>{}%</code>
Réserve (RAM) : <code>{}%</code> 
Espace total : <code>{}</code>
Espace utilisé : <code>{} {}%</code>
Espace libre : <code>{}</code>
Upload : <code>{}</code>
Download : <code>{}</code>
V𝟷.𝟶 「STABLE」
"""
    
    DIGITAL_METADATA = """
❪ Métadonnées maudites ❫

- /metadata — Définir/modifier tes métadonnées

Exemple :
<code>-map 0 -c:s copy -c:a copy -c:v copy -metadata title="Powered By:- @Kingcey" -metadata author="@Kingcey" -metadata:s:s title="Subtitled By :- @Kingcey" -metadata:s:a title="By :- @Kingcey" -metadata:s:v title="By:- @Kingcey"</code>

📥 Aide : @Kingcey
"""

    SEND_METADATA = """
❪ Métadonnées personnalisées ❫

Envoie ta propre commande de métadonnées ffmpeg.

Exemple :
<code>-map 0 -c:s copy -c:a copy -c:v copy -metadata title="Powered By:- @Kingcey" -metadata author="@Kingcey" -metadata:s:s title="Subtitled By :- @Kingcey" -metadata:s:a title="By :- @Kingcey" -metadata:s:v title="By:- @Kingcey"</code>

📥 Aide : @Kingcey
"""
    
    CUSTOM_FILE_NAME = """
<u>🖋️ Nom de fichier maudit personnalisé</u>

Tu peux ajouter un préfixe et un suffixe à tes fichiers

➢ /set_prefix — Ajouter un préfixe
➢ /see_prefix — Voir ton préfixe
➢ /del_prefix — Supprimer ton préfixe
➢ /set_suffix — Ajouter un suffixe
➢ /see_suffix — Voir ton suffixe
➢ /del_suffix — Supprimer ton suffixe

Exemple : <code>/set_suffix @Kingcey</code>
Exemple : <code>/set_prefix @Kingcey</code>
"""
    
    DEV_TXT = """<b><u>⛩️⛩️⛩️ MESSAGE DU ROI DES MALÉDICTIONS ⛩️⛩️⛩️</u>

Rejoins mon domaine pour suivre les mises à jour, les nouveautés et parler avec l'administrateur.

<a href='t.me/ZeeXClub'>Entrer dans le domaine</a>

Pour tout problème, contacte : <a href='t.me/ZeeXDevBot'>◡‌⃝ㅤ👹 Kιηg¢єу</a></b>"""

    RKN_PROGRESS = """<b>\n
╭━━━━❰RITUEL EN COURS...❱━➣
┣⪼ 🗃️ Taille: {1} | {2}
┣⪼ ⏳️ Progression : {0}%
┣⪼ 🚀 Vitesse: {3}/s
┣⪼ ⏰️ Temps restant: {4}
╰━━━━━━━━━━━━━━━➣ </b>"""

    # ===================== TEXTES QUOTAS =====================

    QUOTA_LOW_TXT = """<b>👹 Tes quotas sont épuisés.

Sukuna n'agit pas gratuitement éternellement. Il te reste <code>{remain}</code> quota(s), mais renommer ce fichier en demande davantage.

⚡ Regarde une courte pub pour recevoir <b>{per_ad} quotas</b> instantanément (valables {expiry}h)
👑 Ou passe premium pour des quotas qui n'expirent jamais</b>"""

    QUOTA_INFO_TXT = """<b>👁️ Bilan de tes quotas, {user}

🩸 Quotas gratuits (expirent) : <code>{free}</code>
👑 Quotas premium (illimités dans le temps) : <code>{premium}</code>
⚡ Total disponible : <code>{total}</code>

{expiry_line}

1 quota = 1 fichier renommé.</b>"""

    QUOTA_EARN_INTRO_TXT = """<b>⚡ Ouvre la Mini App ci-dessous pour regarder une pub et recevoir tes quotas.

Chaque pub complète = +{per_ad} quotas, valables {expiry}h.</b>"""

    QUOTA_REWARD_ADMIN_LOG = """<b>👹 Quota crédité

👤 Utilisateur : {mention}
🆔 ID : <code>{user_id}</code>
⚡ Quotas ajoutés : {amount}
⏰ Expire dans : {expiry}h</b>"""

    QUOTA_ADMIN_USAGE = """<b>👑 Commande admin /quota

Utilisation :
<code>/quota add user_id montant</code> — ajoute des quotas premium (n'expirent jamais)
<code>/quota remove user_id montant</code> — retire des quotas premium
<code>/quota set user_id montant</code> — fixe le solde premium
<code>/quota info user_id</code> — voir le solde d'un utilisateur

Exemple : <code>/quota add 123456789 100</code></b>"""

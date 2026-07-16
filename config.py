import re, os, time
id_pattern = re.compile(r'^.\d+$') 

class Config(object):
    # Configuration client
    API_ID = os.environ.get("API_ID", "37641587")
    API_HASH = os.environ.get("API_HASH", "9bce1167e828939f39452795e56202a9")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "7312727906:AAFrkZ712b6mg0Fwgfsx7dZNSJbIm5s210M") 

    # Session string requise pour compte premium (fichiers > 2Go)
    STRING_SESSION = os.environ.get("STRING_SESSION", "")
    
    # Configuration base de données
    DB_NAME = os.environ.get("DB_NAME","TELEGRAMBOTS")     
    DB_URL = os.environ.get("DB_URL","mongodb+srv://Ethan:Ethan123@telegrambots.lva9j.mongodb.net/?retryWrites=true&w=majority&appName=TELEGRAMBOTS")
 
    # Autres configurations
    RKN_PIC = os.environ.get("RKN_PIC", "https://i.ibb.co/dsX1bNTN/x.jpg")
    ADMIN = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMIN', '8467461906').split()]
    LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1003340962000"))

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
    ADSGRAM_BLOCK_ID = os.environ.get("ADSGRAM_BLOCK_ID", "37235")
    MONETAG_ZONE_ID = os.environ.get("MONETAG_ZONE_ID", "REMPLACE_PAR_TA_ZONE_MONETAG")

    # Taille max en upload local (limite technique liée à l'API Bot Telegram, pas au quota)
    FREE_UPLOAD_LIMIT = 2000 * 1024 * 1024  # 2 Go


class rkn(object):
    # ===================== TEXTES — THÈME RYOMEN SUKUNA =====================
    # Tags HTML utilisés partout : <b> emphase, <i> nuance, <code> valeurs/commandes,
    # <blockquote> bloc mis en avant. Textes volontairement courts et scannables.

    START_TXT = """<b>Ryomen Sukuna</b> — Roi des Malédictions du renommage.

Envoie-moi un fichier, donne-lui un nom, je m'en charge en un instant.

<blockquote>Salut {0} 👁️ — prêt à renommer ?</blockquote>"""

    ABOUT_TXT = """<b>SukunaRenamer</b>
<i>Roi des malédictions du renommage de fichiers.</i>

<blockquote>Bot : {0}
Contact : <a href="https://t.me/itz_kingcey">It'z Kingcey</a>
Version : <code>V1.0 「Ryoiki Tenkai」</code></blockquote>"""

    HELP_TXT = """<b>Grimoire de Sukuna</b>

<b>/start</b> — Invoquer le bot
<b>/mesquotas</b> — Voir tes quotas
<b>/plans</b> — Devenir premium

<blockquote><i>Renommer un fichier :</i>
1. Envoie ton fichier
2. Donne le nouveau nom
3. Choisis le format</blockquote>

Plus de quotas ? Regarde une pub, +15 offerts.

<a href="https://t.me/+u5qxRjapSF05YTBk">Groupe de support</a>"""

    UPGRADE = """<b>Passer premium</b>

Les quotas premium n'expirent jamais, contrairement aux quotas gratuits qui se dissipent après {0}h.

<blockquote><b>Premium</b> : quotas à vie, accès prioritaire, fichiers jusqu'à 4 Go</blockquote>

Contacte l'administrateur pour activer ton plan, ou regarde une pub pour des quotas gratuits immédiats."""

    THUMBNAIL = """<b>Miniature personnalisée</b>

Envoie une photo pour la définir comme miniature.

<b>/del_thumb</b> — Supprimer
<b>/view_thumb</b> — Voir la miniature actuelle"""

    CAPTION = """<b>Légende personnalisée</b>

<b>/set_caption</b> — Définir
<b>/see_caption</b> — Voir
<b>/del_caption</b> — Supprimer

<blockquote><code>/set_caption Nom : {filename}
Taille : {filesize}
Durée : {duration}</code></blockquote>"""

    BOT_STATUS = """<b>État du Domaine</b>

<blockquote>Éveillé depuis : <code>{}</code>
Vaisseaux enregistrés : <code>{}</code>
Vaisseaux premium : <code>{}</code>
Malédictions envoyées : <code>{}</code>
Malédictions reçues : <code>{}</code></blockquote>"""

    LIVE_STATUS = """<b>Pouls du Domaine</b>

<blockquote>Éveillé depuis : <code>{}</code>
CPU : <code>{}%</code>
RAM : <code>{}%</code>
Espace total : <code>{}</code>
Espace utilisé : <code>{} ({}%)</code>
Espace libre : <code>{}</code>
Upload : <code>{}</code>
Download : <code>{}</code></blockquote>

<i>V1.0 「STABLE」</i>"""

    DIGITAL_METADATA = """<b>Métadonnées</b>

<b>/metadata</b> — Définir tes métadonnées

<blockquote><code>-map 0 -c:s copy -c:a copy -c:v copy -metadata title="Powered By:- @Kingcey" -metadata author="@Kingcey" -metadata:s:s title="Subtitled By :- @Kingcey" -metadata:s:a title="By :- @Kingcey" -metadata:s:v title="By:- @Kingcey"</code></blockquote>

Aide : @Kingcey"""

    SEND_METADATA = """<b>Métadonnées personnalisées</b>

Envoie ta propre commande ffmpeg.

<blockquote><code>-map 0 -c:s copy -c:a copy -c:v copy -metadata title="Powered By:- @Kingcey" -metadata author="@Kingcey" -metadata:s:s title="Subtitled By :- @Kingcey" -metadata:s:a title="By :- @Kingcey" -metadata:s:v title="By:- @Kingcey"</code></blockquote>

Aide : @Kingcey"""

    CUSTOM_FILE_NAME = """<b>Préfixe / suffixe</b>

<b>/set_prefix</b> — Ajouter · <b>/see_prefix</b> — Voir · <b>/del_prefix</b> — Supprimer
<b>/set_suffix</b> — Ajouter · <b>/see_suffix</b> — Voir · <b>/del_suffix</b> — Supprimer

<blockquote><code>/set_suffix @Kingcey</code></blockquote>"""

    DEV_TXT = """<b>Rejoins le domaine</b>

Mises à jour, nouveautés, contact direct avec l'administrateur.

<blockquote><a href="https://t.me/ZeeXClub">Entrer dans le domaine</a></blockquote>

Un problème ? <a href="https://t.me/ZeeXDevBot">Contacter Kingcey</a>"""

    RKN_PROGRESS = """<b>Rituel en cours…</b>
<blockquote><code>{1} | {2}</code>
Progression : <code>{0}%</code>
Vitesse : <code>{3}/s</code>
Temps restant : <code>{4}</code></blockquote>"""

    # ===================== TEXTES QUOTAS =====================

    QUOTA_LOW_TXT = """<b>Quotas épuisés</b>

Il te reste <code>{remain}</code> quota(s), insuffisant pour ce fichier.

<blockquote>Regarde une pub → +<b>{per_ad}</b> quotas (valables {expiry}h)
Ou passe premium → quotas à vie</blockquote>"""

    QUOTA_INFO_TXT = """<b>Quotas de {user}</b>

<blockquote>Gratuits : <code>{free}</code>
Premium : <code>{premium}</code>
Total : <code>{total}</code></blockquote>

<i>{expiry_line}</i>

1 quota = 1 fichier renommé."""

    QUOTA_EARN_INTRO_TXT = """<b>Regarde une pub</b>

Ouvre la Mini App ci-dessous. Chaque pub complète = +<b>{per_ad}</b> quotas (valables {expiry}h)."""

    QUOTA_REWARD_ADMIN_LOG = """<b>Quota crédité</b>

<blockquote>Utilisateur : {mention}
ID : <code>{user_id}</code>
Ajouté : <code>{amount}</code>
Expire dans : <code>{expiry}h</code></blockquote>"""

    QUOTA_ADMIN_USAGE = """<b>Commande /quota</b>

<code>/quota add user_id montant</code> — ajoute des quotas premium
<code>/quota remove user_id montant</code> — retire des quotas premium
<code>/quota set user_id montant</code> — fixe le solde premium
<code>/quota info user_id</code> — voir le solde d'un utilisateur

Exemple : <code>/quota add 123456789 100</code>"""

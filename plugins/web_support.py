# SukunaRenamer — serveur web : health check + API pour la Mini App de récompense pub

from aiohttp import web
import json

from config import Config
from helper.database import zeexdev
from helper.utils import verify_telegram_init_data

Rkn_FileRenameBot = web.RouteTableDef()


def _cors_headers():
    return {
        "Access-Control-Allow-Origin": Config.ALLOWED_ORIGIN,
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }


@Rkn_FileRenameBot.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response("SukunaRenamer")


@Rkn_FileRenameBot.options("/api/{tail:.*}")
async def api_options(request):
    return web.Response(status=204, headers=_cors_headers())


@Rkn_FileRenameBot.post("/api/session")
async def api_session(request):
    """Appelé au chargement de la Mini App. Valide l'utilisateur Telegram et
    renvoie un jeton de session à usage unique + le solde actuel."""
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "invalid_json"}, status=400, headers=_cors_headers())

    init_data = body.get("init_data", "")
    verified = verify_telegram_init_data(init_data, Config.BOT_TOKEN)
    if not verified:
        return web.json_response({"error": "invalid_init_data"}, status=401, headers=_cors_headers())

    user_id = verified["user"]["id"]

    if not await zeexdev.is_user_exist(user_id):
        return web.json_response({"error": "unknown_user", "message": "Fais /start sur le bot d'abord."}, status=403, headers=_cors_headers())

    token = await zeexdev.create_ad_session(user_id)
    balance = await zeexdev.get_quota_balance(user_id)
    cooldown_left = await zeexdev.seconds_until_next_ad(user_id)

    return web.json_response({
        "token": token,
        "balance": {"free": balance["free"], "premium": balance["premium"], "total": balance["total"]},
        "cooldown_seconds_left": cooldown_left,
        "quota_per_ad": Config.QUOTA_PER_AD,
        "quota_expiry_hours": Config.QUOTA_EXPIRY_HOURS,
    }, headers=_cors_headers())


@Rkn_FileRenameBot.post("/api/reward")
async def api_reward(request):
    """Appelé après la complétion vérifiée de la pub rewarded AdsGram.
    Crédite les quotas une seule fois par jeton de session, avec cooldown anti-abus."""
    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "invalid_json"}, status=400, headers=_cors_headers())

    init_data = body.get("init_data", "")
    token = body.get("token", "")

    verified = verify_telegram_init_data(init_data, Config.BOT_TOKEN)
    if not verified:
        return web.json_response({"error": "invalid_init_data"}, status=401, headers=_cors_headers())

    user_id = verified["user"]["id"]

    if not await zeexdev.is_user_exist(user_id):
        return web.json_response({"error": "unknown_user"}, status=403, headers=_cors_headers())

    if not token:
        return web.json_response({"error": "missing_token"}, status=400, headers=_cors_headers())

    if not await zeexdev.can_watch_ad(user_id):
        cooldown_left = await zeexdev.seconds_until_next_ad(user_id)
        return web.json_response({"error": "cooldown", "cooldown_seconds_left": cooldown_left}, status=429, headers=_cors_headers())

    session_ok = await zeexdev.consume_ad_session(token, user_id)
    if not session_ok:
        return web.json_response({"error": "invalid_or_used_token"}, status=409, headers=_cors_headers())

    expires_at = await zeexdev.add_free_quota(user_id, Config.QUOTA_PER_AD)
    await zeexdev.set_last_ad_reward(user_id)
    balance = await zeexdev.get_quota_balance(user_id)

    return web.json_response({
        "success": True,
        "added": Config.QUOTA_PER_AD,
        "expires_at": expires_at.isoformat(),
        "balance": {"free": balance["free"], "premium": balance["premium"], "total": balance["total"]},
    }, headers=_cors_headers())


async def web_server():
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(Rkn_FileRenameBot)
    return web_app

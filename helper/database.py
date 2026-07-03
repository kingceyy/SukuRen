# (c) @RknDeveloperr — modifié pour SukunaRenamer (système de quotas)

"""
Apache License 2.0
Copyright (c) 2022 @zeexdev
"""

# database imports
import motor.motor_asyncio, datetime, pytz, uuid

# bots imports
from config import Config
from helper.utils import send_log

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.user
        self.premium = self.db.premium
        self.ad_sessions = self.db.ad_sessions

    def new_user(self, id):
        return dict(
            _id=int(id),
            join_date=datetime.date.today().isoformat(),
            file_id=None,
            caption=None,
            prefix=None,
            suffix=None,
            usertype="Free",
            metadata_mode=False,
            metadata_code=""" -map 0 -c:s copy -c:a copy -c:v copy -metadata title="Powered By:- @Kingcey" -metadata author="@Kingcey" -metadata:s:s title="Subtitled By :- @Kingcey" -metadata:s:a title="By :- @Kingcey" -metadata:s:v title="By:- @Kingcey" """,
            has_free_trial=False,
            # --- quotas ---
            quota_batches=[],       # [{amount, expires_at, granted_at}] — quotas gagnés par pub, expirent
            quota_premium=Config.FREE_QUOTA_ON_SIGNUP,  # quotas premium/admin, n'expirent jamais
            last_ad_reward=None,
            ban_status=dict(
                is_banned=False,
                ban_duration=0,
                banned_on=datetime.date.max.isoformat(),
                ban_reason=''
            )
        )

    async def add_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.new_user(u.id)
            await self.col.insert_one(user)            
            await send_log(b, u)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.col.delete_many({'_id': int(user_id)})
    
    async def set_thumbnail(self, id, file_id):
        await self.col.update_one({'_id': int(id)}, {'$set': {'file_id': file_id}})

    async def get_thumbnail(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('file_id', None)

    async def set_caption(self, id, caption):
        await self.col.update_one({'_id': int(id)}, {'$set': {'caption': caption}})

    async def get_caption(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('caption', None)

    async def set_prefix(self, id, prefix):
        await self.col.update_one({'_id': int(id)}, {'$set': {'prefix': prefix}})

    async def get_prefix(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('prefix', None)

    async def set_suffix(self, id, suffix):
        await self.col.update_one({'_id': int(id)}, {'$set': {'suffix': suffix}})

    async def get_suffix(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('suffix', None)

    async def set_metadata_mode(self, id, bool_meta):
        await self.col.update_one({'_id': int(id)}, {'$set': {'metadata_mode': bool_meta}})

    async def get_metadata_mode(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('metadata_mode', None)

    async def set_metadata_code(self, id, metadata_code):
        await self.col.update_one({'_id': int(id)}, {'$set': {'metadata_code': metadata_code}})

    async def get_metadata_code(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('metadata_code', None)

    async def set_usertype(self, id, type):
        await self.col.update_one({'_id': int(id)}, {'$set': {'usertype': type}})

    async def get_user_data(self, id) -> dict:
        user_data = await self.col.find_one({'_id': int(id)})
        return user_data or None
        
    async def get_user(self, user_id):
        user_data = await self.premium.find_one({"id": user_id})
        return user_data

    # ===================== SYSTÈME DE QUOTAS =====================

    async def _clean_quota_batches(self, id):
        """Supprime les lots de quotas gratuits expirés et retourne les lots encore valides."""
        user = await self.col.find_one({'_id': int(id)})
        if not user:
            return []
        now = datetime.datetime.now()
        batches = user.get('quota_batches', []) or []
        valid = [b for b in batches if b.get('expires_at') and b['expires_at'] > now]
        if len(valid) != len(batches):
            await self.col.update_one({'_id': int(id)}, {'$set': {'quota_batches': valid}})
        return valid

    async def get_quota_balance(self, id):
        """Retourne {free, premium, total, batches, next_expiry}."""
        batches = await self._clean_quota_batches(id)
        free = sum(int(b.get('amount', 0)) for b in batches)
        user = await self.col.find_one({'_id': int(id)})
        premium = int(user.get('quota_premium', 0)) if user else 0
        next_expiry = None
        if batches:
            next_expiry = min(b['expires_at'] for b in batches)
        return {"free": free, "premium": premium, "total": free + premium, "batches": batches, "next_expiry": next_expiry}

    async def add_free_quota(self, id, amount, valid_hours=None):
        """Ajoute un lot de quotas expirants (ex: obtenus via pub)."""
        valid_hours = valid_hours or Config.QUOTA_EXPIRY_HOURS
        expires_at = datetime.datetime.now() + datetime.timedelta(hours=valid_hours)
        await self.col.update_one(
            {'_id': int(id)},
            {'$push': {'quota_batches': {'amount': int(amount), 'expires_at': expires_at, 'granted_at': datetime.datetime.now()}}},
            upsert=True
        )
        return expires_at

    async def add_premium_quota(self, id, amount):
        """Ajoute des quotas qui n'expirent jamais (admin / achat)."""
        await self.col.update_one({'_id': int(id)}, {'$inc': {'quota_premium': int(amount)}}, upsert=True)

    async def set_premium_quota(self, id, amount):
        await self.col.update_one({'_id': int(id)}, {'$set': {'quota_premium': int(amount)}}, upsert=True)

    async def remove_premium_quota(self, id, amount):
        balance = await self.get_quota_balance(id)
        new_val = max(0, balance['premium'] - int(amount))
        await self.col.update_one({'_id': int(id)}, {'$set': {'quota_premium': new_val}})
        return new_val

    async def consume_quota(self, id, amount=1):
        """Déduit `amount` quotas : les lots gratuits qui expirent le plus tôt d'abord, puis le premium."""
        balance = await self.get_quota_balance(id)
        if balance['total'] < amount:
            return False

        remaining = amount
        batches_sorted = sorted(balance['batches'], key=lambda b: b['expires_at'])
        new_batches = []
        for b in batches_sorted:
            if remaining <= 0:
                new_batches.append(b)
                continue
            if b['amount'] <= remaining:
                remaining -= b['amount']
            else:
                new_batches.append({
                    'amount': b['amount'] - remaining,
                    'expires_at': b['expires_at'],
                    'granted_at': b.get('granted_at')
                })
                remaining = 0

        new_premium = balance['premium']
        if remaining > 0:
            new_premium = max(0, balance['premium'] - remaining)

        await self.col.update_one(
            {'_id': int(id)},
            {'$set': {'quota_batches': new_batches, 'quota_premium': new_premium}}
        )
        return True

    async def can_watch_ad(self, id, cooldown_seconds=None):
        cooldown_seconds = cooldown_seconds if cooldown_seconds is not None else Config.AD_COOLDOWN_SECONDS
        user = await self.col.find_one({'_id': int(id)})
        if not user:
            return True
        last = user.get('last_ad_reward')
        if not last:
            return True
        delta = (datetime.datetime.now() - last).total_seconds()
        return delta >= cooldown_seconds

    async def seconds_until_next_ad(self, id, cooldown_seconds=None):
        cooldown_seconds = cooldown_seconds if cooldown_seconds is not None else Config.AD_COOLDOWN_SECONDS
        user = await self.col.find_one({'_id': int(id)})
        if not user or not user.get('last_ad_reward'):
            return 0
        delta = (datetime.datetime.now() - user['last_ad_reward']).total_seconds()
        return max(0, int(cooldown_seconds - delta))

    async def set_last_ad_reward(self, id):
        await self.col.update_one({'_id': int(id)}, {'$set': {'last_ad_reward': datetime.datetime.now()}}, upsert=True)

    # --- jetons de session pub (anti-rejeu) ---

    async def create_ad_session(self, user_id):
        token = str(uuid.uuid4())
        await self.ad_sessions.insert_one({
            "token": token, "user_id": int(user_id),
            "created_at": datetime.datetime.now(), "used": False
        })
        return token

    async def consume_ad_session(self, token, user_id, max_age_seconds=None):
        max_age_seconds = max_age_seconds or Config.AD_SESSION_MAX_AGE
        session = await self.ad_sessions.find_one({"token": token, "user_id": int(user_id), "used": False})
        if not session:
            return False
        age = (datetime.datetime.now() - session['created_at']).total_seconds()
        if age > max_age_seconds:
            return False
        await self.ad_sessions.update_one({"_id": session["_id"]}, {"$set": {"used": True}})
        return True

    # ===================== PREMIUM (statut, indépendant des quotas) =====================

    async def addpremium(self, user_id, user_data, type):    
        await self.premium.update_one({"id": user_id}, {"$set": user_data}, upsert=True)
        await self.col.update_one({'_id': user_id}, {'$set': {'usertype': type}})
        
    async def remove_premium(self, user_id, type="Free"):
        await self.premium.update_one({"id": user_id}, {"$set": {"expiry_time": None}})
        await self.col.update_one({'_id': user_id}, {'$set': {'usertype': type}})
    
    async def checking_remaining_time(self, user_id):
        user_data = await self.get_user(user_id)
        expiry_time = user_data.get("expiry_time")
        time_left_str = expiry_time - datetime.datetime.now()
        return time_left_str

    async def has_premium_access(self, user_id):
        user_data = await self.get_user(user_id)
        if user_data:
            expiry_time = user_data.get("expiry_time")
            if expiry_time is None:
                return False
            elif isinstance(expiry_time, datetime.datetime) and datetime.datetime.now() <= expiry_time:
                return True
            else:
                await self.remove_premium(user_id)
        return False

    async def total_premium_users_count(self):
        count = await self.premium.count_documents({"expiry_time": {"$gt": datetime.datetime.now()}})
        return count

    async def get_all_premium_users(self):
        all_premium_users = self.premium.find({"expiry_time": {"$gt": datetime.datetime.now()}})
        return all_premium_users

    async def get_free_trial_status(self, user_id):
        user_data = await self.get_user(user_id)
        if user_data:
            return user_data.get("has_free_trial", False)
        return False

    async def give_free_trail(self, user_id):
        seconds, type = 720 * 60, "Trial"
        expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        user_data = {"id": user_id, "expiry_time": expiry_time, "has_free_trial": True}
        await self.addpremium(user_id, user_data, type)
        await self.add_premium_quota(user_id, 50)  # bonus quotas premium pendant l'essai
      
    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_duration=0,
            banned_on=datetime.date.max.isoformat(),
            ban_reason=''
        )
        await self.col.update_one({'_id': int(id)}, {'$set': {'ban_status': ban_status}})

    async def ban_user(self, user_id, ban_duration, ban_reason):
        ban_status = dict(
            is_banned=True,
            ban_duration=ban_duration,
            banned_on=datetime.date.today().isoformat(),
            ban_reason=ban_reason
        )
        await self.col.update_one({'_id': int(user_id)}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_duration=0,
            banned_on=datetime.date.max.isoformat(),
            ban_reason=''
        )
        user = await self.col.find_one({'_id': int(id)})
        return user.get('ban_status', default)

    async def get_all_banned_users(self):
        banned_users = self.col.find({'ban_status.is_banned': True})
        return banned_users
        
zeexdev = Database(Config.DB_URL, Config.DB_NAME)

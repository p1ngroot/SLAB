import aiohttp
import logging
from os import getenv
from datetime import datetime, timedelta
from keyboards import PLAN_MAP


class RemnawaveClient:
    def __init__(self):
        self.url = getenv("REMNAWAVE_API_URL", "").rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {getenv('REMNAWAVE_API_KEY')}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        # UUID внутреннего сквада (не имя — иначе не выдаётся)
        self.squad_uuid = "c494ced2-8eb8-4724-85db-af1688e44259"

    async def _request(self, method, endpoint, json_data=None):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(method, endpoint, json=json_data, headers=self.headers) as r:
                    logging.info(f"[API] {method} {endpoint} | Status: {r.status}")
                    if r.content_type != 'application/json':
                        text = await r.text()
                        logging.warning(f"[API] Non-JSON response: {text[:200]}")
                        return {"error": "not_json", "status": r.status, "text": text}, r.status
                    res = await r.json()
                    logging.info(f"[API] Response: {res}")
                    return res, r.status
            except Exception as e:
                logging.error(f"[API] Exception: {e}")
                return {"error": str(e)}, 500

    def _expire_date(self, plan_id: str) -> str:
        """Вычисляет дату истечения подписки по plan_id."""
        days = 30
        if "12m" in plan_id:
            days = 365
        elif "6m" in plan_id:
            days = 180
        elif "3m" in plan_id:
            days = 90
        return (datetime.utcnow() + timedelta(days=days)).strftime('%Y-%m-%dT%H:%M:%S.000Z')

    async def create_user(self, username: str, plan_id: str = "plan_2dev_1m"):
        """Создаёт юзера с expireAt и squadUuid (не squadName)."""
        endpoint = f"{self.url}/api/users"
        payload = {
            "username": username,
            "expireAt": self._expire_date(plan_id),
            "squadUuid": self.squad_uuid,
        }
        res, status = await self._request("POST", endpoint, payload)

        if status in (200, 201):
            logging.info(f"User {username} created successfully")
        elif status in (400, 409) and "already exists" in str(res):
            logging.info(f"User {username} already exists, skipping creation")
            # Если юзер уже есть — обновляем expireAt через PATCH
            await self.create_subscription(username, plan_id)
        else:
            logging.warning(f"create_user unexpected status {status}: {res}")
        return res, status

    async def create_subscription(self, username: str, plan_id: str):
        """
        В Remnawave подписка создаётся вместе с юзером.
        Здесь обновляем дату истечения через PATCH /api/users/{shortUuid}.
        """
        res, status = await self._request(
            "GET", f"{self.url}/api/subscriptions/by-username/{username}"
        )
        if status != 200:
            logging.warning(f"create_subscription: cannot get user info for {username}")
            return None

        data = res.get("response", res)
        user = data.get("user", {})
        short_uuid = user.get("shortUuid")

        if not short_uuid:
            logging.warning(f"create_subscription: no shortUuid for {username}")
            return None

        patch_payload = {"expireAt": self._expire_date(plan_id)}
        patch_res, patch_status = await self._request(
            "PATCH", f"{self.url}/api/users/{short_uuid}", patch_payload
        )
        if patch_status in (200, 201, 204):
            logging.info(f"Subscription updated for {username} via PATCH")
        else:
            logging.warning(f"PATCH expireAt failed ({patch_status}): {patch_res}")
        return patch_res

    async def get_config(self, username: str) -> str | None:
        """Возвращает subscriptionUrl из /api/subscriptions/by-username/{username}."""
        res, status = await self._request(
            "GET", f"{self.url}/api/subscriptions/by-username/{username}"
        )
        if status != 200 or not isinstance(res, dict):
            logging.error(f"get_config: bad response {status} for {username}")
            return None

        data = res.get("response", res)
        sub_url = data.get("subscriptionUrl")
        if sub_url:
            logging.info(f"get_config: subscriptionUrl = {sub_url}")
            return sub_url

        logging.error(f"Could not get config for {username}: no subscriptionUrl")
        return None

    async def get_user_info(self, username: str) -> dict | None:
        """Информация о юзере через /api/subscriptions/by-username."""
        res, status = await self._request(
            "GET", f"{self.url}/api/subscriptions/by-username/{username}"
        )
        if status != 200 or not isinstance(res, dict):
            return None

        data = res.get("response", res)
        user = data.get("user", {})
        sub_url = data.get("subscriptionUrl")

        expire_raw = user.get("expiresAt", "")
        try:
            expire_dt = datetime.fromisoformat(expire_raw.replace("Z", "+00:00"))
            expiry_date = expire_dt.strftime("%d.%m.%Y")
        except Exception:
            expiry_date = expire_raw or "Не ограничено"

        return {
            "plan": "Активна" if user.get("isActive") else "Неактивна",
            "expiry_date": expiry_date,
            "config_link": sub_url,
            "days_left": user.get("daysLeft", "?"),
            "is_active": user.get("isActive", False),
        }

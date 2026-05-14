# v1.0.0

Первый рабочий релиз SLAB — Telegram VPN бот на базе Remnawave.

## Исправления
- `create_user` теперь передаёт `expireAt` (обязательное поле API)
- `squadUuid` вместо `squadName` — внутренний сквад теперь выдаётся
- `get_config` через `/api/subscriptions/by-username` вместо `/api/users/{uuid}`
- `create_subscription` через `PATCH /api/users/{shortUuid}`
- Авто-обновление `expireAt` если юзер уже существует

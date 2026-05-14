# SLAB — Telegram VPN Bot

Telegram-бот для продажи VPN-подписок через панель [Remnawave](https://remnawave.dev).

## Стек
- Python 3.11+
- aiogram 3.x
- aiohttp
- aiosqlite
- Remnawave API

## Быстрый старт

```bash
pip install -r requirements.txt
cp .env.example .env
# Заполни .env своими данными
python bot.py
```

## Переменные окружения

| Переменная | Описание |
|---|---|
| `BOT_TOKEN` | Токен бота от @BotFather |
| `ADMIN_GROUP_ID` | ID группы для уведомлений |
| `CARD_NUMBER` | Реквизиты для оплаты |
| `REMNAWAVE_API_URL` | URL панели Remnawave |
| `REMNAWAVE_API_KEY` | API ключ из панели |

## Важно
- В `keyboards.py` замени UUID-заглушки в `PLAN_MAP` на реальные UUID планов из панели Remnawave (Settings → Plans)
- Настрой хосты в Remnawave (вкладка Hosts) для сквада `Main_sab` — иначе ссылки будут пустыми

## Исправления remnawave.py
- `create_user` теперь передаёт `expireAt` (обязательное поле)
- `get_config` использует `/api/subscriptions/by-username/{username}` вместо `/api/users/{uuid}`
- `create_subscription` обновляет дату через `PATCH /api/users/{shortUuid}`

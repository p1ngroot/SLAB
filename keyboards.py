from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# Маппинг ваших тарифов на реальные UUID планов из Remnawave
# Замените значения на реальные UUID из вашей панели (Settings → Plans)
PLAN_MAP = {
    "plan_2dev_1m":  "uuid-plan-2dev-1m",
    "plan_5dev_1m":  "uuid-plan-5dev-1m",
    "plan_3m":       "uuid-plan-3m",
    "plan_5dev_3m":  "uuid-plan-5dev-3m",
    "plan_6m":       "uuid-plan-6m",
    "plan_5dev_6m":  "uuid-plan-5dev-6m",
    "plan_12m":      "uuid-plan-12m",
    "plan_5dev_12m": "uuid-plan-5dev-12m",
}

def get_main_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💳 Купить VPN"), KeyboardButton(text="📦 Мои подписки")],
            [KeyboardButton(text="❓ Поддержка"), KeyboardButton(text="⚙️ Инструкция")]
        ],
        resize_keyboard=True
    )

def get_tariffs_kb():
    tariffs = [
        ("📱 2 устройства — 200₽ 100₽ / мес 🔥", "plan_2dev_1m"),
        ("👥 5 устройств — 500₽ 400₽ / мес 🔥", "plan_5dev_1m"),
        ("📅 3 месяца — 300₽ 250₽ 🔥", "plan_3m"),
        ("👥📅 5 устр + 3 мес — 700₽ 500₽ 🔥", "plan_5dev_3m"),
        ("📆 6 месяцев — 1000₽ 700₽ 🔥", "plan_6m"),
        ("👥📆 5 устр + 6 мес — 1600₽ 1200₽ 🔥", "plan_5dev_6m"),
        ("🗓 12 месяцев — 2000₽ 1300₽ 🔥", "plan_12m"),
        ("👥🗓 5 устр + 12 мес — 3500₽ 2500₽ 🔥", "plan_5dev_12m"),
    ]
    buttons = [[InlineKeyboardButton(text=t[0], callback_data=t[1])] for t in tariffs]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def admin_approve_kb(user_id: int, username: str, plan_id: str):
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Одобрить", callback_data=f"apprv:{user_id}:{username}:{plan_id}"),
        InlineKeyboardButton(text="❌ Отклонить", callback_data=f"rej:{user_id}")
    ]])

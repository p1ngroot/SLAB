import asyncio
import logging
import re
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import keyboards as kb
import db
from remnawave import RemnawaveClient

__version__ = "1.1.0"

# --- ИНИЦИАЛИЗАЦИЯ ---
load_dotenv()
logging.basicConfig(level=logging.INFO)

TOKEN = getenv("BOT_TOKEN")
ADMIN_GROUP = int(getenv("ADMIN_GROUP_ID", "-5170265363"))
CARD_DETAILS = getenv("CARD_NUMBER", "0000 0000 0000 0000")
CHANNEL_LINK = "https://t.me/SEVEN_LAB_PROXY"
FOOTER = f"\n\n📢 Наш [ТГ канал]({CHANNEL_LINK})"

bot = Bot(token=TOKEN)
dp = Dispatcher()
remna = RemnawaveClient()

# --- СОСТОЯНИЯ FSM ---
class OrderStates(StatesGroup):
    waiting_for_proof = State()

class SupportStates(StatesGroup):
    waiting_for_question = State()

# --- БАЗОВЫЕ КОМАНДЫ ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 Добро пожаловать в **SEVEN-LAB PROXY**!\nЛучший VPN на базе протоколов VLESS/Xray.",
        reply_markup=kb.get_main_kb(),
        parse_mode="Markdown"
    )

# --- ПРОФИЛЬ (МОИ ПОДПИСКИ) ---
@dp.message(F.text == "📦 Мои подписки")
async def show_profile(message: types.Message):
    username = (message.from_user.username or f"id{message.from_user.id}").replace("@", "")
    await message.answer("🔄 Загружаю данные из системы...")
    try:
        user_info = await remna.get_user_info(username)
        if user_info and user_info.get("is_active"):
            text = (
                f"👤 **Ваш профиль**\n━━━━━━━━━━━━━━━\n"
                f"🔑 Профиль: `{username}`\n"
                f"📦 Статус: {user_info['plan']}\n"
                f"📅 Истекает: {user_info['expiry_date']} (осталось {user_info['days_left']} дн.)\n"
                f"━━━━━━━━━━━━━━━\n"
                f"🔗 Ссылка на подписку:\n`{user_info['config_link'] or 'Не найдена'}`"
            )
        else:
            text = "❌ У вас пока нет активных подписок. Купите VPN, чтобы начать пользоваться."
    except Exception as e:
        logging.error(f"Error fetching profile: {e}")
        text = "⚙️ Ошибка получения данных. Попробуйте позже или напишите в поддержку."
    await message.answer(text + FOOTER, parse_mode="Markdown", disable_web_page_preview=True)

# --- ИНСТРУКЦИЯ ---
@dp.message(F.text == "⚙️ Инструкция")
async def show_instruction(message: types.Message):
    inst_text = (
        "🚀 **Как подключить VPN:**\n\n"
        "1️⃣ **iOS/Android:** Скачайте приложение v2rayNG или FoXray.\n"
        "2️⃣ **Windows/Mac:** Скачайте v2rayN или Nekoray.\n"
        "3️⃣ **Настройка:** Скопируйте ссылку-конфиг из профиля и импортируйте её в приложение через '+' (Import from Clipboard).\n"
        "4️⃣ **Готово!** Нажмите кнопку 'Подключиться'."
    )
    await message.answer(inst_text + FOOTER, parse_mode="Markdown")

# --- ПОДДЕРЖКА ---
@dp.message(F.text == "❓ Поддержка")
async def support_init(message: types.Message, state: FSMContext):
    await message.answer("📝 Напишите ваш вопрос, и наш агент ответит вам прямо здесь:")
    await state.set_state(SupportStates.waiting_for_question)

@dp.message(SupportStates.waiting_for_question)
async def forward_to_admin(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username or "NoUsername"
    await bot.send_message(
        ADMIN_GROUP,
        f"🆘 **НОВЫЙ ВОПРОС**\n"
        f"👤 От: @{username} (ID: `{user_id}`)\n"
        f"📝 Текст: {message.text}\n\n"
        f"───────────────────────\n"
        f"Чтобы ответить, нажмите Reply и начните с 'Ответ:'",
    )
    await message.answer("✅ Ваш вопрос отправлен! Ожидайте ответа." + FOOTER, parse_mode="Markdown")
    await state.clear()

@dp.message(F.chat.id == ADMIN_GROUP, F.text.startswith("Ответ:"))
async def admin_reply_fix(message: types.Message):
    if not message.reply_to_message:
        return await message.answer("❌ Нужно ответить (Reply) на сообщение с вопросом!")
    match = re.search(r"ID: `(\d+)`", message.reply_to_message.text)
    if match:
        user_id = int(match.group(1))
        answer_text = message.text.replace("Ответ:", "").strip()
        try:
            await bot.send_message(
                user_id,
                f"✉️ **Ответ от поддержки:**\n\n{answer_text}" + FOOTER,
                parse_mode="Markdown"
            )
            await message.answer("✅ Ответ отправлен пользователю.")
        except Exception as e:
            await message.answer(f"❌ Не удалось отправить (бот заблокирован?): {e}")
    else:
        await message.answer("❌ Не удалось найти ID пользователя в тексте сообщения.")

# --- ПРОДАЖА VPN ---
@dp.message(F.text == "💳 Купить VPN")
async def buy_vpn(message: types.Message):
    await message.answer(
        "💎 **ДОСТУПНЫЕ ТАРИФЫ**\nВысокая скорость и обход блокировок\n━━━━━━━━━━━━━━━",
        reply_markup=kb.get_tariffs_kb(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data.startswith("plan_"))
async def select_plan(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(selected_plan=callback.data)
    await callback.message.answer(
        f"💳 **Оплата переводом на карту**\n\n"
        f"Реквизиты: `{CARD_DETAILS}`\n\n"
        "После оплаты отправьте чек (скриншот) ответным сообщением:",
        parse_mode="Markdown"
    )
    await state.set_state(OrderStates.waiting_for_proof)

@dp.message(OrderStates.waiting_for_proof, F.photo)
async def process_payment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = (message.from_user.username or f"id{message.from_user.id}").replace("@", "")
    await db.add_transaction(message.from_user.id, username, data['selected_plan'], message.photo[-1].file_id)
    await bot.send_photo(
        chat_id=ADMIN_GROUP,
        photo=message.photo[-1].file_id,
        caption=(
            f"💰 **Новая оплата VPN**\n\n"
            f"👤 Пользователь: @{username} (ID: `{message.from_user.id}`)\n"
            f"📦 Тариф: {data['selected_plan']}\n"
        ),
        reply_markup=kb.admin_approve_kb(message.from_user.id, username, data['selected_plan'])
    )
    await message.answer("⏳ Чек отправлен! Ожидайте уведомления об активации.")
    await state.clear()

# --- ЛОГИКА ОДОБРЕНИЯ ---
@dp.callback_query(F.data.startswith("apprv:"))
async def approve_vpn(callback: types.CallbackQuery):
    _, user_id, username, plan = callback.data.split(":")
    try:
        # create_user сам обработает случай 409 (уже существует) и обновит expireAt
        await remna.create_user(username, plan)

        # Получаем ссылку с retry — API может чуть задержать
        config_link = None
        for _ in range(3):
            await asyncio.sleep(2)
            config_link = await remna.get_config(username)
            if config_link:
                break

        await db.update_payment_status(int(user_id), "approved")

        text = (
            f"✅ **Оплата подтверждена!**\n\n"
            f"👤 Профиль: `{username}`\n"
            f"🔗 Ссылка на подписку:\n`{config_link or 'Генерируется... Проверьте в Профиле'}`"
            + FOOTER
        )
        await bot.send_message(int(user_id), text, parse_mode="Markdown", disable_web_page_preview=True)
        await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n✅ ОДОБРЕНО")
    except Exception as e:
        logging.error(f"Approve Error: {e}")
        await callback.answer(f"Ошибка API: {str(e)}", show_alert=True)

@dp.callback_query(F.data.startswith("rej:"))
async def reject_vpn(callback: types.CallbackQuery):
    user_id = callback.data.split(":")[1]
    try:
        await db.update_payment_status(int(user_id), "rejected")
        await bot.send_message(int(user_id), "❌ Оплата не подтверждена. Обратитесь в поддержку.")
        await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n❌ ОТКЛОНЕНО")
    except Exception as e:
        logging.error(f"Reject Error: {e}")
        await callback.answer(f"Ошибка: {str(e)}", show_alert=True)

# --- ЗАПУСК ---
async def main():
    await db.init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

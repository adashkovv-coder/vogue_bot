from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_IDS
from database import Database
from keyboards import admin_panel, status_list_keyboard, status_change_keyboard

router = Router()
db = Database()

# Состояния для ввода трек-номера
class TrackState(StatesGroup):
    waiting_for_tracking = State()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# Главная команда админа
@router.message(Command("admin"))
async def admin_cmd(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа.")
        return
    await message.answer("👑 Панель администратора:", reply_markup=admin_panel())

# Список заказов (выбор заказа)
@router.callback_query(F.data == "admin_orders")
async def admin_orders(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    orders = db.get_all_orders()
    if not orders:
        await callback.message.edit_text("📭 Нет заказов.")
        return
    await callback.message.edit_text(
        "Выберите заказ:",
        reply_markup=status_list_keyboard(orders)
    )
    await callback.answer()

# Детали выбранного заказа и кнопки изменения статуса
@router.callback_query(F.data.startswith("order_"))
async def order_detail(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    order_id = int(callback.data.split("_")[1])
    order = db.get_order(order_id)
    if not order:
        await callback.answer("Заказ не найден")
        return
    # order: (id, user_id, username, type, deadline, execution_option, extras, photos, texts, status, tracking, created_at)
    text = (
        f"📄 **Заказ #{order[0]}**\n"
        f"👤 Клиент: @{order[2]}\n"
        f"📖 Тип: {order[3]}\n"
        f"📅 Срок: {order[4]}\n"
        f"⚙️ Вариант: {order[5]}\n"
        f"✨ Допы: {order[6]}\n"
        f"📸 Фото: {len(order[7].split(',')) if order[7] else 0} шт.\n"
        f"📝 Текст: {order[8][:100] if order[8] else 'нет'}...\n"
        f"🏷️ Статус: {order[9]}\n"
        f"📦 Трек: {order[10] if order[10] else 'нет'}"
    )
    await callback.message.edit_text(
        text,
        parse_mode="Markdown",
        reply_markup=status_change_keyboard(order_id, order[9])
    )
    await callback.answer()

# Изменение статуса
@router.callback_query(F.data.startswith("set_status_"))
async def set_status(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    parts = callback.data.split("_", 2)
    if len(parts) != 3:
        await callback.answer("Ошибка формата данных")
        return
    _, order_id_str, new_status = parts
    order_id = int(order_id_str)

    db.update_status(order_id, new_status)

    # Уведомить клиента
    order = db.get_order(order_id)
    if order:
        user_id = order[1]
        try:
            await callback.bot.send_message(
                user_id,
                f"🔄 Статус вашего заказа #{order_id} изменился на: **{new_status.upper()}**",
                parse_mode="Markdown"
            )
        except Exception:
            pass  # клиент не начинал диалог

    await callback.answer(f"✅ Статус заказа #{order_id} обновлён на {new_status}")

    # Показать обновлённые детали заказа
    await order_detail(callback)

# Запрос трек-номера (список заказов)
@router.callback_query(F.data == "admin_add_tracking")
async def ask_tracking(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    orders = db.get_all_orders()
    if not orders:
        await callback.message.edit_text("Нет заказов.")
        return
    await state.set_state(TrackState.waiting_for_tracking)
    await callback.message.edit_text(
        "Выберите заказ, для которого добавить трек-номер:",
        reply_markup=status_list_keyboard(orders)
    )
    await callback.answer()

# Выбор заказа для трек-номера
@router.callback_query(TrackState.waiting_for_tracking, F.data.startswith("order_"))
async def select_order_for_tracking(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    order_id = int(callback.data.split("_")[1])
    await state.update_data(track_order_id=order_id)
    await callback.message.edit_text(
        f"Введите трек-номер для заказа #{order_id}:"
    )
    await callback.answer()

# Получение текста трек-номера
@router.message(TrackState.waiting_for_tracking)
async def receive_tracking(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    data = await state.get_data()
    order_id = data.get("track_order_id")
    if not order_id:
        await message.answer("Ошибка: не выбран заказ. Начните заново через /admin")
        await state.clear()
        return
    tracking = message.text.strip()
    db.update_tracking(order_id, tracking)

    # Уведомить клиента
    order = db.get_order(order_id)
    if order:
        user_id = order[1]
        try:
            await message.bot.send_message(
                user_id,
                f"📦 К вашему заказу #{order_id} добавлен трек-номер: `{tracking}`",
                parse_mode="Markdown"
            )
        except Exception:
            pass

    await message.answer(f"✅ Трек-номер для заказа #{order_id} добавлен: {tracking}")
    await state.clear()

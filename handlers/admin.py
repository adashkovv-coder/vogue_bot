from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from config import ADMIN_IDS
from database import Database
from keyboards import admin_panel, status_list_keyboard, status_change_keyboard

router = Router()
db = Database()

def is_admin(user_id):
    return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def admin_cmd(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Панель администратора:", reply_markup=admin_panel())

@router.callback_query(F.data == "admin_orders")
async def admin_orders(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    orders = db.get_all_orders()
    if not orders:
        await callback.message.edit_text("Нет заказов.")
        return
    await callback.message.edit_text("Выберите заказ:", reply_markup=status_list_keyboard(orders))
    await callback.answer()

@router.callback_query(F.data.startswith("order_"))
async def order_detail(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[1])
    order = db.get_order(order_id)
    if not order:
        await callback.answer("Заказ не найден")
        return
    text = (
        f"📄 Заказ #{order[0]}\n"
        f"Клиент: @{order[2]}\n"
        f"Тип: {order[3]}\n"
        f"Срок: {order[4]}\n"
        f"Вариант: {order[5]}\n"
        f"Допы: {order[6]}\n"
        f"Статус: {order[8]}\n"
        f"Трек: {order[9] if order[9] else 'нет'}"
    )
    await callback.message.edit_text(text, reply_markup=status_change_keyboard(order_id, order[8]))
    await callback.answer()

@router.callback_query(F.data.startswith("set_status_"))
async def set_status(callback: CallbackQuery):
    _, order_id_str, new_status = callback.data.split("_")
    order_id = int(order_id_str)
    db.update_status(order_id, new_status)
    # уведомить клиента
    order = db.get_order(order_id)
    if order:
        user_id = order[1]
        await callback.bot.send_message(user_id, f"🔄 Статус вашего заказа #{order_id} изменился на: {new_status.upper()}")
    await callback.answer(f"Статус заказа #{order_id} обновлён на {new_status}")
    await admin_orders(callback)

@router.callback_query(F.data == "admin_add_tracking")
async def ask_tracking(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        return
    orders = db.get_all_orders()
    await callback.message.edit_text("Выберите заказ для добавления трек-номера:", reply_markup=status_list_keyboard(orders))
    await callback.answer()

@router.callback_query(F.data.startswith("order_"))
async def add_tracking_prompt(callback: CallbackQuery):
    # перехватываем второй раз — для ввода трека
    if callback.data.startswith("order_"):
        order_id = int(callback.data.split("_")[1])
        await callback.message.answer(f"Введите трек-номер для заказа #{order_id}:")
        # сохраним временно order_id в словаре или используем FSM
        from aiogram.fsm.context import FSMContext
        from aiogram.fsm.state import State, StatesGroup
        class TrackState(StatesGroup):
            waiting = State()
        await callback.message.bot.set_state(callback.from_user.id, TrackState.waiting, callback.message.chat.id)
        async with callback.message.bot._state_storage.storage as storage:
            await storage.set_data(chat_id=callback.message.chat.id, user_id=callback.from_user.id, data={"order_id": order_id})
        await callback.answer()
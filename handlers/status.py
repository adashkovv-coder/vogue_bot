from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards import main_menu
from database import Database

router = Router()
db = Database()

# Словарь для преобразования статусов
status_rus = {
    'new': 'новый',
    'design': 'дизайн',
    'print': 'печать',
    'delivery': 'доставка',
    'completed': 'выполнен'
}

@router.callback_query(F.data == "my_orders")
async def my_orders(callback: CallbackQuery):
    user_id = callback.from_user.id
    orders = db.get_user_orders(user_id)
    if not orders:
        await callback.message.answer("📭 У вас пока нет заказов.", reply_markup=main_menu())
        await callback.answer()
        return

    text = "🦢 Ваши заказы:\n\n"
    for idx, order in enumerate(orders, start=1):
        # order: (id, user_id, username, type, deadline, execution_option, extras, photos, texts, status, tracking, created_at)
        order_id = order[0]
        order_type = order[3]
        deadline = order[4]
        exec_option = order[5]
        extras = order[6]
        status = order[9]
        # Преобразуем статус в русский
        status_ru = status_rus.get(status, status)
        # Формируем строку
        text += f"Заказ {idx}:\n"
        text += f"        {order_type}, до {deadline}, {exec_option}, дополнительно: {extras}\n"
        text += f"         Статус заказа: {status_ru}\n\n"

    await callback.message.answer(text, parse_mode="HTML", reply_markup=main_menu())
    await callback.answer()

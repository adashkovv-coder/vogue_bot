from aiogram import Router, F
from aiogram.types import CallbackQuery
from keyboards import main_menu
from database import Database

router = Router()
db = Database()

@router.callback_query(F.data == "my_orders")
async def my_orders(callback: CallbackQuery):
    user_id = callback.from_user.id
    orders = db.get_user_orders(user_id)
    if not orders:
        await callback.message.edit_text("У вас пока нет заказов.", reply_markup=main_menu())
        await callback.answer()
        return
    text = "📦 Ваши заказы:\n\n"
    for order in orders:
        text += f"#{order[0]} — статус: {order[8]}\n"
        if order[9]:
            text += f"   Трек-номер: {order[9]}\n"
    await callback.message.edit_text(text, reply_markup=main_menu())
    await callback.answer()
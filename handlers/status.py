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
        # Отправляем новое сообщение, а не редактируем старое
        await callback.message.answer("📭 У вас пока нет заказов.", reply_markup=main_menu())
        await callback.answer()
        return
    text = "📦 **Ваши заказы:**\n\n"
    for order in orders:
        # order: id, user_id, username, type, deadline, execution_option, extras, status, tracking
        text += (
            f"*{order[0]}* — статус: {order[8]}\n"
            f"  📖 {order[3]} | ⏰ {order[4]}\n"
            f"  🛠️ {order[5]} | ✨ {order[6]}\n"
        )
        if order[9]:
            text += f"  📦 Трек: {order[9]}\n"
        text += "\n"
    await callback.message.answer(text, parse_mode="Markdown", reply_markup=main_menu())
    await callback.answer()

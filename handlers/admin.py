from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from config import ADMIN_IDS
from database import Database
from keyboards import admin_panel, status_list_keyboard, status_change_keyboard

router = Router()          # <-- ЭТО БЫЛО ПРОПУЩЕНО
db = Database()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def admin_cmd(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ У вас нет доступа.")
        return
    await message.answer("👑 Панель администратора:", reply_markup=admin_panel())

@router.callback_query(F.data == "admin_orders")
async def admin_orders(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Нет доступа", show_alert=True)
        return
    orders = db.get_all_orders()
    if not orders:
        await callback.message.edit_text("📭 Нет заказов.")
        return

    text = "📋 **Список заказов:**\n\n"
    for order in orders:
        # order: id, user_id, username, type, deadline, execution_option, extras, photos, texts, status, tracking
        text += (
            f"*{order[0]}* | @{order[2]}\n"
            f"  📖 {order[3]} | ⏰ {order[4]}\n"
            f"  🛠️ {order[5]} | ✨ {order[6]}\n"
            f"  🏷️ Статус: {order[9]}\n\n"
        )
    await callback.message.edit_text(text, parse_mode="Markdown")
    await callback.answer()

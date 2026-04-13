from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📖 Сделать заказ", callback_data="new_order")],
        [InlineKeyboardButton(text="Портфолио", callback_data="portfolio")],
        [InlineKeyboardButton(text="Прайс", callback_data="price")],
        [InlineKeyboardButton(text="Статус заказа", callback_data="my_orders")]
    ])

def order_type_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="На день рождения 🍰", callback_data="type_birthday")],
        [InlineKeyboardButton(text="Love story для важной даты 💌", callback_data="type_wedding")],
        [InlineKeyboardButton(text="Просто для себя 🙏🏻", callback_data="type_business")],
        [InlineKeyboardButton(text="Другое", callback_data="type_other")]
    ])

def execution_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Только дизайн (печатаю сам)", callback_data="exec_print_only")],
        [InlineKeyboardButton(text="Полный цикл (дизайн+печать+доставка)", callback_data="exec_full")]
    ])

def extras_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="постер А3 - 350₽", callback_data="extras_poster")],
        [InlineKeyboardButton(text="постер А4 - 250₽", callback_data="extras_magnet")],
        [InlineKeyboardButton(text="оба 500₽", callback_data="extras_both")],
        [InlineKeyboardButton(text="нет, спасибо", callback_data="extras_none")]
    ])

def confirm_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Подтвердить заказ", callback_data="confirm_order")],
        [InlineKeyboardButton(text="Изменить", callback_data="edit_order")]
    ])

def admin_panel():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Список заказов", callback_data="admin_orders")],
        [InlineKeyboardButton(text="Изменить статус", callback_data="admin_change_status")],
        [InlineKeyboardButton(text="Добавить трек-номер", callback_data="admin_add_tracking")]
    ])

def status_list_keyboard(orders):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for order in orders:
        kb.inline_keyboard.append([InlineKeyboardButton(text=f"Заказ #{order[0]}", callback_data=f"order_{order[0]}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")])
    return kb

def status_change_keyboard(order_id, current_status):
    statuses = ["new", "design", "print", "delivery", "completed"]
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for s in statuses:
        if s != current_status:
            kb.inline_keyboard.append([InlineKeyboardButton(text=s.upper(), callback_data=f"set_status_{order_id}_{s}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="admin_orders")])
    return kb

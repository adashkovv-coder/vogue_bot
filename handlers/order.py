from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from states import OrderStates
from keyboards import order_type_keyboard, execution_keyboard, extras_keyboard, confirm_keyboard
from database import Database
from config import ADMIN_IDS, GIRL_TELEGRAM

router = Router()
db = Database()

@router.callback_query(F.data == "new_order")
async def new_order(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.choosing_type)
    await callback.message.edit_text(
        "🎉 Какой журнал вам нужен? Выберите тип:",
        reply_markup=order_type_keyboard()
    )
    await callback.answer()

@router.callback_query(StateFilter(OrderStates.choosing_type), F.data.startswith("type_"))
async def choose_type(callback: CallbackQuery, state: FSMContext):
    type_map = {
        "type_birthday": "На день рождения",
        "type_lovestory": "Love story (для важной даты влюбленным)",
        "type_myself": "Просто для себя",
        "type_other": "Другое"
    }
    selected = type_map.get(callback.data)
    await state.update_data(order_type=selected)
    await state.set_state(OrderStates.entering_deadline)
    await callback.message.edit_text(
        "📅 Напишите желаемую дату готовности (например, 30.05.2026):"
    )
    await callback.answer()

@router.message(StateFilter(OrderStates.entering_deadline))
async def enter_deadline(message: Message, state: FSMContext):
    await state.update_data(deadline=message.text)
    await state.set_state(OrderStates.choosing_execution)
    await message.answer(
        "Какой вариант вам удобнее?",
        reply_markup=execution_keyboard()
    )

@router.callback_query(StateFilter(OrderStates.choosing_execution), F.data.startswith("exec_"))
async def choose_execution(callback: CallbackQuery, state: FSMContext):
    exec_map = {
        "exec_print_only": "Только дизайн",
        "exec_full": "Полный цикл (дизайн+печать+доставка)"
    }
    selected = exec_map.get(callback.data)
    await state.update_data(execution_option=selected)
    await state.set_state(OrderStates.choosing_extras)
    await callback.message.edit_text(
        "✨ Хотите добавить дополнительные товары со скидкой?",
        reply_markup=extras_keyboard()
    )
    await callback.answer()

@router.callback_query(StateFilter(OrderStates.choosing_extras), F.data.startswith("extras_"))
async def choose_extras(callback: CallbackQuery, state: FSMContext):
    extras_map = {
        "extras_poster": "Постер А3 - 350 руб",
        "extras_magnet": "Постер А4 - 250 руб",
        "extras_both": "Оба - 500 руб",
        "extras_none": "Нет"
    }
    selected = extras_map.get(callback.data)
    await state.update_data(extras=selected)

    data = await state.get_data()
    summary = (
        f"📋 Проверьте ваш заказ:\n"
        f"Тип: {data['order_type']}\n"
        f"Срок: {data['deadline']}\n"
        f"Вариант: {data['execution_option']}\n"
        f"Доп. товары: {data['extras']}\n\n"
        f"Всё верно?"
    )
    await state.set_state(OrderStates.confirming)
    await callback.message.edit_text(summary, reply_markup=confirm_keyboard())
    await callback.answer()

@router.callback_query(StateFilter(OrderStates.confirming), F.data == "confirm_order")
async def confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id
    username = callback.from_user.username or callback.from_user.full_name

    # Сохраняем заказ в БД (фото и текст – пустые строки)
    order_id = db.add_order(
        user_id=user_id,
        username=username,
        order_type=data['order_type'],
        deadline=data['deadline'],
        execution_option=data['execution_option'],
        extras=data['extras'],
        photos="",
        texts=""
    )

    # Уведомление админу
    for admin_id in ADMIN_IDS:
        try:
            await callback.bot.send_message(
                admin_id,
                f"🆕 Новый заказ #{order_id}\n"
                f"От: @{username}\n"
                f"Тип: {data['order_type']}\n"
                f"Срок: {data['deadline']}\n"
                f"Вариант: {data['execution_option']}\n"
                f"Допы: {data['extras']}"
            )
        except Exception:
            pass

    # Отправляем клиенту сообщение с контактом девушки
    await callback.message.edit_text(
        f"Ваш заказ принят!\n\n"
        f"Теперь, пожалуйста, напишите мне лично {GIRL_TELEGRAM}\n"
        f"Спасибо за заказ! 💐"
    )
    await state.clear()
    await callback.answer()

@router.callback_query(StateFilter(OrderStates.confirming), F.data == "edit_order")
async def edit(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.choosing_type)
    await callback.message.edit_text("Давайте начнём заново. Выберите тип журнала:", reply_markup=order_type_keyboard())
    await callback.answer()

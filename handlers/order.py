from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from states import OrderStates
from keyboards import order_type_keyboard, execution_keyboard, extras_keyboard, confirm_keyboard
from database import Database
from config import ADMIN_IDS

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
        "extras_magnet": "Постер А4  - 250 руб",
        "extras_both": "Оба - 500 руб",
        "extras_none": "Нет"
    }
    selected = extras_map.get(callback.data)
    await state.update_data(extras=selected)
    await state.set_state(OrderStates.uploading_photos)
    await callback.message.edit_text(
        "📸 Загрузите фотографии для журнала.\n"
        "Можно отправить несколько сообщений (каждое фото отдельно).\n"
        "Когда закончите, напишите /done_photos"
    )
    await callback.answer()

# Временно храним фотографии
user_photos = {}

@router.message(StateFilter(OrderStates.uploading_photos), F.photo)
async def handle_photos(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id not in user_photos:
        user_photos[user_id] = []
    file_id = message.photo[-1].file_id
    user_photos[user_id].append(file_id)
    await message.answer(f"✅ Фото {len(user_photos[user_id])} добавлено. Отправляйте ещё или /done_photos")

@router.message(StateFilter(OrderStates.uploading_photos), F.text == "/done_photos")
async def done_photos(message: Message, state: FSMContext):
    user_id = message.from_user.id
    photos = user_photos.get(user_id, [])
    await state.update_data(photos=",".join(photos))
    # очищаем временное хранилище
    if user_id in user_photos:
        del user_photos[user_id]
    await state.set_state(OrderStates.entering_texts)
    await message.answer(
        "📝 Пришлите тексты для журнала (пожелания, поздравления, описания).\n"
        "Можно отправить одним сообщением."
    )

@router.message(StateFilter(OrderStates.entering_texts))
async def enter_texts(message: Message, state: FSMContext):
    await state.update_data(texts=message.text)
    data = await state.get_data()
    # Показываем сводку
    summary = (
        f"📋 Проверьте ваш заказ:\n"
        f"Тип: {data['order_type']}\n"
        f"Срок: {data['deadline']}\n"
        f"Вариант: {data['execution_option']}\n"
        f"Доп. товары: {data['extras']}\n"
        f"Фото: {len(data['photos'].split(',')) if data['photos'] else 0} шт.\n"
        f"Текст: {data['texts'][:100]}...\n\n"
        f"Всё верно?"
    )
    await state.set_state(OrderStates.confirming)
    await message.answer(summary, reply_markup=confirm_keyboard())

@router.callback_query(StateFilter(OrderStates.confirming), F.data == "confirm_order")
async def confirm(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id
    username = callback.from_user.username or callback.from_user.full_name
    order_id = db.add_order(
        user_id=user_id,
        username=username,
        order_type=data['order_type'],
        deadline=data['deadline'],
        execution_option=data['execution_option'],
        extras=data['extras'],
        photos=data['photos'],
        texts=data['texts']
    )
    await callback.message.edit_text(
        f"✅ Ваш заказ №{order_id} принят!\n"
        f"Мы свяжемся с вами в ближайшее время.\n"
        f"Статус заказа можно отследить в меню «Статус заказа»."
    )
    await state.clear()

    # Уведомление админу
    for admin_id in ADMIN_IDS:
        await callback.bot.send_message(
            admin_id,
            f"🆕 Новый заказ #{order_id}\n"
            f"От: @{username}\n"
            f"Тип: {data['order_type']}\n"
            f"Срок: {data['deadline']}\n"
            f"Вариант: {data['execution_option']}\n"
            f"Допы: {data['extras']}"
        )
    await callback.answer()

@router.callback_query(StateFilter(OrderStates.confirming), F.data == "edit_order")
async def edit(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.choosing_type)
    await callback.message.edit_text("Давайте начнём заново. Выберите тип журнала:", reply_markup=order_type_keyboard())
    await callback.answer()

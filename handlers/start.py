from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from keyboards import main_menu

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "🦢 Приветик! я бот для заказа индивидуального журнала по душе.\n"
        "Мы создаем уникальные подарки так и важные воспоминания.\n\n"
        "• Портфолио вместе с прайсом можно посмотреть по ссылке в меню.\n\n"
        "Чтобы начать, нажми ”сделать заказ”",
        reply_markup=main_menu()
    )
    
@router.callback_query(F.data == "portfolio")
async def portfolio(callback: CallbackQuery):
    await callback.message.answer(
        "📷 Наше портфолио:\nhttps://www.instagram.com/ваш_аккаунт/\n\n"
        "Или примеры журналов: [ссылка на гугл-диск]"
    )
    await callback.answer()

@router.callback_query(F.data == "price")
async def price(callback: CallbackQuery):
    await callback.message.answer(
        "💰 Цены:\n"
        "📖 Журнал A4 (20 страниц) — 2500₽\n"
        "🖼️ Постер A3 — 500₽\n"
        "🧲 Магнит 10x15 — 200₽\n"
        "🚚 Доставка по России — 300₽\n\n"
        "Скидка 10% при заказе журнала+постера+магнита!"
    )
    await callback.answer()

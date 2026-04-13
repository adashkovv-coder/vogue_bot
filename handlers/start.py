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
        "🦢 Наше портфолио- https://t.me/nkssmaz\n\n"
    )
    await callback.answer()
    
@router.callback_query(F.data == "price")
async def price(callback: CallbackQuery):
    text = (
        "🦢 Прайс лист журналов\n\n"
        "12 листов - 700₽\n"
        "14 листов - 820₽\n"
        "16 листов - 940₽\n"
        "18 листов - 1060₽\n"
        "20 листов - 1180₽\n"
        "(далее +60₽ за лист)\n\n"
        "доставка по России -\n"
        "до 350₽\n"
        "(доставка возможна по ближним странам куда может доехать сдэк, доставка будет дороже в зависимости где вы находитесь)\n\n"
        "печать журнала -\n"
        "экстра печать (срок 1 день) - 1500₽\n"
        "обычная печать (срок до 5 дней) - 1200₽\n\n"
        "!цена печати указана за 12 листов, чем больше тем дороже, уточнять!\n\n"
        "дополнительно -\n\n"
        "постер А3 - 350₽\n"
        "постер А4 - 250₽"
    )
    await callback.message.answer(text)
    await callback.answer()

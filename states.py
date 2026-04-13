from aiogram.fsm.state import State, StatesGroup

class OrderStates(StatesGroup):
    choosing_type = State()
    entering_deadline = State()
    choosing_execution = State()
    choosing_extras = State()
    uploading_photos = State()
    entering_texts = State()
    confirming = State()
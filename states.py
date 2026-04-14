from aiogram.fsm.state import State, StatesGroup

class OrderStates(StatesGroup):
    choosing_type = State()
    entering_deadline = State()
    choosing_execution = State()
    choosing_extras = State()
    confirming = State()        # подтверждение заказа
    waiting_for_contact = State()  # новый этап: написать девушке

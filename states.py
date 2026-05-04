from aiogram.fsm.state import State, StatesGroup

class LessonStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_content = State()

class AdminStates(StatesGroup):
    waiting_for_password = State()
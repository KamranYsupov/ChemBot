from aiogram.fsm.state import State, StatesGroup


class MenuState(StatesGroup):
    union = State()
    fio = State()
    phone = State()
    email = State()
    end_reg = State()
    hand_over = State()
    feedback = State()
    get_comment = State()
    make_order = State()
    get_plombo = State()
    show_points = State()
    issued_order = State()
    get_point = State()
    search = State()

    def __str__(self):
        return self.state
    


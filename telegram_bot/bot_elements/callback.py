from aiogram.filters.callback_data import CallbackData


class MenuCallBack(CallbackData, prefix="menu"):
    to: str

class SubscribeCallBack(CallbackData, prefix="sub"):
    data: bool

class PointCallBack(CallbackData, prefix="poi"):
    type_: str
    data: int

class OrderCallBack(CallbackData, prefix="ord"):
    to: str

class HandOverCallBack(CallbackData, prefix="chs"):
    type_: str
    data: int

class BackCallBack(CallbackData, prefix="back"):
    to: str

class KeywordCallBack(CallbackData, prefix="kw"):
    suuid: str

class ContinueCallBack(CallbackData, prefix="cont"):
    s: int
    p: int
    mxs: int
    cw: int

class SliderCallBack(CallbackData, prefix="slide"):
    action: int
    last_index: int
    stype: str


if __name__ == "__main__":
    pack_meny = MenuCallBack(to="ddd").pack()
    print(pack_meny)
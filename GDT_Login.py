from gdo.core.GDT_String import GDT_String


class GDT_Login(GDT_String):

    def __init__(self, name: str):
        super().__init__(name)
        self.tooltip('tt_login')
        self.icon('account')

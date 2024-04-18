from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Password import Password, GDT_Password
from gdo.ui.GDT_Link import GDT_Link


class module_login(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 80

    def gdo_user_config(self) -> list[GDT]:
        return [
            GDT_Password('password'),
        ]

    def gdo_init_sidebar(self, page):
        page._left_bar.add_field(GDT_Link().href(self.href('form')))

    def set_password_for(self, user: GDO_User, password: str) -> None:
        user.save_setting('password', Password.hash(password))

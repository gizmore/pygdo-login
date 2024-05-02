from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Password import Password, GDT_Password
from gdo.core.GDT_UInt import GDT_UInt
from gdo.date.GDT_DateTime import GDT_DateTime
from gdo.date.GDT_Duration import GDT_Duration
from gdo.login.GDO_LoginAttempt import GDO_LoginAttempt
from gdo.net.GDT_IP import GDT_IP
from gdo.ui.GDT_Link import GDT_Link


class module_login(GDO_Module):

    def __init__(self):
        super().__init__()
        self._priority = 80

    def gdo_dependencies(self) -> list:
        return [
            'form',
        ]

    def gdo_classes(self):
        return [
            GDO_LoginAttempt,
        ]

    def gdo_module_config(self) -> list[GDT]:
        return [
            GDT_Duration('login_timeout').initial('5m'),
            GDT_UInt('login_attempts').initial('3').min(1),
        ]

    def cfg_failure_timeout(self) -> int:
        return self.get_config_value('login_timeout')

    def cfg_failure_attempts(self) -> int:
        return self.get_config_value('login_attempts')

    def gdo_user_config(self) -> list[GDT]:
        return [
            GDT_Password('password'),
            GDT_IP('last_login_ip'),
            GDT_DateTime('last_login_datetime'),
        ]

    def gdo_init_sidebar(self, page):
        page._right_bar.add_field(GDT_Link().href(self.href('form')).text('module_login'))

    def set_password_for(self, user: GDO_User, password: str) -> None:
        user.save_setting('password', Password.hash(password))

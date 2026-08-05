from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_User import GDT_User


class no_pass(Method):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'no_pass'

    def gdo_user_permission(self) -> str | None:
        return 'admin'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_User('user').not_null(),
        ]

    def gdo_execute(self) -> GDT:
        user = self.param_value('user')
        user.reset_setting('password')
        return self.reply('msg_password_removed', (user.render_name(),))

from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDO_User import GDO_User


class logout(Method):

    def gdo_trigger(self) -> str:
        return "logout"

    def gdo_connectors(self) -> str:
        return 'irc,web'

    def gdo_user_type(self) -> str | None:
        return 'member,guest'

    def gdo_has_permission(self, user: 'GDO_User'):
        if user._authenticated:
            return True
        return True

    def gdo_execute(self) -> GDT:
        self._env_user.logout(self._env_session)
        return self.msg('msg_logged_out')

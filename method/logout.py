from gdo.base.GDT import GDT
from gdo.base.Method import Method


class logout(Method):

    def gdo_trigger(self) -> str:
        return ""

    def gdo_user_type(self) -> str | None:
        return 'member,guest'

    def gdo_execute(self) -> GDT:
        self._env_user.logout(self._env_session)
        return self.reply('msg_logged_out')

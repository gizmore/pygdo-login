from gdo.base.Method import Method


class logout(Method):

    def gdo_user_type(self) -> str | None:
        return 'member,guest'

    def gdo_execute(self):
        self._env_user.logout(self._env_session)
        return self.reply('msg_logged_out')


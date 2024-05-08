from gdo.base.Method import Method


class logout(Method):

    def gdo_execute(self):
        self._env_user.logout(self._env_session)
        return self.reply('msg_logged_out')


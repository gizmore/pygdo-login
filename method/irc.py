from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Password import GDT_Password
from gdo.core.GDT_Secret import GDT_Secret
from gdo.core.GDT_UserType import GDT_UserType
from gdo.form.GDT_Form import GDT_Form
from gdo.form.GDT_Submit import GDT_Submit
from gdo.login.GDT_Login import GDT_Login
from gdo.login.method.form import form


class irc(form):

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'login'

    def gdo_connectors(self) -> str:
        return 'irc'

    def gdo_has_permission(self, user: 'GDO_User'):
        if user._authenticated:
            return False
        return True

    def gdo_user_type(self) -> str | None:
        return GDT_UserType.MEMBER

    def gdo_in_channels(self) -> bool:
        return False

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(GDT_Login('login').writable(False).hidden().initial(self._env_user.get_name()).not_null())
        form.add_field(GDT_Secret('password').not_null())
        form.add_field(GDT_Bool('bind_ip').not_null().initial('1'))
        form.actions().add_field(GDT_Submit().calling(self.form_submitted).default_button())

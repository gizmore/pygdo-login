from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Password import GDT_Password
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.login.GDT_Login import GDT_Login


class form(MethodForm):

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(GDT_Login('login').not_null())
        form.add_field(GDT_Password('password').not_null())
        form.add_field(GDT_Bool('bind_ip').not_null().initial('1'))
        super().gdo_create_form(form)

    def gdo_execute(self):
        return self.error('err_login_failed')
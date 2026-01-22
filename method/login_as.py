from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_User import GDT_User
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm


class login_as(MethodForm):

    @classmethod
    def gdo_trigger(cls) -> str:
        return "login.as"

    # def gdo_connectors(self) -> str:
    #     return 'web'

    def gdo_user_permission(self) -> str | None:
        return 'admin'

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(GDT_User('user'))
        super().gdo_create_form(form)

    def get_user(self) -> GDO_User:
        return self.param_value('user')

    def form_submitted(self):
        user = self.get_user()

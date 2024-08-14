from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.core.GDT_Password import GDT_Password
from gdo.form.GDT_Form import GDT_Form
from gdo.form.GDT_Validator import GDT_Validator
from gdo.form.MethodForm import MethodForm
from gdo.login import module_login


class change_password(MethodForm):

    def gdo_trigger(self) -> str:
        return ""

    def gdo_user_type(self) -> str | None:
        return 'guest,member'

    def gdo_in_channels(self) -> bool:
        return False

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(
            GDT_Password('old').label('old_password').not_null(),
            GDT_Validator().validator(form, 'old', self.validate_old_pass),
            GDT_Password('new').label('new_password').tooltip('tt_password').not_null(),
            GDT_Password('retype').not_null(),
            GDT_Validator().validator(form, 'retype', self.validate_pass_retype),
        )
        super().gdo_create_form(form)

    def validate_old_pass(self, form: GDT_Form, field: GDT, value: any) -> bool:
        user = self._env_user
        old_hash = user.get_setting_val('password')
        if not GDT_Password.check(old_hash, value):
            return field.error('err_wrong_password')
        return True

    def validate_pass_retype(self, form: GDT_Form, field: GDT, value: any) -> bool:
        if self.param_val('new') != self.param_val('retype'):
            return field.error('err_password_retype')
        return True

    def form_submitted(self):
        user = self._env_user
        mod = module_login.instance()
        old = self.param_val('old')
        new = self.param_val('new')
        mod.set_password_for(user, new)
        Application.EVENTS.publish('password_changed', user, old, new)  # GPG can hook here and re-encrypt the public key
        return self.msg('msg_password_changed')

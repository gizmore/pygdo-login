from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Trans import sitename, t
from gdo.base.Util import Strings, module_enabled
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Password import GDT_Password
from gdo.core.GDT_Secret import GDT_Secret
from gdo.core.GDT_UserType import GDT_UserType
from gdo.core.connector.Web import Web
from gdo.date.Time import Time
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.login import module_login
from gdo.login.GDO_LoginAttempt import GDO_LoginAttempt
from gdo.login.GDT_Login import GDT_Login
from gdo.mail.Mail import Mail
from gdo.net.GDT_IP import GDT_IP
from gdo.net.GDT_Url import GDT_Url
from gdo.ui.GDT_Link import GDT_Link


class form(MethodForm):
    _user: GDO_User

    @classmethod
    def gdo_trigger(cls) -> str:
        return ""

    def gdo_user_type(self) -> str | None:
        return GDT_UserType.GHOST

    def gdo_needs_authentication(self) -> bool:
        return False

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(GDT_Login('login').not_null())
        form.add_field(GDT_Secret('password').not_null())
        form.add_field(GDT_Bool('bind_ip').icon('url').tooltip('tt_bind_ip').not_null().initial('1'))
        form.add_field(GDT_Url('_back_to').internal().hidden())
        super().gdo_create_form(form)

    def form_submitted(self):
        return self.on_login(self.param_val('login'), self.param_val('password'), self.param_value('bind_ip'))

    def get_user(self, login: str) -> GDO_User | None:
        if hasattr(self, '_user'):
            return self._user
        if user := self._env_server.get_user_by_login(login):
            self._user = user
        return user

    def on_login(self, login: str, password: str, bind_ip: bool = False) -> GDT:
        if not self.ban_check():
            return self.get_form()
        user = self.get_user(login)
        if not user:
            return self.login_failed(user)
        hash_ = user.get_setting_val('password')
        if not hash_ or not GDT_Password.check(hash_, password):
            return self.login_failed(user)
        return self.login_success(user, bind_ip)

    def ban_check(self) -> bool:
        min_time, count = self.ban_data()
        if int(count) >= self.max_attempts():
            banned_for = float(min_time) - self.ban_cut()
            self.err('err_login_ban', (Time.human_duration(banned_for),))
            return False
        return True

    def ban_data(self) -> tuple:
        table = GDO_LoginAttempt.table()
        cut = Time.get_date(self.ban_cut())
        condition = f"la_ip={self.quote(GDT_IP.current())} AND la_created > {self.quote(cut)}"
        return table.select(f"UNIX_TIMESTAMP(MIN(la_created)), COUNT(*)").where(condition).exec(False).fetch_row()

    def ban_cut(self) -> float:
        return Application.TIME - self.ban_timeout()

    def ban_timeout(self) -> float:
        return module_login.instance().cfg_failure_timeout()

    def max_attempts(self) -> int:
        return self.gdo_module().cfg_failure_attempts()

    def login_failed(self, user: GDO_User) -> GDT:
        # ip = GDT_IP.current()
        userid = user.get_id() if user else None
        GDO_LoginAttempt.blank({
            # 'la_ip': ip,
            'la_user': userid,
        }).insert()
        if user:
            self.check_security_threat(user)
        min_time, attempts = self.ban_data()
        banned_for = float(min_time or 0) - self.ban_cut()
        attempts_left = self.max_attempts() - int(attempts)
        self.err('err_login_failed', (attempts_left, Time.human_duration(banned_for),))
        return self.get_form()

    def check_security_threat(self, user: GDO_User) -> None:
        table = GDO_LoginAttempt.table()
        cut = Time.get_date(self.ban_cut())
        condition = f"la_user={user.get_id()} AND la_created>'{cut}'"
        if table.count_where(condition) == 1:
            if module_enabled('mail'):
                self.mail_security_threat(user)

    def mail_security_threat(self, user: GDO_User) -> None:
        mail = Mail.from_bot()
        mail.subject(t('mails_login_threat'))
        ip = GDT_IP.current()
        args = (user.render_name(), sitename(), ip)
        mail.body(t('mailb_login_threat', args))
        mail.send_to_user(user)

    def get_last_login_data(self) -> tuple | None:
        ip = self._user.get_setting_val('last_login_ip')
        dt = self._user.get_setting_val('last_login_datetime')
        if ip and dt:
            return ip, dt
        return None, None

    def login_success(self, user: GDO_User, bind_ip: bool = False) -> GDT:
        self._user = user
        last_ip, last_date = self.get_last_login_data()
        if last_ip:
            self.msg('msg_authenticated_again', (user.render_name(), Time.display_date(last_date), last_ip))
        else:
            self.msg('msg_authenticated', (user.render_name(),))
        user.authenticate(self._env_session, bind_ip)
        back = self.param_val('_back_to')
        if back:
            link = GDT_Link().href(back).render()
            self.msg('msg_back_to', (link,))
        return self.empty()

from gdo.base.Application import Application
from gdo.base.GDT import GDT
from gdo.base.Util import Strings
from gdo.base.WithPermissionCheck import WithPermissionCheck
from gdo.core.GDO_User import GDO_User
from gdo.core.GDT_Bool import GDT_Bool
from gdo.core.GDT_Password import GDT_Password
from gdo.core.GDT_UserType import GDT_UserType
from gdo.core.connector.Web import Web
from gdo.date.Time import Time
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.login import module_login
from gdo.login.GDO_LoginAttempt import GDO_LoginAttempt
from gdo.login.GDT_Login import GDT_Login
from gdo.net.GDT_IP import GDT_IP
from gdo.net.GDT_Url import GDT_Url
from gdo.ui.GDT_Link import GDT_Link


class form(WithPermissionCheck, MethodForm):
    _user: GDO_User

    def gdo_user_type(self) -> str | None:
        return GDT_UserType.GHOST

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(GDT_Login('login').not_null())
        form.add_field(GDT_Password('password').not_null())
        form.add_field(GDT_Bool('bind_ip').not_null().initial('1'))
        form.add_field(GDT_Url('_back_to').internal().hidden())
        super().gdo_create_form(form)

    def form_submitted(self):
        return self.on_login(self.param_val('login'), self.param_val('password'), self.param_value('bind_ip'))

    def get_user(self, login: str) -> GDO_User | None:
        if hasattr(self, '_user'):
            return self._user
        server = Web.get_server()
        user = server.get_user_by_login(login)
        if user:
            self._user = user
        return user

    def on_login(self, login: str, password: str, bind_ip: bool = False) -> GDT:
        if not self.ban_check():
            return self.get_form()
        user = self.get_user(login)
        if not user:
            return self.login_failed(user)
        hash_ = user.get_setting_val('password')
        if not GDT_Password.check(hash_, password):
            return self.login_failed(user)
        return self.login_success(user, bind_ip)

    def ban_check(self) -> bool:
        min_time, count = self.ban_data()
        if int(count) >= self.max_attempts():
            banned_for = float(min_time) - self.ban_cut()
            self.err('err_login_ban', [Time.human_duration(banned_for)])
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
        return self.module().cfg_failure_attempts()

    def login_failed(self, user: GDO_User) -> GDT:
        ip = GDT_IP.current()
        userid = user.get_id() if user else None
        GDO_LoginAttempt.blank({
            'la_ip': ip,
            'la_user': userid,
        }).insert()
        if user:
            self.check_security_threat(user)
        min_time, attempts = self.ban_data()
        banned_for = float(min_time or 0) - self.ban_cut()
        attempts_left = self.max_attempts() - int(attempts)
        self.err('err_login_failed', [attempts_left, Time.human_duration(banned_for)])
        return self.get_form()

    def check_security_threat(self, user: GDO_User) -> None:
        # dbms = Module_DBMS.instance()
        table = GDO_LoginAttempt.table()
        # fromUnix = dbms.dbmsFromUnixtime(self.banCut())
        condition = f"la_user_id={user.get_id()} AND la_created > {fromUnix}"
        if table.countWhere(condition) == 1:
            if module_enabled('Mail'):
                self.mailSecurityThreat(user)

    def mailSecurityThreat(self, user: GDO_User) -> None:
        mail = Mail()
        mail.setSender(GDO_BOT_EMAIL)
        mail.setSubject(t('mail_subj_login_threat', [sitename()]))
        revealIP = Module_Login.instance().cfgFailureIPReveal()
        ip = GDT_IP.current() if revealIP else 'xx.xx.xx.xx'
        args = [user.renderName(), sitename(), ip]
        mail.setBody(t('mail_body_login_threat', args))
        mail.sendToUser(user)

    def get_last_login_data(self) -> tuple | None:
        ip = self._user.get_setting_val('last_login_ip')
        dt = self._user.get_setting_val('last_login_datetime')
        if ip and dt:
            return ip, dt
        return None, None

    def login_success(self, user: GDO_User, bind_ip: bool = False) -> GDT:
        last_ip, last_date = self.get_last_login_data()
        if last_ip:
            self.msg('msg_authenticated_again', [user.render_name(), Time.display_date(last_date), last_ip])
        else:
            self.msg('msg_authenticated', [user.render_name()])
        user.authenticate(self._env_session, bind_ip)
        back = self.param_val('_back_to')
        if back:
            link = GDT_Link().href(back).render()
            self.msg('msg_back_to', [Strings.html(link)])
        return self.get_form()
        # msg('msg_authenticated',)
        # if module_enabled('Session'):
        #     session = GDO_Session.instance()
        #     if not session:
        #         return self.error('err_session_required')
        #     session.setVar('sess_user', user.getID())
        #     GDO_User.setCurrent(user)
        #     if bindIP:
        #         session.setVar('sess_ip', GDT_IP.current())
        #     GDT_Hook.callWithIPC('UserAuthenticated', user)
        #     self.message('msg_authenticated', [user.renderUserName()])
        #     if href := self.gdoParameterVar('_backto'):
        #         self.message('msg_back_to', [html(href)])
        # else:
        #     return self.error('err_session_required')
        # return GDT_Response.make()

    # def validateDeleted(self, form: GDT_Form, field: GDT, value) -> bool:
    #     user = GDO_User.getByLogin(value)
    #     if user and user.isDeleted():
    #         return field.error('err_user_deleted')
    #     return True
    #
    # def validateType(self, form: GDT_Form, field: GDT, value) -> bool:
    #     if value:
    #         user = GDO_User.getByLogin(value)
    #         if user and not user.isMember():
    #             return field.error('err_user_type', [t('enum_member')])
    #     return True
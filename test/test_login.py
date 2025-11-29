import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.core.connector.Web import Web
from gdo.login import module_login
from gdo.mail import module_mail
from gdotest.TestUtil import web_plug, reinstall_module, WebPlug, GDOTestCase


class LoginTest(GDOTestCase):

    async def asyncSetUp(self):
        await super().asyncSetUp()
        Application.init(os.path.dirname(__file__ + "/../../../../"))
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        reinstall_module('login')
        reinstall_module('mail')
        loader.init_modules(True, True)
        user = await Web.get_server().get_or_create_user('gizmore')
        module_login.instance().set_password_for(user, '11111111')
        module_mail.instance().set_email_for(user, 'gizmore@gizmore.org')
        WebPlug.COOKIES = {}

    def test_01_login_form_render(self):
        result = web_plug('login.form.html').post({"login": "gizmore", "password": "11111111"}).exec()
        self.assertIn('<form', result, 'Did not pass render <form')
        self.assertIn('gizmore', result, 'Does not refill form vars')

    def test_02_login_form_incomplete(self):
        result = web_plug('login.form.html').post({"submit": "1", "login": "", "password": "11111111"}).exec()
        self.assertIn('This field may not be left empty', result, 'does not execute command or does not display required username')

    def test_03_login_form_fail_unknown_user(self):
        result = web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "not_gizmore", "password": "11111111"}).exec()
        self.assertIn('Authentication failure. You have ', result, 'login.form does not fail correctly')

    def test_04_login_form_correct(self):
        web_plug('login.logout.html').exec()
        result = web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "gizmore", "password": "11111111"}).exec()
        self.assertIn('Welcome back gizmore', result, 'login.form does not work with correct credentials')

    def test_05_login_form_correct_via_email(self):
        web_plug('login.logout.html').exec()
        result = web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "gizmore@gizmore.org", "password": "11111111"}).exec()
        self.assertIn('been authenticated', result, 'login.form does not work with correct mail credentials')

    def test_06_login_form_brute_block(self):
        web_plug('login.logout.html').exec()
        web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "not_gizmore", "password": "11111111"}).exec()
        web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "not_gizmore", "password": "11111111"}).exec()
        web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "not_gizmore", "password": "11111111"}).exec()
        web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "not_gizmore", "password": "11111111"}).exec()
        web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "not_gizmore", "password": "11111111"}).exec()
        result = web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "gizmore", "password": "11111111"}).exec()
        self.assertIn('Too much authentication failures,', result, 'login.form does not ban users for brute forcing logins')

    def test_07_login_with_ref_back(self):
        web_plug('login.logout.html').exec()
        post_data = {"submit": "1", "bind_ip": "1", "login": "gizmore@gizmore.org", "password": "11111111", '_back_to': '/core.welcome.html'}
        result = web_plug('login.form.html').post(post_data).exec()
        self.assertIn('Welcome back gizmore', result, 'login.form does not login showing refback')
        self.assertIn('core.welcome.html', result, 'login.form does not show ref back')

    def test_08_login_session(self):
        web_plug('login.logout.html').exec()
        post_data = {"submit": "1", "bind_ip": "1", "login": "gizmore@gizmore.org", "password": "11111111", '_back_to': '/core.welcome.html'}
        web_plug('login.form.html').post(post_data).exec()
        result = web_plug('login.form.html').exec()
        self.assertIn('method is restricted to', result, 'Authentication did not persist in session')
        web_plug('login.logout.html')

    def test_09_login_with_bind_ip(self):
        web_plug('login.logout.html').exec()
        post_data = {"submit": "1", "bind_ip": "1", "login": "gizmore@gizmore.org", "password": "11111111", '_back_to': '/core.welcome.html'}
        result = web_plug('login.form.html').post(post_data).exec()
        self.assertIn('Welcome back gizmore', result, 'login.form does not work with bind IP')
        post_data = {"submit": "1", "bind_ip": "1", "login": "gizmore@gizmore.org", "password": "11111111", '_back_to': '/core.welcome.html'}
        result = web_plug('login.form.html').ip('::2').post(post_data).exec()
        self.assertIn('Welcome back gizmore', result, 'login.form does not login showing refback')


if __name__ == '__main__':
    unittest.main()

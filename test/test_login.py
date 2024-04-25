import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Trans import t
from gdo.core.GDO_User import GDO_User
from gdo.core.connector.Web import Web
from gdo.login import module_login
from gdotest.TestUtil import web_plug, reinstall_module


class LoginTest(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__ + "/../../../../"))
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules()
        reinstall_module('login')
        user = Web.get_server().get_or_create_user('gizmore')
        module_login.instance().set_password_for(user, '11111111')
        user.save_setting('email', 'gizmore@gizmore.org')
        return self

    def test_01_login_form_render(self):
        result = web_plug('login.form.html').post({"login": "gizmore", "password": "11111111"}).exec()
        self.assertIn('<nav', result, 'Did not pass render <nav')
        self.assertIn('<form', result, 'Did not pass render <form')
        self.assertIn('gizmore', result, 'Does not refill form vars')

    def test_02_login_form_incomplete(self):
        result = web_plug('login.form.html').post({"submit": "1", "login": "", "password": "11111111"}).exec()
        self.assertIn(t('err_not_null'), result, 'does not execute command or does not display required username')

    def test_03_login_form_fail_unknown_user(self):
        result = web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "not_gizmore", "password": "11111111"}).exec()
        self.assertIn('Authentication failure. You have ', result, 'login.form does not fail correctly')

    def test_04_login_form_correct(self):
        result = web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "gizmore", "password": "11111111"}).exec()
        self.assertIn('Welcome back gizmore!', result, 'login.form does not work with correct credentials')
        GDO_User.current().logout()

    def test_05_login_form_correct_via_email(self):
        result = web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "gizmore@gizmore.org", "password": "11111111"}).exec()
        self.assertIn('been authenticated', result, 'login.form does not work with correct mail credentials')
        GDO_User.current().logout()

    def test_06_login_form_brute_block(self):
        web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "not_gizmore", "password": "11111111"}).exec()
        web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "not_gizmore", "password": "11111111"}).exec()
        web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "not_gizmore", "password": "11111111"}).exec()
        web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "not_gizmore", "password": "11111111"}).exec()
        web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "not_gizmore", "password": "11111111"}).exec()
        result = web_plug('login.form.html').post({"submit": "1", "bind_ip": "1", "login": "gizmore", "password": "11111111"}).exec()
        self.assertIn('Too much authentication failures,', result, 'login.form does not ban users for bruteforcing logins')

    def test_07_login_with_ref_back(self):
        post_data = {"submit": "1", "bind_ip": "1", "login": "gizmore@gizmore.org", "password": "11111111", '_back_to': '/core.welcome2.html'}
        result = web_plug('login.form.html').post(post_data).exec()
        self.assertIn('Welcome back gizmore!', result, 'login.form does not login showing refback')
        self.assertIn('core.welcome2.html', result, 'login.form does not show refback')


if __name__ == '__main__':
    unittest.main()

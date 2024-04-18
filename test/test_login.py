import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Trans import t
from gdo.core.connector.Web import Web
from gdo.login import module_login
from gdotest.TestUtil import install_module, web_plug


class LoginTest(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__ + "/../../../../"))
        loader = ModuleLoader.instance()
        loader.load_modules_db(True)
        loader.init_modules()
        user = Web.get_server().get_or_create_user('gizmore')
        module_login.instance().set_password_for(user, '11111111')
        return self

    def test_login_form_render(self):
        result = web_plug('login.form.html').post({"login": "gizmore", "password": "11111111"}).exec()
        self.assertIn('<nav', result, 'Did not pass render <nav')
        self.assertIn('<form', result, 'Did not pass render <form')
        self.assertIn('gizmore', result, 'Does not refill form vars')

    def test_login_form_fail(self):
        result = web_plug('login.form.html').post({"submit": "1", "login": "", "password": "11111111"}).exec()
        self.assertIn(t('err_not_null'), result, 'does not execute command or does not display required username')

    def test_login_form_timeout(self):
        result = web_plug('login.form.html').post({"submit": "1", "login": "not_gizmore", "password": "11111111"}).exec()
        self.assertIn('aaa', result, 'login.form does not have a bruteforce protection')


if __name__ == '__main__':
    unittest.main()

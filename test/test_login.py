import os
import unittest

from gdo.base.Application import Application
from gdo.base.ModuleLoader import ModuleLoader
from gdo.base.Trans import t
from gdotest.TestUtil import install_module, web_plug


class LoginTest(unittest.TestCase):

    def setUp(self):
        Application.init(os.path.dirname(__file__ + "/../../../../"))
        install_module('login')
        ModuleLoader.instance().load_modules_db(True)
        ModuleLoader.instance().init_modules()
        return self

    def test_login_form_render(self):
        result = web_plug('login.form.html').post({"login": "gizmore", "password": "11111111"}).exec()
        self.assertIn('<nav', result, 'Did not pass render <nav')
        self.assertIn('<form', result, 'Did not pass render <form')
        self.assertIn('gizmore', result, 'Does not refill form vars')

    def test_login_form_fail(self):
        result = web_plug('login.form.html').post({"submit": "1", "login": "", "password": "11111111"}).exec()
        self.assertIn(t('err_not_null'), result, 'does not execute command or does not display required username')


if __name__ == '__main__':
    unittest.main()

from gdo.base.GDO_Module import GDO_Module
from gdo.base.GDT import GDT
from gdo.core.GDT_Password import GDT_Password
from gdo.ui.GDT_Link import GDT_Link
from gdo.ui.GDT_Page import GDT_Page


class module_login(GDO_Module):

    def gdo_user_config(self) -> list[GDT]:
        return [
            GDT_Password('password'),
        ]

    def gdo_init_sidebar(self, page):
        page._left_bar.add_field(GDT_Link().href(self.href('form')))

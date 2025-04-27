from gdo.base.GDO import GDO
from gdo.base.GDT import GDT
from gdo.core.GDT_AutoInc import GDT_AutoInc
from gdo.core.GDT_User import GDT_User
from gdo.date.GDT_Created import GDT_Created
from gdo.net.GDT_IP import GDT_IP


class GDO_LoginAttempt(GDO):

    def gdo_cached(self) -> bool:
        return False

    def gdo_columns(self) -> list[GDT]:
        return [
            GDT_AutoInc('la_id'),
            GDT_User('la_user'),
            GDT_IP('la_ip').use_current().not_null(),
            GDT_Created('la_created'),
        ]

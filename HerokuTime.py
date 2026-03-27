# meta developer: @SunnexGB
# meta pic: https://r2.fakecrime.bio/uploads/7ba33dd9-b0a6-4c1c-8002-dc5c87d83365.jpg
# meta banner: https://r2.fakecrime.bio/uploads/7ba33dd9-b0a6-4c1c-8002-dc5c87d83365.jpg
# meta fhsdesc: Плейсхолдер, placeholder, Time, Время, Статистика, Stats
# крутой баннер да?
#current version
__version__ = (1, 0, 0)

import time
from .. import loader, utils

@loader.tds
class HerokuTime(loader.Module):
    """shows how much heroku you use in total (since installing placeholder)"""

    strings = {
        "name": "HerokuTime",
        "sec": "sec",
        "min": "min",
        "hour": "h",
    }

    strings_ru = {
        "cls_doc": "показывает сколько вы используете всего хероку(с момента установки плейсхолдера)",
        "sec": "сек",
        "min": "мин",
        "hour": "ч",
    }

    async def client_ready(self, client):
        self._client = client
        if not self.get("start_time"):
            self.set("start_time", int(time.time()))
        utils.register_placeholder("alltime", self.get_uptime, "show heroku time usage")

    def format_time(self, seconds: int) -> str:
        if seconds < 60:
            return f"{seconds} {self.strings('sec')}"
        minutes = seconds // 60
        if minutes < 60:
            return f"{minutes} {self.strings('min')} {seconds % 60} {self.strings('sec')}"
        hours = minutes // 60
        return f"{hours} {self.strings('hour')} {minutes % 60} {self.strings('min')} {seconds % 60} {self.strings('sec')}"

    async def get_uptime(self):
        start_time = self.get("start_time")
        if not start_time:
            return f"0 {self.strings('sec')}"
        now = int(time.time())
        uptime = now - start_time
        return self.format_time(uptime)
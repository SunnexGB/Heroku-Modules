# meta developer: @H_SunMods
# meta banner: https://r2.fakecrime.bio/uploads/7c43eb05-4387-48f8-bbb2-20c5fad2f85f.jpg
# current ver
__version__ = (1, 0, 1)
 
from .. import loader, utils
from herokutl.types import Message
from ..types import InlineCall
import asyncio
import aiohttp
import math
 
FHETA_URL = "https://api.fixyres.com/grates"
VECTOR_URL = "https:www.0xvector.lol/api/devstats"
VECTOR_TOPMOD_URL = "https:www.0xvector.lol/api/usertopmod?users="

@loader.tds
class DevStats(loader.Module):
    """developers stats module"""
 
    strings = {
        "name": "DevStats",
        "loading": "<b>Loading...</b>",
        "no_data": "<b>Failed to fetch data. Try again later.</b>",
        "dev_header": "<b><i>Most popular developers:</i></b>\n\n",
        "devtop_not_found": "<b>Your not found.</b>",
        "topmod_not_found": "<b>No modules found.</b>",
        "no_usernames": "<b>No usernames configured.</b> Set them in <code>.fcfg DevStats usernames @username</code>",
        "select_page": "<b>Select page:</b>",
        "btn_prev": "◄",
        "btn_next": "►",
        "btn_back": "Back",
        "btn_close": "Close",
        "like_singl": "like",
        "just_likes": "likes",
        "just_dislikes": "dislikes",
        "devtop_desc": "Your rank in developer leaderboard",
        "topmod_desc": "Your most popular module and its rank",
    }
 
    strings_ru = {
        "_cls_doc": "Модуль статистики разработчиков",
        "loading": "<b>Загрузка...</b>",
        "no_data": "<b>Не удалось получить данные. Попробуйте позже.</b>",
        "dev_header": "<b><i>Самые популярные разработчики:</i></b>\n\n",
        "devtop_not_found": "<b>Вы не были найдены.</b>",
        "topmod_not_found": "<b>Модули не найдены.</b>",
        "no_usernames": "<b>Юзернеймы не настроены.</b> Укажите в <code>.fcfg DevStats usernames @username</code>",
        "select_page": "<b>Выберите страницу:</b>",
        "btn_prev": "◄",
        "btn_next": "►",
        "btn_back": "Назад",
        "btn_close": "Закрыть",
        "like_singl": "Лайк",
        "just_likes": "Лайков",
        "just_dislikes": "Дизлайков",
        "devtop_desc": "Ваше место в рейтинге разработчиков",
        "topmod_desc": "Ваш самый популярный модуль и его место в топе",
    }
 
    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "provider",
                "multi",
                "Data source: multi (fheta + vector combined) | fheta | vector",
                validator=loader.validators.Choice(["multi", "fheta", "vector"]),
            ),
            loader.ConfigValue(
                "display_mode",
                "likes",
                "Display mode: likes | both",
                validator=loader.validators.Choice(["likes", "both"]),
            ),
            loader.ConfigValue(
                "usernames",
                [],
                "Your usernames with @ for placeholders",
                validator=loader.validators.Series(loader.validators.String()),
            ),
            loader.ConfigValue(
                "excluded_authors",
                ["unknown"],
                "Authors to exclude from leaderboard",
                validator=loader.validators.Series(loader.validators.String()),
            ),
            loader.ConfigValue(
                "rank1_emoji",
                "<tg-emoji emoji-id=5429387335626145566>👑</tg-emoji>",
                "Emoji for rank №1",
            ),
            loader.ConfigValue(
                "rank2_emoji",
                "<tg-emoji emoji-id=5429351167706547656>🌟</tg-emoji>",
                "Emoji for rank №2",
            ),
            loader.ConfigValue(
                "rank3_emoji",
                "<tg-emoji emoji-id=5429365839314830135>✨</tg-emoji>",
                "Emoji for rank №3",
            ),
        )
 
    async def client_ready(self, client, db):
        utils.register_placeholder("devtop", self.placeholder_devtop, self.strings("devtop_desc"))
        utils.register_placeholder("topmod", self.placeholder_topmod, self.strings("topmod_desc"))
 
    async def request_api(self, url: str, token: str = None):
        headers = {"Authorization": token} if token else {}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    return await resp.json() if resp.status == 200 else None
        except Exception:
            return None
 
    def aggregate_devs(self, data: dict) -> list:
        excluded = {u.lower() for u in self.config["excluded_authors"]}
        devs = {}
        items = data.items() if isinstance(data, dict) else (
            (e.get("url", i), e) for i, e in enumerate(data)
        )
        for _, info in items:
            author = info.get("author", "").lstrip("@")
            if not author or author.lower() in excluded:
                continue
            if author not in devs:
                devs[author] = {"likes": 0, "dislikes": 0}
            devs[author]["likes"] += int(info.get("likes", 0) or 0)
            devs[author]["dislikes"] += int(info.get("dislikes", 0) or 0)
        return sorted(devs.items(), key=lambda x: x[1]["likes"], reverse=True)

    def aggregate_vector(self, data: list) -> list:
        excluded = {u.lower() for u in self.config["excluded_authors"]}
        devs = {}
        for entry in data:
            author = entry.get("author", "").lstrip("@")
            if not author or author.lower() in excluded:
                continue
            if author not in devs:
                devs[author] = {"likes": 0, "dislikes": 0}
            devs[author]["likes"] += int(entry.get("likes", 0) or 0)
            devs[author]["dislikes"] += int(entry.get("dislikes", 0) or 0)
        return sorted(devs.items(), key=lambda x: x[1]["likes"], reverse=True)

    def merge_sources(self, fheta_devs: list, vector_devs: list) -> list:
        merged = {}
        for username, stats in fheta_devs:
            merged[username.lower()] = {"name": username, "likes": stats["likes"], "dislikes": stats["dislikes"]}
        for username, stats in vector_devs:
            key = username.lower()
            if key in merged:
                merged[key]["likes"] += stats["likes"]
                merged[key]["dislikes"] += stats["dislikes"]
            else:
                merged[key] = {"name": username, "likes": stats["likes"], "dislikes": stats["dislikes"]}
        result = [(v["name"], {"likes": v["likes"], "dislikes": v["dislikes"]}) for v in merged.values()]
        return sorted(result, key=lambda x: x[1]["likes"], reverse=True)

    async def fetch_sorted_devs(self) -> list:
        provider = self.config["provider"]
        if provider == "fheta":
            data = await self.request_api(FHETA_URL)
            return self.aggregate_devs(data) if data else []
        if provider == "vector":
            data = await self.request_api(VECTOR_URL)
            return self.aggregate_vector(data) if isinstance(data, list) else []
        # multi
        fheta_data, vector_data = await asyncio.gather(
            self.request_api(FHETA_URL),
            self.request_api(VECTOR_URL),
        )
        fheta_devs = self.aggregate_devs(fheta_data) if fheta_data else []
        vector_devs = self.aggregate_vector(vector_data) if isinstance(vector_data, list) else []
        if not fheta_devs and not vector_devs:
            return []
        return self.merge_sources(fheta_devs, vector_devs)

    def extract_module_name(self, key: str) -> str:
        return key.strip().split("/")[-1].removesuffix(".py")
 
    def format_stats(self, likes: int, dislikes: int) -> str:
        mode = self.config["display_mode"]
        lw = self.strings["like_singl"] if likes == 1 else self.strings["just_likes"]
        if mode == "both":
            return f"({likes} {lw} | {dislikes} {self.strings['just_dislikes']})"
        return f"({likes} {lw})"
 
    def dev_entry(self, rank: int, username: str, likes: int, dislikes: int) -> str:
        stats = self.format_stats(likes, dislikes)
        emoji = self.config[f"rank{rank}_emoji"] if rank <= 3 else ""
        safe = utils.escape_html(username)
        if emoji:
            return f"{rank}. @{safe} <b>{stats} | </b>{emoji}\n"
        return f"{rank}. @{safe} <b>{stats}</b>\n"
 
    def kb_dev_page(self, sorted_devs: list, page: int) -> str:
        start = page * 10
        text = self.strings["dev_header"]
        for i, (username, stats) in enumerate(sorted_devs[start:start + 10]):
            rank = start + i + 1
            text += self.dev_entry(rank, username, stats["likes"], stats["dislikes"])
        return text
 
    def nav_markup(self, page: int, total: int, on_prev, on_next, on_page) -> list:
        return [
            [
                {"text": self.strings["btn_prev"], "callback": on_prev},
                {"text": f"{page + 1}/{total}", "callback": on_page},
                {"text": self.strings["btn_next"], "callback": on_next},
            ],
            [{"text": self.strings["btn_close"], "action": "close"}],
        ]
 
    def page_selector_markup(self, total: int, page_cb_factory, on_back) -> list:
        buttons, row = [], []
        for p in range(total):
            row.append({"text": str(p + 1), "callback": page_cb_factory(p)})
            if len(row) == 5:
                buttons.append(row)
                row = []
        if row:
            buttons.append(row)
        buttons.append([{"text": self.strings["btn_back"], "callback": on_back}])
        return buttons
 
    async def placeholder_devtop(self) -> str:
        usernames = {u.lstrip("@").lower() for u in self.config["usernames"]}
        if not usernames:
            return self.strings["no_usernames"]
        sorted_devs = await self.fetch_sorted_devs()
        if not sorted_devs:
            return self.strings["no_data"]
        for rank, (username, _) in enumerate(sorted_devs, 1):
            if username.lower() in usernames:
                return f"{rank}"
        return self.strings["devtop_not_found"]
 
    async def placeholder_topmod(self) -> str:
        usernames = {u.lstrip("@").lower() for u in self.config["usernames"]}
        if not usernames:
            return self.strings["no_usernames"]

        provider = self.config["provider"]
        joined_usernames = ",".join(sorted(usernames))

        if provider in {"vector", "multi"}:
            data = await self.request_api(f"{VECTOR_TOPMOD_URL}{joined_usernames}")
            if isinstance(data, dict) and data.get("name") and data.get("rank"):
                return f"{data['name']} ({data['rank']})"
            if provider == "vector":
                return self.strings["topmod_not_found"] if data else self.strings["no_data"]

        data = await self.request_api(FHETA_URL)
        if not data:
            return self.strings["no_data"]
        all_sorted = sorted(
            [(self.extract_module_name(k), v) for k, v in data.items()],
            key=lambda x: int(x[1].get("likes", 0) or 0),
            reverse=True,
        )
        user_mods = [
            (name, val)
            for name, val in all_sorted
            if val.get("author", "").lstrip("@").lower() in usernames
        ]
        if not user_mods:
            return self.strings["topmod_not_found"]
        top_name = user_mods[0][0]
        global_rank = next(
            (i + 1 for i, (name, _) in enumerate(all_sorted) if name == top_name),
            None,
        )
        return (
            f"{top_name} ({global_rank})"
            if global_rank
            else self.strings["topmod_not_found"]
        )
 
    @loader.command(ru_doc="Статистика топ разработчиков")
    async def devstats(self, message: Message):
        """Top Developers statistics"""
        await utils.answer(message, self.strings["loading"])
        sorted_devs = await self.fetch_sorted_devs()
        if not sorted_devs:
            return await utils.answer(message, self.strings["no_data"])
        total_pages = max(1, math.ceil(len(sorted_devs) / 10))
        state = {"page": 0}
 
        def markup():
            return self.nav_markup(state["page"], total_pages, on_prev, on_next, on_page)
 
        def render():
            return self.kb_dev_page(sorted_devs, state["page"])
 
        async def on_prev(call: InlineCall):
            state["page"] = max(0, state["page"] - 1)
            await call.edit(render(), reply_markup=markup())
 
        async def on_next(call: InlineCall):
            state["page"] = min(total_pages - 1, state["page"] + 1)
            await call.edit(render(), reply_markup=markup())
 
        async def on_page(call: InlineCall):
            await call.edit(
                self.strings["select_page"],
                reply_markup=self.page_selector_markup(total_pages, make_page_cb, on_back),
            )
 
        def make_page_cb(p):
            async def go(call: InlineCall):
                state["page"] = p
                await call.edit(render(), reply_markup=markup())
            return go
 
        async def on_back(call: InlineCall):
            await call.edit(render(), reply_markup=markup())
        await utils.answer(message, render(), reply_markup=markup())
#             █ █ ▀ █▄▀ ▄▀█ █▀█ ▀
#             █▀█ █ █ █ █▀█ █▀▄ █
#              © Copyright 2022
#           https://t.me/hikariatama
#
# 🔒      Licensed under the GNU AGPLv3
# 🌐 https://www.gnu.org/licenses/agpl-3.0.html

# meta pic: https://static.dan.tatar/anisearch_icon.png
# meta banner: https://r2.fakecrime.bio/uploads/38dc99ec-1ed3-4e09-830f-785aec51435d.jpg
# meta developer: Author: @hikarimods | Forked by: @SunnexGB
# scope: heroku_only
# scope: heroku_min 2.1.0

import requests
from herokutl.types import Message
from .. import loader, utils

@loader.tds
class AniSearchMod(loader.Module):
    """Searches for anime exact moment by only frame screenshot"""

    strings = {
        "name": "AniSearch",
        "no_lib": "<tg-emoji emoji-id=5348118479847333898>🗑</tg-emoji> | <b>Library not loaded</b>",
        "404": (
            "<tg-emoji emoji-id=5348118479847333898>🗑</tg-emoji> <b>I don't know which"
            " anime it is...</b>"
        ),
        "searching": (
            "<tg-emoji emoji-id=5345778951031658558>😭</tg-emoji> <b>Let me take a"
            " look...</b>"
        ),
        "result": """
        <aside><b>{title}</b></aside>

        <figure>
        <img src="{cover}"/>
        <figcaption>Episode: {ep} | {time} | I think it is ~{proc}% similarity</figcaption>
        </figure>

        <hr/>

        <table bordered>
        <tr>
            <td align="center" valign="middle"><b>Alias</b></td>
            <td><b>{aliases}</b></td>
        </tr>
        <tr>
            <td align="center" valign="middle"><b>Genre</b></td>
            <td><b>{genres}</b></td>
        </tr>
        <tr>
            <td align="center" valign="middle"><b>Studio</b></td>
            <td>
            {studios}
            </td>
        </tr>
        <tr>
            <td align="center" valign="middle"><b>External Links</b></td>
            <td>
            {e_links}
            </td>
        </tr>
        </table>

<aside><b>Information provided by</b> <a href="https://anilist.co/">anilist.co</a></aside>
""",
        "media_not_found": (
            "<tg-emoji emoji-id=5348118479847333898>🗑</tg-emoji> <b>Media not found</b>"
        ),
        "no_data": "no data",
        "header_title_cfg": "header title language"
    }

    strings_ru = {
        "_cls_doc": "Ищет конкретную серию и тайм-код аниме по скриншоту",
        "no_lib": "<tg-emoji emoji-id=5348118479847333898>🗑</tg-emoji> | <b>>Библиотека не была загружена</b>",
        "404": (
            "<tg-emoji emoji-id=5348118479847333898>🗑</tg-emoji> <b>Я не знаю"
            " что это за аниме...</b>"
        ),
        "searching": (
            "<tg-emoji emoji-id=5345778951031658558>😭</tg-emoji> <b>Дай-ка мне"
            " посмотреть...</b>"
        ),
        "result": """
        <aside><b>{title}</b></aside>

        <figure>
        <img src="{cover}"/>
        <figcaption>Серия: {ep} | {time} | Я уверен в сходстве на ~{proc}%</figcaption>
        </figure>

        <hr/>

        <table bordered>
        <tr>
            <td align="center" valign="middle"><b>Другие названия</b></td>
            <td><b>{aliases}</b></td>
        </tr>
        <tr>
            <td align="center" valign="middle"><b>Жанры</b></td>
            <td><b>{genres}</b></td>
        </tr>
        <tr>
            <td align="center" valign="middle"><b>Студии</b></td>
            <td>
            {studios}
            </td>
        </tr>
        <tr>
            <td align="center" valign="middle"><b>Внешние ссылки</b></td>
            <td>
            {e_links}
            </td>
        </tr>
        </table>

<aside><b>Информация бралась из</b> <a href="https://anilist.co/">anilist.co</a></aside>
""",
        "media_not_found": (
            "<tg-emoji emoji-id=5348118479847333898>🗑</tg-emoji> <b>Media not found</b>"
        ),
        "no_data": "no data",
        "header_title_cfg": "Язык на котором будет заголовок."
    }

    strings_jp = {
    "_cls_doc": "スクリーンショットからアニメの特定のエピソードとタイムコードを検索します",
    "name": "AniSearch",
    "no_lib": "<tg-emoji emoji-id=5348118479847333898>🗑</tg-emoji> | <b>ライブラリがロードされていません</b>",
    "404": (
        "<tg-emoji emoji-id=5348118479847333898>🗑</tg-emoji> <b>どのアニメか"
        "わかりません…</b>"
    ),
    "searching": (
        "<tg-emoji emoji-id=5345778951031658558>😭</tg-emoji> <b>ちょっと"
        "見てみますね…</b>"
    ),
    "result": """
    <aside><b>{title}</b></aside>

    <figure>
    <img src="{cover}"/>
    <figcaption>第: {ep}話 | {time} | 類似度約: {proc}%</figcaption>
    </figure>

    <hr/>

    <table bordered>
    <tr>
        <td align="center" valign="middle"><b>別名</b></td>
        <td><b>{aliases}</b></td>
    </tr>
    <tr>
        <td align="center" valign="middle"><b>ジャンル</b></td>
        <td><b>{genres}</b></td>
    </tr>
    <tr>
        <td align="center" valign="middle"><b>スタジオ</b></td>
        <td>
        {studios}
        </td>
    </tr>
    <tr>
        <td align="center" valign="middle"><b>外部リンク</b></td>
        <td>
        {e_links}
        </td>
    </tr>
    </table>

    <aside><b>情報提供元:</b> <a href="https://anilist.co/">anilist.co</a></aside>
    """,
        "media_not_found": (
            "<tg-emoji emoji-id=5348118479847333898>🗑</tg-emoji> <b>メディアが見つかりません</b>"
        ),
        "no_data": "データなし",
        "header_title_cfg": "ヘッダータイトルの言語"
    }

    def __init__(self):
        self.api_url = "https://api.trace.moe/search?anilistInfo"
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "header_title",
                "native",
                lambda: self.strings["header_title_cfg"],
                validator=loader.validators.Choice(["native", "romaji", "chinese", "english"]),
            ),
        )
        self.lib = None

    async def client_ready(self):
        self.lib = await self.import_lib(
            "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/refs/heads/main/External%20libs/rich_message_lib.py",
            suspend_on_error=True,
        )

    async def on_unload(self):
        if self.lib:
            await self.lib.cleanup(self.inline)

    def header_title_language(self, titles):
        language = self.config["header_title"]
        return titles.get(language) or titles.get("native")
 
    def br_list(self, items):
        return ",<br>".join(items) if items else self.strings["no_data"]
 
    def inline_words(self, items):
        return ", ".join(items) if items else self.strings["no_data"]
 
    def format_time(self, seconds):
        hrs, ostatok = divmod(int(seconds), 3600)
        mins, sex = divmod(ostatok, 60)
        return f"{hrs:02d}:{mins:02d}:{sex:02d}"
 
    @loader.command(ru_doc="- Найти аниме по фото", jp_doc="- 写真でアニメを検索", alias="aser")
    async def anisearchcmd(self, message: Message):
        # зачем этот кадр вообще нужен,если в итоге ты отвечаешь скорее просто на фото.
        """- Search anime by photo"""
        if not self.lib:
            return await utils.answer(message, self.strings("no_lib"))
 
        reply = await message.get_reply_message()
        if not message.media and (not reply or not reply.media):
            await utils.answer(message, self.strings("media_not_found"))
            return
 
        message = await utils.answer(message, self.strings("searching"))
        response = await utils.run_sync(
            requests.post,
            self.api_url,
            files={
                "image": await message.client.download_media(
                        message if message.media else reply,
                        bytes,
                )
            },
        )
        search_result = response.json()
 
        if not search_result or not search_result.get("result", False):
            await utils.answer(message, self.strings("404"))
            return
 
        result_endpoint = search_result["result"][0]
        anilist = result_endpoint["anilist"]
        title = anilist["title"]
        synonyms = anilist.get("synonyms", [])
        genres = anilist.get("genres", [])
        studios_edges = anilist.get("studios", {}).get("edges", [])
        external_links = anilist.get("externalLinks", [])
        coverImage = anilist.get("coverImage", {}).get("extraLarge", "")
        episode = result_endpoint["episode"]
        pos_from = result_endpoint["from"]
        pos_to = result_endpoint["to"]
        conf = result_endpoint["similarity"]
        studios = [edge["node"]["name"] for edge in studios_edges]
        links = [f'<a href="{link["url"]}">{link["site"]}</a>' for link in external_links]
        aliases = self.br_list(synonyms)
        genres_list = self.inline_words(genres)
        studios_list = self.br_list(studios)
        links_list = self.br_list(links)
        ep = str(episode)
        time = f"{self.format_time(pos_from)} - {self.format_time(pos_to)}"
        proc = str(round(conf * 100, 2))
 
        await self.lib.r_msg(
            message.client,
            self.inline,
            message.chat_id,
            r_message=self.strings("result").format(
                title=self.header_title_language(title),
                cover=coverImage,
                ep=ep,
                time=time,
                proc=proc,
                aliases=aliases,
                genres=genres_list,
                studios=studios_list,
                e_links=links_list,
            ),
            parse_mode="html",
            rich_mode="auto",
            reply_to=self.lib.send_topic(message),
        )
        await message.delete()

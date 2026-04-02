# requires: aiohttp
# meta banner: https://r2.fakecrime.bio/uploads/c389e9b5-9ef1-495d-a37a-e993ef819b4a.mp4
# meta developer: @SunnexGB
__version__ = (1, 0, 0)

from .. import loader, utils
import re
import aiohttp

@loader.tds
class Mikuru(loader.Module):
    """Censors words with phrase Mikuru Asahina"""

    strings = {
        "name": "Mikuru",
        "mikuru": "<tg-emoji emoji-id=5856940583934760252>🤤</tg-emoji> | <b><i>I cant say this is for u, b-because this is c-classified information</i></b>",
        "adult_mikuru": "<tg-emoji emoji-id=5859584252269564510>😥</tg-emoji> | <b><i>Y-you already k-know s-so much...</i></b>",
        "ignored": "<tg-emoji emoji-id=5859243730082468153>😏</tg-emoji> | <b><i>Y-you can talk about c-classified information in this chat</i></b>",
        "unignored": "<tg-emoji emoji-id=5859594216593691408>☺️</tg-emoji> | <b><i>You cant speak in this chat b-because c-classified information</i></b>",
        "classified_information": "<b>classified information</b>"
    }

    strings_ru = {
        "_cls_doc": "Цензурует слова фразой Микуру Асахины",
        "mikuru": "<tg-emoji emoji-id=5856940583934760252>🤤</tg-emoji> | <b><i>Я не могу сказать тебе это, п-п-потому что это с-секретные сведения</i></b>",
        "adult_mikuru": "<tg-emoji emoji-id=5859584252269564510>😥</tg-emoji> | <b><i>Т-ты и так м-много з-знаешь...</i></b> ",
        "ignored": "<tg-emoji emoji-id=5859243730082468153>😏</tg-emoji> | <b><i>Т-ты можешь говорить о с-секретных сведениях в этом чате</i></b>",
        "unignored": "<tg-emoji emoji-id=5859594216593691408>☺️</tg-emoji> | <b><i>Ты не можешь говорить в этом чате п-потому что с-секретные сведения</i></b>",
        "classified_information": "<b>секретные сведения</b>"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "Ignored_chats",
                [-1002410964167,
                 -1002341345589,
                 -1001697279580,
                 -1001554874075,
                 -1001984640085],
                "Ignored chats",
                validator=loader.validators.Series()
            ),
        )
        self.bad_words = None

    async def client_ready(self, client, db):
        self.db = db
        await self.load_words()

    async def load_words(self):
        cultural_words = [
            "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/refs/heads/main/Assets/Mikuru/cultural_words_ru.txt",
            "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/49f6883d03d1d2c15c82bad55ee4d31f708870ed/Assets/Mikuru/cultural_words_en.txt"
        ]

        words = set()

        async with aiohttp.ClientSession() as session:
            for url in cultural_words:
                try:
                    async with session.get(url) as resp:
                        if resp.status != 200:
                            continue
                        text = await resp.text()
                        for line in text.splitlines():
                            w = line.strip().lower()
                            if w:
                                words.add(w)
                except Exception:
                    pass

        if words:
            self.bad_words = re.compile(
                r"\b(" + "|".join(map(re.escape, words)) + r")\b",
                re.IGNORECASE
            )
        else:
            self.bad_words = None

    @loader.command(ru_doc="- Начать цензурирование")
    async def mikuru(self, message):
        """- lets go censoring"""
        state = self.db.get(self.name, "mikuru_state", False)
        if state:
            self.db.set(self.name, "mikuru_state", False)
            await utils.answer(message, self.strings("adult_mikuru"))
        else:
            self.db.set(self.name, "mikuru_state", True)
            await utils.answer(message, self.strings("mikuru"))

    @loader.command(ru_doc="- Добавить в список игнорируемых чатов(не будет работать в этих чатах) <id/@>")
    async def ignore(self, message):
        """- Add to list ignored chats(will not work in these chats) <id/@>"""
        args = utils.get_args_raw(message)
        if not args:
            target = str(utils.get_chat_id(message))
        else:
            target = args.strip()
        ignored = list(self.config["Ignored_chats"])
        if target in ignored:
            ignored.remove(target)
            self.config["Ignored_chats"] = ignored
            await utils.answer(message, self.strings("unignored"))
        else:
            ignored.append(target)
            self.config["Ignored_chats"] = ignored
            await utils.answer(message, self.strings("ignored"))

    async def watcher(self, message):
        if not self.db.get(self.name, "mikuru_state", False):
            return
        if not message.text:
            return
        if not message.out:
            return

        chat_id = str(utils.get_chat_id(message))
        user_id = str(getattr(message.sender_id, "id", message.sender_id))

        if chat_id in self.config["Ignored_chats"] or user_id in self.config["Ignored_chats"]:
            return
        if not self.bad_words:
            return

        if self.bad_words.search(message.text):
            text = self.bad_words.sub(
                self.strings("classified_information"),
                message.text
            )
            try:
                await message.edit(text)
            except Exception:
                try:
                    await message.delete()
                    await message.respond(text)
                except Exception:
                    pass
# meta developer: @H_SunMods
# meta pic: https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/Hangman/10.png
# meta banner: https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/Hangman/10.png
# meta fhsdesc: Game, Игра, Hangman, Висилица
# крутой баннер да?

#current version
__version__ = ("d", "i", "e")

import random
import aiohttp
from .. import loader, utils
from herokutl.types import Message
from ..types import InlineCall

words = "https://github.com/SunnexGB/Heroku-Modules/raw/refs/heads/main/Assets/Hangman/words.txt"

@loader.tds
class Hangman(loader.Module):
    """Висилица"""

    strings = {
        "name": "Hangman",
        "caption": "<b>{word}</b>",
        "won": "<b>{word}</b>",
        "over": "Игра окончена. Слово было: <b>{word}</b>",
        "already": "<b>Сосиски свои ебаные убрал от этой буквы!</b>",
    }

    HangmanLives = [
        "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/Hangman/full_hp.png",
        "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/Hangman/1.png",
        "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/Hangman/2.png",
        "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/Hangman/3.png",
        "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/Hangman/4.png",
        "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/Hangman/5.png",
        "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/Hangman/6.png",
        "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/Hangman/7.png",
        "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/Hangman/8.png",
        "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/Hangman/9.png",
        "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/Hangman/10.png",
    ]

    async def client_ready(self):
        await self.load_words()

    async def load_words(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(words) as resp:
                    resp.raise_for_status()
                    text = await resp.text()
            self.words = [
                word.strip().upper()
                for word in text.splitlines()
                if word.strip()
            ]
        except Exception:
            self.words = ["СЛЕНДЕРМЕН", "КАЗИНО", "АЗАРТ"]

    def field_w_letters(self, word, guessed):
        return " ".join(l if l in guessed else "_" for l in word)

    def caption(self, state):
        return self.strings["caption"].format(
            word=self.field_w_letters(state["word"], state["guessed"]),
        )

    def russian_latters(self, state, chat_id):
        guessed = state["guessed"]
        wrong = state["wrong"]
        return [
            [
                {"text": "А", "callback": self.on_letter, "args": (chat_id, "А"), **({"style": "success"} if "А" in guessed else {"style": "danger"} if "А" in wrong else {})},
                {"text": "Б", "callback": self.on_letter, "args": (chat_id, "Б"), **({"style": "success"} if "Б" in guessed else {"style": "danger"} if "Б" in wrong else {})},
                {"text": "В", "callback": self.on_letter, "args": (chat_id, "В"), **({"style": "success"} if "В" in guessed else {"style": "danger"} if "В" in wrong else {})},
                {"text": "Г", "callback": self.on_letter, "args": (chat_id, "Г"), **({"style": "success"} if "Г" in guessed else {"style": "danger"} if "Г" in wrong else {})},
                {"text": "Д", "callback": self.on_letter, "args": (chat_id, "Д"), **({"style": "success"} if "Д" in guessed else {"style": "danger"} if "Д" in wrong else {})},
                {"text": "Е", "callback": self.on_letter, "args": (chat_id, "Е"), **({"style": "success"} if "Е" in guessed else {"style": "danger"} if "Е" in wrong else {})},
                {"text": "Ё", "callback": self.on_letter, "args": (chat_id, "Ё"), **({"style": "success"} if "Ё" in guessed else {"style": "danger"} if "Ё" in wrong else {})},
                {"text": "Ж", "callback": self.on_letter, "args": (chat_id, "Ж"), **({"style": "success"} if "Ж" in guessed else {"style": "danger"} if "Ж" in wrong else {})},
            ],
            [
                {"text": "З", "callback": self.on_letter, "args": (chat_id, "З"), **({"style": "success"} if "З" in guessed else {"style": "danger"} if "З" in wrong else {})},
                {"text": "И", "callback": self.on_letter, "args": (chat_id, "И"), **({"style": "success"} if "И" in guessed else {"style": "danger"} if "И" in wrong else {})},
                {"text": "Й", "callback": self.on_letter, "args": (chat_id, "Й"), **({"style": "success"} if "Й" in guessed else {"style": "danger"} if "Й" in wrong else {})},
                {"text": "К", "callback": self.on_letter, "args": (chat_id, "К"), **({"style": "success"} if "К" in guessed else {"style": "danger"} if "К" in wrong else {})},
                {"text": "Л", "callback": self.on_letter, "args": (chat_id, "Л"), **({"style": "success"} if "Л" in guessed else {"style": "danger"} if "Л" in wrong else {})},
                {"text": "М", "callback": self.on_letter, "args": (chat_id, "М"), **({"style": "success"} if "М" in guessed else {"style": "danger"} if "М" in wrong else {})},
                {"text": "Н", "callback": self.on_letter, "args": (chat_id, "Н"), **({"style": "success"} if "Н" in guessed else {"style": "danger"} if "Н" in wrong else {})},
                {"text": "О", "callback": self.on_letter, "args": (chat_id, "О"), **({"style": "success"} if "О" in guessed else {"style": "danger"} if "О" in wrong else {})},
            ],
            [
                {"text": "П", "callback": self.on_letter, "args": (chat_id, "П"), **({"style": "success"} if "П" in guessed else {"style": "danger"} if "П" in wrong else {})},
                {"text": "Р", "callback": self.on_letter, "args": (chat_id, "Р"), **({"style": "success"} if "Р" in guessed else {"style": "danger"} if "Р" in wrong else {})},
                {"text": "С", "callback": self.on_letter, "args": (chat_id, "С"), **({"style": "success"} if "С" in guessed else {"style": "danger"} if "С" in wrong else {})},
                {"text": "Т", "callback": self.on_letter, "args": (chat_id, "Т"), **({"style": "success"} if "Т" in guessed else {"style": "danger"} if "Т" in wrong else {})},
                {"text": "У", "callback": self.on_letter, "args": (chat_id, "У"), **({"style": "success"} if "У" in guessed else {"style": "danger"} if "У" in wrong else {})},
                {"text": "Ф", "callback": self.on_letter, "args": (chat_id, "Ф"), **({"style": "success"} if "Ф" in guessed else {"style": "danger"} if "Ф" in wrong else {})},
                {"text": "Х", "callback": self.on_letter, "args": (chat_id, "Х"), **({"style": "success"} if "Х" in guessed else {"style": "danger"} if "Х" in wrong else {})},
                {"text": "Ц", "callback": self.on_letter, "args": (chat_id, "Ц"), **({"style": "success"} if "Ц" in guessed else {"style": "danger"} if "Ц" in wrong else {})},
            ],
            [
                {"text": "Ч", "callback": self.on_letter, "args": (chat_id, "Ч"), **({"style": "success"} if "Ч" in guessed else {"style": "danger"} if "Ч" in wrong else {})},
                {"text": "Ш", "callback": self.on_letter, "args": (chat_id, "Ш"), **({"style": "success"} if "Ш" in guessed else {"style": "danger"} if "Ш" in wrong else {})},
                {"text": "Щ", "callback": self.on_letter, "args": (chat_id, "Щ"), **({"style": "success"} if "Щ" in guessed else {"style": "danger"} if "Щ" in wrong else {})},
                {"text": "Ъ", "callback": self.on_letter, "args": (chat_id, "Ъ"), **({"style": "success"} if "Ъ" in guessed else {"style": "danger"} if "Ъ" in wrong else {})},
                {"text": "Ь", "callback": self.on_letter, "args": (chat_id, "Ь"), **({"style": "success"} if "Ь" in guessed else {"style": "danger"} if "Ь" in wrong else {})},
                {"text": "Ы", "callback": self.on_letter, "args": (chat_id, "Ы"), **({"style": "success"} if "Ы" in guessed else {"style": "danger"} if "Ы" in wrong else {})},
                {"text": "Э", "callback": self.on_letter, "args": (chat_id, "Э"), **({"style": "success"} if "Э" in guessed else {"style": "danger"} if "Э" in wrong else {})},
                {"text": "Ю", "callback": self.on_letter, "args": (chat_id, "Ю"), **({"style": "success"} if "Ю" in guessed else {"style": "danger"} if "Ю" in wrong else {})},
            ],
            [
                {"text": "Я", "callback": self.on_letter, "args": (chat_id, "Я"), **({"style": "success"} if "Я" in guessed else {"style": "danger"} if "Я" in wrong else {})},
            ],
        ]

    async def on_letter(self, call: InlineCall, chat_id: int, letter: str):
        letter = letter.upper()
        state = self.get(f"pidor_{chat_id}", None)

        if letter in state["guessed"] or letter in state["wrong"]:
            await call.answer(self.strings["already"], show_alert=True)
            return

        if letter in state["word"]:
            state["guessed"].append(letter)
            self.set(f"pidor_{chat_id}", state)

            if "_" not in self.field_w_letters(state["word"], state["guessed"]):
                self.set(f"pidor_{chat_id}", None)
                await call.edit(self.strings["won"].format(word=state["word"]))
                return

            await call.edit(self.caption(state), reply_markup=self.russian_latters(state, chat_id))

        else:
            state["wrong"].append(letter)
            self.set(f"pidor_{chat_id}", state)

            wrong_count = len(state["wrong"])
            stage = min(wrong_count, len(self.HangmanLives) - 1)

            if wrong_count >= 10:
                self.set(f"pidor_{chat_id}", None)
                await call.edit(
                    self.strings["over"].format(word=state["word"]),
                    photo=self.HangmanLives[stage],
                )
                return

            await call.edit(
                self.caption(state),
                reply_markup=self.russian_latters(state, chat_id),
                photo=self.HangmanLives[stage],
            )

    @loader.command(ru_doc="(.oleg) Начать висилицу", alias="oleg")
    async def hangman(self, message: Message):
        """(.oleg) Start hangman game"""
        chat_id = message.chat_id
        word = random.choice(self.words)
        state = {"word": word, "guessed": [], "wrong": []}
        self.set(f"pidor_{chat_id}", state)

        await self.inline.form(
            message=message,
            text=self.caption(state),
            reply_markup=self.russian_latters(state, chat_id),
            photo=self.HangmanLives[0],
        )
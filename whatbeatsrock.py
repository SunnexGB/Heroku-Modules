# requires: aiohttp
# https://sunnexgb.github.io/Heroku-documentations-md/quickstart-development/
# meta pic: https://r2.fakecrime.bio/uploads/ee7f6884-af8d-4af9-8356-56eec2f8c2a3.jpg
# meta banner: https://r2.fakecrime.bio/uploads/ee7f6884-af8d-4af9-8356-56eec2f8c2a3.jpg
# meta developer: @H_SunMods
#current version
__version__ = (1, 0, 0)

from .. import loader, utils
from herokutl.types import Message
from ..types import InlineCall
import aiohttp
import uuid

@loader.tds
class WhatBeatsRock(loader.Module):
    "Rock scissors paper /w AI"
    strings = {
        "name": "WhatBeatsRock",
        "main_msg": (
            "⠀⠀⠀⠀⠀⠀⠀    ⠀<b>what beats</b>:\n"
            "⠀⠀⠀⠀⠀⠀⠀⠀    ⠀⠀<code>{item}?</code>\n"
            "⠀⠀⠀⠀⠀⠀⠀⠀⠀    ⠀⠀{emoji}\n"
            " <blockquote>{reason}</blockquote>\n\n"
            " <b>follow the creators </b><a href=\"https://x.com/dragon_khoi\"><b>khoi🐟</b></a><b> & </b><a href=\"https://x.com/qualiaspace\"><b>kyle</b></a>🥬\n"
            "⠀<b>join the community on </b><a href=\"https://discord.gg/bjbHyFEyWv\"><b>discord</b></a> 💬\n"
            "⠀<b>powered by </b><a href=\"https://deepinfra.com/?utm_source=whatbeatsrock\"><b>deepinfra</b></a> 🤖"
        ),
        "give_guess": "What a beat this is item",
        "guess_btn": "Enter guess",
        "close_btn": "Close",
    }

    def __init__(self):
        self.api_url = "https://www.whatbeatsrock.com/api/vs"
        self.request_headers = {
            "User-Agent": "Telegram/6.9 (H_SunMods; SlendermanOS x86_64)",
            "Accept": "*/*",
            "Referer": "https://www.whatbeatsrock.com/",
            "Content-Type": "application/json",
            "Origin": "https://www.whatbeatsrock.com",
        }
        self.item = "rock"
        self.emoji = "\U0001FAA8"
        self.reason = ""
        self.score = 0
        self.game_id = str(uuid.uuid4())
        self.session = None

    async def client_ready(self):
        self.session = aiohttp.ClientSession()

    async def on_unload(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def request_result(self, prev_item, guess, game_id):
        payload = {"prev": prev_item, "guess": guess, "gid": game_id}
        async with self.session.post(
            self.api_url, json=payload, headers=self.request_headers
        ) as response:
            return await response.json()

    def Inlive_keyboard(self, game_over=False):
        if game_over:
            return [[{"text": self.strings["close_btn"], "callback": self.close}]]
        return [
            [
                {
                    "text": self.strings["guess_btn"],
                    "input": self.strings["give_guess"],
                    "handler": self.process_guess,
                },
            ],
            [{"text": self.strings["close_btn"], "callback": self.close}],
        ]

    async def close(self, call: InlineCall):
        return await call.delete()

    def create_game_msg(self):
        return self.strings["main_msg"].format(
            item=self.item,
            emoji=self.emoji,
            reason=self.reason,
            score=self.score,
        )

    @loader.command()
    async def wbr(self, message: Message):
        "start a game"
        self.item = "rock"
        self.emoji = "\U0001FAA8"
        self.reason = ""
        self.score = 0
        self.game_id = str(uuid.uuid4())
        await utils.answer(
            message,
            self.create_game_msg(),
            reply_markup=self.Inlive_keyboard(),
        )

    async def process_guess(self, call: InlineCall, guess: str):
        result = await self.request_result(self.item, guess, self.game_id)
        data = result.get("data", {})
        self.reason = data.get("reason", "")

        if data.get("guess_wins"):
            self.item = guess
            self.emoji = data.get("guess_emoji", "")
            self.score += 1
            await call.edit(
                self.create_game_msg(),
                reply_markup=self.Inlive_keyboard(),
            )
        else:
            self.item = "rock"
            self.emoji = "\U0001FAA8"
            self.score = 0
            self.game_id = str(uuid.uuid4())
            await call.edit(
                self.create_game_msg(),
                reply_markup=self.Inlive_keyboard(game_over=True),
            )
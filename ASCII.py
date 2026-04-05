# requires: Pillow numpy
# meta developer: @SunnexGB
# meta banner: https://i.pinimg.com/control1/1200x/24/8d/40/248d40b6afa5bd3c3764556b50635691.jpg
__version__ = (1, 0, 0)

import io
import logging
from herokutl.types import Message
from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class ASCII(loader.Module):
    """Convert images to braille ASCII"""

    strings = {
        "name": "ASCII",
        "no_lib": "<tg-emoji emoji-id=5447385112612208213>🚫</tg-emoji> | <b>Library not loaded</b>",
        "no_image": "<tg-emoji emoji-id=5447381715293074599>⚠️</tg-emoji> | <b>Reply to image</b>",
        "processing": "<tg-emoji emoji-id=5445373981290952548>®️</tg-emoji> | <b>Processing...</b>",
        "empty": "<tg-emoji emoji-id=5287613115180006030>🤬</tg-emoji> | <b>Empty result</b>",
        "result": "<pre>{art}</pre>",
        "Failed_to_load_library": "Failed to load library",
        "Conversion_error": "Conversion error",
    }

    strings_ru = {
        "_cls_doc": "Конвертирует картинку в braille ASCII",
        "no_lib": "<tg-emoji emoji-id=5447385112612208213>🚫</tg-emoji> | <b>Библиотека не была загружена</b>",
        "no_image": "<tg-emoji emoji-id=5447381715293074599>⚠️</tg-emoji> | <b>Ответьте на картинку</b>",
        "processing": "<tg-emoji emoji-id=5445373981290952548>®️</tg-emoji> | <b>Обработка...</b>",
        "empty": "<tg-emoji emoji-id=5287613115180006030>🤬</tg-emoji> | <b>Пустой результат</b>",
        "result": "<pre>{art}</pre>",
        "Failed_to_load_library": "Не удалось загрузить библиотеку",
        "Conversion_error": "Ошибка конвертации",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue("width", 50),
            loader.ConfigValue("threshold", 0.65),
            loader.ConfigValue("contrast", 2.0),
            loader.ConfigValue("chars", 464),
            loader.ConfigValue("invert", False),
        )
        self.lib = None

    async def client_ready(self):
        try:
            self.lib = await self.import_lib("https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/refs/heads/main/Assets/ASCII/ascii-lib.py", suspend_on_error=True)
        except Exception:
            logger.exception(self.strings["Failed_to_load_library"])
            self.lib = None

    @loader.command(ru_doc="- Отрисовать ASCII-ART (аргумент -f, отправляет файлом)")
    async def dotcmd(self, message: Message):
        """- Draw ASCII-ART (argument -f, sends as a file)"""
        if not self.lib:
            return await utils.answer(message, self.strings["no_lib"])
        args = utils.get_args_raw(message)
        force_file = "-f" in args.lower()
        reply = await message.get_reply_message() or message
        if not reply or not (
            reply.photo
            or (
                reply.document
                and str(getattr(reply.document, "mime_type", "")).startswith("image/")
            )
        ):
            return await utils.answer(message, self.strings["no_image"])
        msg = await utils.answer(message, self.strings["processing"])

        try:
            image_bytes = await reply.download_media(bytes)
            art = self.lib.convert(
                image_bytes,
                width=self.config["width"],
                threshold=self.config["threshold"],
                contrast_boost=self.config["contrast"],
                invert=self.config["invert"],
                target_chars=self.config["chars"],
            )

        except Exception as e:
            logger.exception(self.strings["Conversion_error"])
            return await utils.answer(msg, f"<pre>{e}</pre>")
        if not art or not art.strip():
            return await utils.answer(msg, self.strings["empty"])
        formatted_art = self.strings("result").format(art=art)
        if force_file or len(formatted_art) > 4096:
            file = io.BytesIO(art.encode("utf-8"))
            file.name = "ascii.txt"
            await message.client.send_file(message.peer_id, file)
            await msg.delete()
        else:
            await utils.answer(msg, formatted_art)
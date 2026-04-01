# meta pic: https://r2.fakecrime.bio/uploads/54b3c78d-38cb-4970-b925-18b7ec2b268d.jpg
# meta banner: https://r2.fakecrime.bio/uploads/54b3c78d-38cb-4970-b925-18b7ec2b268d.jpg
# requires: https://files.pythonhosted.org/packages/2f/66/31ecae67c373421db10f250a83d80653d6908f7d95080c46816102bd1fda/shazamio-0.8.1.tar.gz https://files.pythonhosted.org/packages/dd/4d/7ecffb341d646e016be76e36f5a42cb32f409c9ca21a57b68f067fad3fc7/python_ffmpeg-2.0.12.tar.gz
# meta developer: @SunnexGB
#current version
__version__ = (1, 0, 0)

from heroku import loader, utils
import os
import asyncio
from shazamio import Shazam

@loader.tds
class Shazamio(loader.Module):
    """Music recognition module"""

    strings = {
        "name": "Shazamio",
        "processing": "<b>Processing <emoji document_id=5325731315004218660>🫥</emoji></b>",
        "shazaming": "<b><emoji document_id=4967658551506895731>🔈</emoji>| Shazaming...</b>",
        "no_reply": "<emoji document_id=4970127715320464315>🚫</emoji>| <b>Reply to a video message.</b>",
        "no_video": "<b><emoji document_id=4970127715320464315>🚫</emoji>| Reply must be to a video message.</b>",
        "ffmpeg_error": "<b><emoji document_id=4970127715320464315>🚫</emoji>| Failed to read audio. Make sure ffmpeg is installed.</b>",
        "not_found": "<b><emoji document_id=4970239229851337393>✖️</emoji>| Sorry, could not recognize the song.</b>",
        "result": "<b><emoji document_id=4967689020004893467>🔈</emoji>| Song recognized:</b>\n\n"
                  "<b><emoji document_id=4967689020004893467>🔈</emoji>Artist:</b><code>{artist}</code>\n"
                  "<b><emoji document_id=4967925573918655510>🚮</emoji>Title:</b><code>{title}</code>",
        "result_url": "<b><emoji document_id=4967503352863654812>〰️</emoji>Song recognized:</b>\n\n"
                      "<b><emoji document_id=4967925573918655510>🚮</emoji>Artist:</b><code>{artist}</code>\n"
                      "<b><emoji document_id=4967689020004893467>🔈</emoji>Title:</b><code>{title}</code>\n\n"
                      "<emoji document_id=4967826519087907994>🔗</emoji><a href=\"{url}\">Listen on Shazam</a>",
        "shazam_history": "<emoji document_id=4969829017524896906>〰️</emoji>| <b>Your last 10 recognised songs</b>", # i put it off for later and then forgot i wanted to implement it
        "no_history": "<emoji document_id=4970064390322652183>〰️</emoji>| <b>What do you want to see here?</b>", # i put it off for later and then forgot i wanted to implement it
    }

    strings_ru = {
        "name": "Shazamio",
        "_cls_doc": "Модуль для распознования музыки",
        "processing": "<b>Обработка <emoji document_id=5325731315004218660>🫥</emoji></b>",
        "shazaming": "<b><emoji document_id=4967658551506895731>🔈</emoji>| Шазамлю...</b>",
        "no_reply": "<emoji document_id=4970127715320464315>🚫</emoji>| <b>Ответьте на сообщение с видео.</b>",
        "no_video": "<b><emoji document_id=4970127715320464315>🚫</emoji>| Ответ должен быть на видео</b>",
        "ffmpeg_error": "<b><emoji document_id=4970127715320464315>🚫</emoji>| Неудачное чтение аудио. Убедитесь что <code>ffmpeg</code> установлен.<a href=\"https://t.me/heroku_talks/8/66067\">Инструкция по установке</a></b>",
        "not_found": "<b><emoji document_id=4970239229851337393>✖️</emoji>| Простите, песня не была найдена.</b>",
        "result": "<b><emoji document_id=4967689020004893467>🔈</emoji>| Песня найдена:</b>\n\n"
                  "<b><emoji document_id=4967689020004893467>🔈</emoji>Исполнитель:</b><code>{artist}</code>\n"
                  "<b><emoji document_id=4967925573918655510>🚮</emoji>Название:</b><code>{title}</code>",
        "result_url": "<b><emoji document_id=4967503352863654812>〰️</emoji>Песня найдена:</b>\n\n"
                      "<b><emoji document_id=4967925573918655510>🚮</emoji>Исполнитель:</b><code>{artist}</code>\n"
                      "<b><emoji document_id=4967689020004893467>🔈</emoji>Название:</b><code>{title}</code>\n\n"
                      "<emoji document_id=4967826519087907994>🔗</emoji><a href=\"{url}\">Слушайте на Shazam</a>",
        "shazam_history": "<emoji document_id=4969829017524896906>〰️</emoji>| <b>Твои 10 последних распознаных треков</b>", # на потом,я забыл что я хотел это реализовать
        "no_history": "<emoji document_id=4970064390322652183>〰️</emoji>| <b>Ну и что ты тут хотел увидеть?</b>", # на потом,я забыл что я хотел это реализовать
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
                "ffmpeg_path",
                "ffmpeg",
                "Path to ffmpeg executable",
        )

    @loader.command(ru_doc="Распознать музыку (Ответом на видео)")
    async def shazam(self, message):
        """Recognize music (Reply in video)"""
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, self.strings("no_reply"))
            return

        if not reply.video:
            await utils.answer(message, self.strings("no_video"))
            return

        await utils.answer(message, self.strings("processing"))
        video_path = await message.client.download_media(reply.video)
        base, _ = os.path.splitext(video_path)
        audio_path = f"{base}.mp3"

        try:
            cmd = (
                f'{self.config["ffmpeg_path"]} -i "{video_path}" '
                f'-y -vn -ab 128k -ar 44100 -f mp3 "{audio_path}"'
            )
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await proc.communicate()

            await utils.answer(message, self.strings("shazaming"))
            shazam = Shazam()
            result = await shazam.recognize(audio_path)

            track = result.get("track")
            if track:
                title = track.get("title", "Unknown Title")
                artist = track.get("subtitle", "Unknown Artist")
                url = track.get("url")

                if url:
                    text = self.strings("result_url").format(
                        title=title, artist=artist, url=url
                    )
                else:
                    text = self.strings("result").format(
                        title=title, artist=artist
                    )

                await utils.answer(message, text)
            else:
                await utils.answer(message, self.strings("not_found"))

        finally:
            if os.path.exists(video_path):
                os.remove(video_path)
            if os.path.exists(audio_path):
                os.remove(audio_path)
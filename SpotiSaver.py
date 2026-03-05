# Спасибо: snfsx, кезу, а так же Gemini
#  блять я забыл поменять параметры для дебага...
# requires: httpx
# meta developer: @SunnexGB
# meta repo: https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/refs/heads/main/spotisaver.py
# meta pic: https://r2.fakecrime.bio/uploads/ddf03169-09fe-4eb1-8eea-bad1a4cc4ada.jpg
# meta banner: https://r2.fakecrime.bio/uploads/ddf03169-09fe-4eb1-8eea-bad1a4cc4ada.jpg
# meta fhsdesc: Spotify, downloader, music, музыка, спотифай,скачать музыку
#current version
__version__ = (1, 0, 1)

import httpx
import os
import re
import random
import string
import logging
from .. import loader, utils
from herokutl.types import Message

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

@loader.tds
class SpotiSaver(loader.Module):
    """Downloading music from Spotify via Spotisaver"""
    
    strings = {
        "name": "SpotiSaver",
        "args": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> link to song is not specified</b>",
        "downloading": "<b><tg-emoji emoji-id=5443127283898405358>📥</tg-emoji> Downloading:</b> <code>{}</code>",
        "error": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> Error`, see logs!</b>",
        "done": "<b><tg-emoji emoji-id=5206607081334906820>✔️</tg-emoji> Done!</b>",
        "nf_id": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> ID key not found!</b>",
        "nf_track": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> Song not found.</b>"
    }

    strings_ru = {
        "name": "SpotiSaver",
        "_cls_doc": "Скачивание музыки из Spotify через Spotisaver",
        "args": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> Ссылка на песню не указана</b>",
        "downloading": "<b><tg-emoji emoji-id=5443127283898405358>📥</tg-emoji> Скачиваю:</b> <code>{}</code>",
        "error": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> Ерорь, смотри логи!</b>",
        "done": "<b><tg-emoji emoji-id=5206607081334906820>✔️</tg-emoji> Готово!</b>",
        "nf_id": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> ID песни не найден</b>",
        "nf_track": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> Песня не найдена</b>"
    }

    def generate_uid(self) -> str:
        prefix = "699f56"
        first_part = ''.join(random.choices(string.digits + string.ascii_lowercase, k=8))
        second_part = ''.join(random.choices(string.digits, k=8))
        return f"v_{prefix}{first_part}.{second_part}"

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "TimeOut",
                60,
                "Response timeout in seconds | Время ожидания ответа в секундах",
                validator=loader.validators.Integer(minimum=30),
            )
        )
        
    @loader.command(ru_doc="<ссылка> — Скачать трек из Spotify")
    async def spotsave(self, message: Message):
        """<link> - Download track from Spotify"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings["args"])

        track_id_match = re.search(r"track/([a-zA-Z0-9]+)", args)
        if not track_id_match:
            return await utils.answer(message, self.strings["nf_id"])
        
        track_id = track_id_match.group(1)
        cookies = {"_s-uid": self.generate_uid()}
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Origin': 'https://spotisaver.net',
            'Referer': f'https://spotisaver.net/ru/track/{track_id}/'
        }

        try:
            async with httpx.AsyncClient(http2=True, follow_redirects=True, cookies=cookies) as client:
                info_url = f"https://spotisaver.net/api/get_playlist.php?id={track_id}&type=track&lang=ru"
                info_res = await client.get(info_url, headers=headers)
                
                if info_res.status_code != 200:
                    return await utils.answer(message, self.strings["error"])

                info_data = info_res.json()
                if 'tracks' not in info_data or not info_data['tracks']:
                    return await utils.answer(message, self.strings["nf_track"])

                track_data = info_data['tracks'][0]
                track_name = track_data['name']
                artists = track_data.get('artists', [])
                artistrack_name = ", ".join(artists) if isinstance(artists, list) else str(artists)
                full_name = f"{artistrack_name} - {track_name}"

                message = await utils.answer(message, self.strings["downloading"].format(utils.escape_html(full_name)))

                payload = {
                    "track": track_data,
                    "download_dir": "downloads",
                    "filename_tag": "SPOTISAVER",
                    "is_premium": False
                }
                
                response = await client.post(
                    "https://spotisaver.net/api/download_track.php",
                    headers=headers,
                    json=payload,
                    timeout=self.config["TimeOut"]
                )

                content = response.content
                if "application/json" in response.headers.get("Content-Type", ""):
                    res_json = response.json()
                    if res_json.get("url"):
                        file_res = await client.get(res_json["url"], timeout=self.config["TimeOut"])
                        content = file_res.content
   
                filename = f"{track_id}.mp3" 
                with open(filename, "wb") as f:
                    f.write(content)

                await self.client.send_file(
                    message.chat_id, 
                    filename, 
                    caption=self.strings["done"],
                    reply_to=message.id,
                    attributes=[
                        utils.get_audio_tag(filename, title=track_name, performer=artistrack_name)
                    ] if hasattr(utils, "get_audio_tag") 
                    else []
                )

                await message.delete()

                if os.path.exists(filename):
                    os.remove(filename)

        except Exception as e:
            logger.exception("Download failed")
            await utils.answer(message, self.strings["error"].format(str(e)))
# Спасибо: snfsx, кезу, а так же Gemini
# requires: httpx
# meta developer: @SunnexGB
# meta repo: https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/refs/heads/main/spotisaver.py
# meta pic: https://r2.fakecrime.bio/uploads/ddf03169-09fe-4eb1-8eea-bad1a4cc4ada.jpg
# meta banner: https://r2.fakecrime.bio/uploads/ddf03169-09fe-4eb1-8eea-bad1a4cc4ada.jpg
# meta fhsdesc: Spotify, downloader, music, музыка, спотифай,скачать музыку
# это не должно было быть в релизе,но ладно я потом пофикшу все и вся в говнокоде.
__version__ = (1, 1, 0)

import asyncio
import httpx
import os
import re
import logging
from .. import loader, utils
from herokutl.types import Message

logger = logging.getLogger(__name__)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://spotmate.online",
    "Referer": "https://spotmate.online/en1",
}

@loader.tds
class SpotiSaver(loader.Module):
    """Downloading music from Spotify"""
    strings = {
        "name": "SpotiSaver",
        "args": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> link to song is not specified</b>",
        "downloading": "<b><tg-emoji emoji-id=5443127283898405358>📥</tg-emoji> Downloading:</b> <code>{}</code>",
        "error": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> Error, see logs!</b>",
        "done": "<b><tg-emoji emoji-id=5206607081334906820>✔️</tg-emoji> Done!</b>",
        "nf_id": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> ID key not found!</b>",
        "nf_track": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> Song not found.</b>",
        "timeout": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> timeout! Try again.</b>",
    }

    strings_ru = {
        "name": "SpotiSaver",
        "_cls_doc": "Скачивание музыки из Spotify",
        "args": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> Ссылка на песню не указана</b>",
        "downloading": "<b><tg-emoji emoji-id=5443127283898405358>📥</tg-emoji> Скачиваю:</b> <code>{}</code>",
        "error": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> Ерорь, смотри логи!</b>",
        "done": "<b><tg-emoji emoji-id=5206607081334906820>✔️</tg-emoji> Готово!</b>",
        "nf_id": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> ID песни не найден</b>",
        "nf_track": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> Песня не найдена</b>",
        "timeout": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> Таймаут! Попробуй ещё раз.</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "TimeOut",
                60,
                "Response timeout in seconds | Время ожидания ответа в секундах",
                validator=loader.validators.Integer(minimum=30),
            )
        )

    async def get_session(self, client: httpx.AsyncClient) -> str:
        res = await client.get("https://spotmate.online/en1", headers={
            "User-Agent": headers["User-Agent"],
            "Accept": "text/html",
        }, 
        timeout=self.config["TimeOut"])
        match = re.search(r'csrf-token[^>]*content="([^"]+)"', res.text)
        if not match:
            raise ValueError("CSRF token not found")
        return match.group(1)

    @loader.command(ru_doc="<ссылка> — Скачать трек из Spotify")
    async def spotsave(self, message: Message):
        """<link> - Download track from Spotify"""
        args = utils.get_args_raw(message)
        if not args:
            return await utils.answer(message, self.strings["args"])
        if "track/" not in args:
            return await utils.answer(message, self.strings["nf_id"])
        track_url = args.split("?")[0]
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                csrf = await self.get_session(client)
                hdrs = {**headers, "X-CSRF-TOKEN": csrf}
                info_res = await client.post(
                    "https://spotmate.online/getTrackData",
                    headers=hdrs,
                    json={"spotify_url": track_url},
                    timeout=self.config["TimeOut"],
                )
                
                info = info_res.json()
                if info.get("type") != "track":
                    return await utils.answer(message, self.strings["nf_track"])
                track_name = info.get("name", "Unknown")
                artists = ", ".join(a["name"] for a in info.get("artists", []))
                full_name = f"{artists} - {track_name}"
                track_id = info.get("id", track_url.split("/")[-1])
                conv_res = await client.post(
                    "https://spotmate.online/convert",
                    headers=hdrs,
                    json={"urls": track_url},
                    timeout=self.config["TimeOut"],
                )
                conv = conv_res.json()
                download_url = conv.get("url") or conv.get("download_url")
                task_id = conv.get("task_id") or conv.get("taskId")
                if not download_url and task_id:
                    for _ in range(40):
                        await asyncio.sleep(4.5)
                        task_res = await client.get(
                            f"https://spotmate.online/tasks/{task_id}",
                            headers={**hdrs, "Accept": "application/json"},
                            timeout=self.config["TimeOut"],
                        )
                        task = task_res.json()
                        if task.get("error"):
                            return await utils.answer(message, self.strings["error"])
                        data = task.get("data") or task.get("result") or {}
                        status = str(data.get("status") or data.get("state") or "").lower()
                        if status == "finished":
                            download_url = (
                                data.get("url") or data.get("download_url")
                                or (data.get("result") or {}).get("url")
                                or (data.get("result") or {}).get("download_url")
                            )
                            break

                        if status in ("failed", "error", "expired", "cancelled"):
                            return await utils.answer(message, self.strings["error"])

                if not download_url:
                    return await utils.answer(message, self.strings["timeout"])

                await utils.answer(
                    message,
                    self.strings["downloading"].format(utils.escape_html(full_name)),
                )
                
                file_res = await client.get(
                    download_url,
                    headers={"User-Agent": headers["User-Agent"], "Referer": "https://spotmate.online/en1"},
                    timeout=self.config["TimeOut"],
                )

                filename = f"{track_id}.mp3"
                with open(filename, "wb") as f:
                    f.write(file_res.content)

                await self.client.send_file(
                    message.chat_id,
                    filename,
                    caption=self.strings["done"],
                    reply_to=message.id,
                    attributes=(
                        [utils.get_audio_tag(filename, title=track_name, performer=artists)]
                        if hasattr(utils, "get_audio_tag")
                        else []
                    ),
                )

                await message.delete()

                if os.path.exists(filename):
                    os.remove(filename)

        except Exception:
            logger.exception("Download failed")
            await utils.answer(message, self.strings["error"])
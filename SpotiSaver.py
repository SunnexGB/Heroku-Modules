# Спасибо: snfsx, кезу,а так же я убоал слоп.
# requires: httpx
# meta developer: @SunnexGB
# meta repo: https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/refs/heads/main/spotisaver.py
# meta pic: https://r2.fakecrime.bio/uploads/ddf03169-09fe-4eb1-8eea-bad1a4cc4ada.jpg
# meta banner: https://r2.fakecrime.bio/uploads/ddf03169-09fe-4eb1-8eea-bad1a4cc4ada.jpg
# meta fhsdesc: Spotify, downloader, music, музыка, спотифай,скачать музыку
# это не должно было быть в релизе,но ладно я потом пофикшу все и вся в говнокоде.
__version__ = (1, 1, 1)
# no_ml

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
    "Origin": "https://spotyloader.com",
    "Referer": "https://spotyloader.com/",
}

@loader.tds
class SpotiSaver(loader.Module):
    """Downloading music from Spotify"""
    strings = {
        "name": "SpotiSaver",
        # "args": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> link to song is not specified</b>",
        "downloading": "<b><tg-emoji emoji-id=5443127283898405358>📥</tg-emoji> Downloading:</b> <code>{}</code>",
        "error": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> Error, see logs!</b>",
        "done": "<b><tg-emoji emoji-id=5206607081334906820>✔️</tg-emoji> Done!</b>",
        "no_spotifymod": "<tg-emoji emoji-id=5431402435497181911>💢</tg-emoji> <b>SpotifyMod not found.</b>",
        "no_spotify": "<tg-emoji emoji-id=5429164207780152924>😅</tg-emoji> <b>Nothing is playing on Spotify.</b>",
        "nf_id": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> ID key not found!</b>",
        "nf_track": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> Song not found.</b>",
        "timeout": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> timeout! Try again.</b>",
    }

    strings_ru = {
        "name": "SpotiSaver",
        "_cls_doc": "Скачивание музыки из Spotify",
        # "args": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> link to song is not specified</b>",
        "downloading": "<b><tg-emoji emoji-id=5443127283898405358>📥</tg-emoji> Скачиваю:</b> <code>{}</code>",
        "error": "<b><tg-emoji emoji-id=5210952531676504517>❌</tg-emoji> Ерорь, смотри логи!</b>",
        "done": "<b><tg-emoji emoji-id=5206607081334906820>✔️</tg-emoji> Готово!</b>",
        "no_spotifymod": "<tg-emoji emoji-id=5431402435497181911>💢</tg-emoji> <b>SpotifyMod не найден.</b>",
        "no_spotify": "<tg-emoji emoji-id=5429164207780152924>😅</tg-emoji> <b>В Spotify ничего не играет.</b>",
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
            ),
            loader.ConfigValue(
                "Attempts",
                15,
                "Count attempts for status request | Кол-во попыток проверки статуса",
                validator=loader.validators.Integer(minimum=1),
            ),
        )
        self.api_url = "https://spotyloader.com/api/spotify"
        self.storage_url = "https://usc1.contabostorage.com/de91f9e22993446b9f80b560103d3e27:tracks/tracks/spotify"

    async def get_current_spotify_url(self) -> str | None:
        spotifymod = self.lookup("SpotifyMod")
        if not spotifymod or not spotifymod.sp:
            return None
        current_playback = await asyncio.to_thread(spotifymod.sp.current_playback)
        if not current_playback or not current_playback.get("is_playing"):
            return None
        track_id = current_playback["item"]["id"]
        return f"https://open.spotify.com/track/{track_id}"

    async def get_track_data(self, client, track_url):
        info_res = await client.get(
            f"{self.api_url}/info",
            params={"url": track_url},
            headers=headers,
            timeout=self.config["TimeOut"],
        )
        info = info_res.json()
        post_data = info.get("post", {})
        track_name = post_data.get("name", "").strip()
        artists = post_data.get("artist", "").strip()
        if artists and track_name:
            full_name = track_name if artists.lower() in track_name.lower() else f"{artists} - {track_name}"
        else:
            full_name = track_name or artists
        return full_name, track_name, artists

    async def get_song_info(self, client, track_id, task_id):
        download_url = f"{self.storage_url}/{track_id}/m4a.m4a"
        for _ in range(self.config["Attempts"]):
            try:
                head_res = await client.head(download_url, timeout=5)
                if head_res.status_code == 200:
                    return download_url
            except Exception:
                pass
            if task_id:
                try:
                    status_res = await client.get(
                        f"{self.api_url}/track/status/{task_id}",
                        headers=headers,
                        timeout=self.config["TimeOut"],
                    )
                    status = status_res.json()
                    state = str(status.get("status") or status.get("state") or "").lower()
                    if state in ("completed", "success", "done", "ready") or status.get("url"):
                        return status.get("url") or download_url
                except Exception:
                    pass
            await asyncio.sleep(2)
        return None

    @loader.command(ru_doc="<ссылка> — Скачать трек из Spotify")
    async def spotsave(self, message: Message):
        """<link> - Download track from Spotify"""
        args = utils.get_args_raw(message)
        if not args:
            spotifymod = self.lookup("SpotifyMod")
            if not spotifymod or not spotifymod.sp:
                return await utils.answer(message, self.strings["no_spotifymod"])
            args = await self.get_current_spotify_url()
            if not args:
                return await utils.answer(message, self.strings["no_spotify"])
        if "track/" not in args:
            return await utils.answer(message, self.strings["nf_id"])
        track_url = args.split("?")[0]
        track_id = track_url.split("track/")[1]
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                full_name, track_name, artists = await self.get_track_data(client, track_url)
                if not track_name:
                    return await utils.answer(message, self.strings["nf_track"])
                conv_res = await client.post(
                    f"{self.api_url}/track",
                    headers=headers,
                    json={"url": track_url, "format": "m4a"},
                    timeout=self.config["TimeOut"],
                )
                conv = conv_res.json()
                task_id = conv.get("jobId") or conv.get("id") or conv.get("taskId")
                await utils.answer(
                    message,
                    self.strings["downloading"].format(utils.escape_html(full_name)),
                )
                download_url = await self.get_song_info(client, track_id, task_id)
                if not download_url:
                    return await utils.answer(message, self.strings["timeout"])
                file_res = await client.get(
                    download_url,
                    headers={"User-Agent": headers["User-Agent"]},
                    timeout=self.config["TimeOut"],
                )
                song_name = re.sub(r'[\\/*?:"<>|]', "", full_name).strip()
                filename = f"{song_name}.m4a"
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
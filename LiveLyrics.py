# meta developer: @SunnexGB
# requires: aiohttp
# meta pic: https://r2.fakecrime.bio/uploads/6725e5a0-0c9e-48ed-be85-dfd857c2aa5f.jpg
# meta banner: https://r2.fakecrime.bio/uploads/6725e5a0-0c9e-48ed-be85-dfd857c2aa5f.jpg
# meta fhsdesc: Spotify, YaMusic, music, музыка, Lyrics, слова, текст, трек, песня

from herokutl.types import Message
from .. import loader, utils
from ..types import InlineCall
import aiohttp
import asyncio
import re

@loader.tds
class LiveLyrics(loader.Module):
    """life lyrics current song"""

    strings = {
        "name": "LiveLyrics",
        "no_spotifymod": "<tg-emoji emoji-id=5431402435497181911>💢</tg-emoji> <b>SpotifyMod not found,but u can install it. You can also support developer: </b> @ke_mods",
        "no_yamusic": "<tg-emoji emoji-id=5431402435497181911>💢</tg-emoji> <b>YaMusicMod not found,but u can install it. You can also support developer: </b> @codrago_m",
        "no_auth_spotify": "<tg-emoji emoji-id=5429225166250984904>⁉️</tg-emoji><b> You not authorized in SpotifyMod, visit you Saved Messages.</b>",
        "no_auth_yamusic": "<tg-emoji emoji-id=5429225166250984904>⁉️</tg-emoji><b> You not authorized in SpotifyMod, visit you Saved Messages and setup token to continue.</b>",
        "no_spotify": "<tg-emoji emoji-id=5429164207780152924>😅</tg-emoji> <b>Nothing is playing on Spotify.</b>",
        "no_ym": "<tg-emoji emoji-id=5429164207780152924>😅</tg-emoji> <b>Nothing is playing on YaMusic.</b>",
        "no_lyrics": "<tg-emoji emoji-id=5431402435497181911>💢</tg-emoji> <b>Lyrics not found for:</b> <code>{}</code>",
        "not_synced": "<i><tg-emoji emoji-id=5431445849026611010>⚠️</tg-emoji> Lyrics are not synchronized.</i>\n\n",
        "TrackEnded": "<tg-emoji emoji-id=5429638011392377649>‼️</tg-emoji> Playback ended or track changed.",
        "header": "<tg-emoji emoji-id=5429413328768224565>🎤</tg-emoji> <b>{} - {}</b>\n\n",
        "timeout": "<b><tg-emoji emoji-id=5429455831764584284>⏳</tg-emoji></b><b> Oopsi, looks like we've got a timeout here</b>.",
        "yamusic_installed": "YaMusic installed!",
        "spotify_installed": "SpotifyMod installed!",
        "song_link": "🔗 song.link",
        "close": "❌ Close",
        "ok": "OK",
    }

    strings_ru = {
        "_cls_doc": "Лайв слова текущей песни.",
        "no_spotifymod": "<tg-emoji emoji-id=5431402435497181911>💢</tg-emoji> <b>SpotifyMod не найден,но его можно установить. Вы также можете поддержать разработчика: </b> @ke_mods",
        "no_yamusic": "<tg-emoji emoji-id=5431402435497181911>💢</tg-emoji> <b>YaMusicMod не найден, но его можно установить. Вы также можете поддержать разработчика: </b> @codrago_m",
        "no_auth_spotify": "<tg-emoji emoji-id=5429225166250984904>⁉️</tg-emoji> <b>Вы не авторизованы в SpotifyMod. Перейдите в Избранное.</b>",
        "no_auth_yamusic": "<tg-emoji emoji-id=5429225166250984904>⁉️</tg-emoji><b> Вы не авторизированы в YaMusicMod, перейдите в Избранное и установите токен для продолжения работы.</b>",
        "no_spotify": "<tg-emoji emoji-id=5429164207780152924>😅</tg-emoji> <b>В Spotify ничего не играет.</b>",
        "no_ym": "<tg-emoji emoji-id=5429164207780152924>😅</tg-emoji> <b>В YaMusic ничего не играет.</b>",
        "no_lyrics": "<tg-emoji emoji-id=5431402435497181911>💢</tg-emoji> <b>Текст не найден для:</b> <code>{}</code>",
        "not_synced": "<i><tg-emoji emoji-id=5431445849026611010>⚠️</tg-emoji> Текст не синхронизирован.</i>\n\n",
        "TrackEnded": "<tg-emoji emoji-id=5429638011392377649>‼️</tg-emoji> Воспроизведение завершено или трек сменился.",
        "header": "<tg-emoji emoji-id=5429413328768224565>🎤</tg-emoji> <b>{} - {}</b>\n\n",
        "timeout": "<b><tg-emoji emoji-id=5429455831764584284>⏳</tg-emoji></b><b> Упси, похоже кто то словил таймаут.</b>.",
        "yamusic_installed": "YaMusic Установлен!",
        "spotify_installed": "SpotifyMod Установлен!",
        "song_link": "🔗 song.link",
        "close": "❌ Закрыть",
        "ok": "OK",
    }

    def __init__(self):
        self._active_tasks: dict = {}
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "emoji_current",
                "<tg-emoji emoji-id='5215679757366089921'>🤯</tg-emoji>",
                "Emoji for the current line",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "dot",
                "♪",
                "instrumental_emoji or text",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "text_lines",
                "6",
                "Count lines in message, with synchronized text",
                validator=loader.validators.Integer(),
            ),
            loader.ConfigValue(
                "lyrics_delay",
                0.5,
                "delay in switching to a new timing sector with words",
            ),
            loader.ConfigValue(
                "request_timeout",
                12,
                "timeout value",
                validator=loader.validators.Integer(),
            ),
        )

    async def install_mod(self, call: InlineCall, heroku_module: str):
        if heroku_module == "SpotifyMod":
            download_url = "https://raw.githubusercontent.com/radiocycle/Modules/refs/heads/master/SpotifyMod.py"
            module_name = "SpotifyMod"
            installed_btn = self.strings["spotify_installed"]
            no_auth_str = self.strings["no_auth_spotify"]
            auth_command = "sauth"
        else:
            download_url = "https://raw.githubusercontent.com/coddrago/modules/main/YaMusic.py"
            module_name = "YaMusic"
            installed_btn = self.strings["yamusic_installed"]
            no_auth_str = self.strings["no_auth_yamusic"]
            auth_command = "yguide"
        try:
            m = self.lookup("loader")
            await m.download_and_install(download_url)
            await call.answer(installed_btn, show_alert=True)
            mod = self.lookup(module_name)
            if heroku_module == "SpotifyMod":
                authorized = mod and mod.get("acs_tkn")
            else:
                authorized = mod and mod.get("__config__")["token"]
            if not authorized:
                await self.invoke(auth_command, " ", "me")
                await call.edit(
                    no_auth_str,
                    reply_markup=[
                        [
                            {"text": self.strings["ok"], "callback": self.close}
                        ]
                    ],
                )
            else:
                await call.delete()
        except Exception as e:
            await call.answer(f"Error: {e}", show_alert=True)

    def close(self, call: InlineCall):
        return call.delete()

    async def get_lyrics(self, artist: str, track: str):
        ClearTimeSections = re.sub(r"\(.*?\)|\[.*?\]", "", track).strip()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://lrclib.net/api/search",
                    params={"track_name": ClearTimeSections, "artist_name": artist},
                    timeout=aiohttp.ClientTimeout(total=self.config["request_timeout"]),
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result[0] if result else None
        except asyncio.TimeoutError:
            return {"timeout": True}
        except Exception:
            pass
        return None

    def parse_synced(self, synced_text: str) -> list:
        lines = []
        for line in synced_text.split("\n"):
            m = re.search(r"\[(\d+):(\d+\.\d+)\](.*)", line)
            if m:
                mins, secs, text = m.groups()
                lines.append({
                    "time": (int(mins) * 60 + float(secs)) * 1000,
                    "text": text.strip(),
                })
        return lines

    def build_lyrics(self, artist, track, lines, plain, progress_ms, not_synced_str):
        header = self.strings["header"].format(
            utils.escape_html(artist),
            utils.escape_html(track),
        )
        if lines:
            curr_idx = 0
            for i, line in enumerate(lines):
                if progress_ms >= line["time"]:
                    curr_idx = i
            l_start = max(0, curr_idx - 1)
            l_end = min(len(lines), l_start + self.config["text_lines"])
            rows = []
            for i in range(l_start, l_end):
                t = lines[i]["text"] or self.config["dot"]
                if i == curr_idx:
                    rows.append(f"<b>{self.config['emoji_current']} {utils.escape_html(t)}</b>")
                else:
                    rows.append(f"<code>{utils.escape_html(t)}</code>")
            return header + "\n".join(rows)
        return header + not_synced_str + f"<blockquote expandable>{utils.escape_html((plain or '')[:4000])}</blockquote>"

    def build_keyboard(self, song_url):
        return [
            [
                {"text": self.strings["song_link"], "url": song_url}
            ],
            [
                {"text": self.strings["close"], "callback": self.close_cb}
            ],
        ]

    async def close_cb(self, call: InlineCall):
        for track_id, task in list(self._active_tasks.items()):
            task.cancel()
            self._active_tasks.pop(track_id, None)
        try:
            await call.answer()
            await call.delete()
        except Exception:
            pass

    async def za_loop_a(self, form, mod, track_id, artist_name, track_name, song_url, lines, plain, not_synced_str, heroku_module: str):
        buffer_clipboard = ""
        try:
            while True:
                if heroku_module == "SpotifyMod":
                    pb = mod.sp.current_playback()
                    TrackEnded = not pb or not pb.get("item") or pb["item"]["id"] != track_id
                else:
                    pb = await mod._YaMusicMod__get_now_playing()
                    TrackEnded = not pb or not pb.get("track") or pb["track"]["track_id"] != track_id
                if TrackEnded:
                    try:
                        await form.edit(
                            self.strings["TrackEnded"],
                            reply_markup=[[{"text": self.strings["close"], "callback": self.close_cb}]],
                        )
                    except Exception:
                        pass
                    break
                prog = pb.get("progress_ms", 0)
                content = self.build_lyrics(artist_name, track_name, lines, plain, prog, not_synced_str)
                if content != buffer_clipboard:
                    try:
                        await form.edit(content, reply_markup=self.build_keyboard(song_url)) 
                        buffer_clipboard = content
                    except Exception:
                        break
                if not lines:
                    break
                await asyncio.sleep(self.config["lyrics_delay"])
        except asyncio.CancelledError:
            raise
        except Exception:
            pass
        finally:
            self._active_tasks.pop(track_id, None)

    @loader.command(ru_doc="- показать синхронизированный текст песни")
    async def snowlcmd(self, message: Message):
        """- show synchronized lyrics for current track"""
        mod = self.lookup("SpotifyMod")
        if not mod:
            form = await self.inline.form("⏳", message=message)
            await form.edit(
                self.strings["no_spotifymod"],
                reply_markup=[
                    [
                    {
                        "text": self.strings["spotify_installed"], 
                        "callback": self.install_mod, 
                        "kwargs": {"heroku_module": "SpotifyMod"}
                    }
                ]
            ],
            )
            return
        if not mod.get("acs_tkn"):
            await self.invoke("sauth", " ", "me")
            form = await self.inline.form("⏳", message=message)
            await form.edit(
                self.strings["no_auth_spotify"],
                reply_markup=[[{"text": self.strings["ok"], "callback": self.close}]],
            )
            return

        playback = mod.sp.current_playback()
        if not playback or not playback.get("item"):
            return await utils.answer(message, self.strings["no_spotify"])
        track = playback["item"]
        track_id = track["id"]
        artist_name = track["artists"][0]["name"]
        track_name = track["name"]
        song_url = f"https://song.link/s/{track_id}"

        old = self._active_tasks.pop(track_id, None)
        if old:
            old.cancel()

        data = await self.get_lyrics(artist_name, track_name)
        if data and data.get("timeout"):
            return await utils.answer(message, self.strings["timeout"])
        if not data or data.get("instrumental"):
            return await utils.answer(
                message,
                self.strings["no_lyrics"].format(f"{utils.escape_html(track_name)} - {utils.escape_html(artist_name)}"),
            )

        synced_raw = data.get("syncedLyrics")
        plain = data.get("plainLyrics", "")
        lines = self.parse_synced(synced_raw) if synced_raw else []
        not_synced_str = self.strings["not_synced"]
        form = await self.inline.form(
            text=self.build_lyrics(artist_name, track_name, lines, plain, playback.get("progress_ms", 0), not_synced_str),
            message=message,
            reply_markup=self.build_keyboard(song_url),
        )

        self._active_tasks[track_id] = asyncio.ensure_future(
            self.za_loop_a(form, mod, track_id, artist_name, track_name, song_url, lines, plain, not_synced_str, heroku_module="SpotifyMod")
        )

    @loader.command(ru_doc="- показать синхронизированный текст песни")
    async def ynowlcmd(self, message: Message):
        """- show synchronized lyrics for current track"""
        mod = self.lookup("YaMusic")
        if not mod:
            form = await self.inline.form("⏳", message=message)
            await form.edit(
                self.strings["no_yamusic"],
                reply_markup=[
                    [
                    {
                        "text": "Install YaMusicMod", 
                        "callback": self.install_mod, 
                        "kwargs": {"heroku_module": "YaMusic"}
                    }
                ]    
            ],
            )
            return
        if not mod.get("__config__")["token"]:
            await self.invoke("yguide", " ", "me")
            form = await self.inline.form("⏳", message=message)
            await form.edit(
                self.strings["no_auth_yamusic"],
                reply_markup=[[{"text": self.strings["ok"], "callback": self.close}]],
            )
            return

        playback = await mod._YaMusicMod__get_now_playing()
        if not playback or not playback.get("track"):
            return await utils.answer(message, self.strings["no_ym"])
        track = playback["track"]
        track_id = track["track_id"]
        artist_name = ", ".join(track["artist"])
        track_name = track["title"]
        song_url = f"https://song.link/s/{track_id}"

        old = self._active_tasks.pop(track_id, None)
        if old:
            old.cancel()

        data = await self.get_lyrics(artist_name, track_name)
        if data and data.get("timeout"):
            return await utils.answer(message, self.strings["timeout"])
        if not data or data.get("instrumental"):
            return await utils.answer(
                message,
                self.strings["no_lyrics"].format(f"{utils.escape_html(track_name)} - {utils.escape_html(artist_name)}"),
            )

        synced_raw = data.get("syncedLyrics")
        plain = data.get("plainLyrics", "")
        lines = self.parse_synced(synced_raw) if synced_raw else []
        not_synced_str = self.strings["not_synced"]

        form = await self.inline.form(
            text=self.build_lyrics(artist_name, track_name, lines, plain, playback.get("progress_ms", 0), not_synced_str),
            message=message,
            reply_markup=self.build_keyboard(song_url),
        )

        self._active_tasks[track_id] = asyncio.ensure_future(
            self.za_loop_a(form, mod, track_id, artist_name, track_name, song_url, lines, plain, not_synced_str, heroku_module="YaMusic")
        )
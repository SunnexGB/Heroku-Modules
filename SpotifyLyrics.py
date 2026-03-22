# meta developer: @SunnexGB
# requires: aiohttp
# meta repo: https://r2.fakecrime.bio/uploads/f49a9294-36ad-4fc4-801f-48cb049111d6.jpg
# meta pic: https://r2.fakecrime.bio/uploads/f49a9294-36ad-4fc4-801f-48cb049111d6.jpg
# meta banner: https://r2.fakecrime.bio/uploads/f49a9294-36ad-4fc4-801f-48cb049111d6.jpg
# meta fhsdesc: Spotify, music, музыка, спотифай,Lyrics, слова, текст, трек, песня
# все же я не знаю трек или сонг, так что пусть будет трек, а не сонг потому что интуитивнее поняттнее,наверное?
# крутой баннер да?
#current version
__version__ = (1, 0, 0)

from herokutl.types import Message
from .. import loader, utils
import aiohttp
import asyncio
import re


@loader.tds
class SpotifyLyrics(loader.Module):
    """life lyrics current song"""

    strings = {
        "name": "SpotifyLyrics",
        "no_spotifymod": "<tg-emoji emoji-id=5431402435497181911>💢</tg-emoji> <b>SpotifyMod not found.</b>",
        "no_spotify": "<tg-emoji emoji-id=5429164207780152924>😅</tg-emoji> <b>Nothing is playing on Spotify.</b>",
        "no_lyrics": "<tg-emoji emoji-id=5431402435497181911>💢</tg-emoji> <b>Lyrics not found for:</b> <code>{}</code>",
        "not_synced": "<i><tg-emoji emoji-id=5431445849026611010>⚠️</tg-emoji> Lyrics are not synchronized.</i>\n\n",
        "finished": "<tg-emoji emoji-id=5429638011392377649>‼️</tg-emoji> Playback ended or track changed.",
        "header": "<tg-emoji emoji-id=5429413328768224565>🎤</tg-emoji> <b>{} - {}</b>\n\n",
        "dot": "···",
    }

    strings_ru = {
        "cls_doc": "Лайв слова текущей песни песни",
        "no_spotifymod": "<tg-emoji emoji-id=5431402435497181911>💢</tg-emoji> <b>SpotifyMod не найден.</b>",
        "no_spotify": "<tg-emoji emoji-id=5429164207780152924>😅</tg-emoji> <b>В Spotify ничего не играет.</b>",
        "no_lyrics": "<tg-emoji emoji-id=5431402435497181911>💢</tg-emoji> <b>Текст не найден для:</b> <code>{}</code>",
        "not_synced": "<i><tg-emoji emoji-id=5431445849026611010>⚠️</tg-emoji> Текст не синхронизирован.</i>\n\n",
        "finished": "<tg-emoji emoji-id=5429638011392377649>‼️</tg-emoji> Воспроизведение завершено или трек сменился.",
        "header": "<tg-emoji emoji-id=5429413328768224565>🎤</tg-emoji> <b>{} - {}</b>\n\n",
        "dot": "···",
    }

    def __init__(self):
        self._active_tasks: dict = {}
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "emoji_current",
                "<tg-emoji emoji-id='5215679757366089921'>🤯</tg-emoji>",
                "Emoji for current line",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "lyrics_delay",
                0.5,
                "delay in switching to a new timing sector with words",
                validator=loader.validators.Integer(minimum=0.5),
            ),
        )

    async def _get_lyrics(self, artist: str, track: str):
        clean_track = re.sub(r"\(.*?\)|\[.*?\]", "", track).strip()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://lrclib.net/api/search",
                    params={"track_name": clean_track, "artist_name": artist},
                    timeout=aiohttp.ClientTimeout(total=6),
                ) as resp:
                    if resp.status == 200:
                        res = await resp.json()
                        return res[0] if res else None
        except Exception:
            pass
        return None

    def _parse_synced(self, synced_text: str) -> list:
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

    def _build_content(self, artist, track, lines, plain, progress_ms, not_synced_str):
        header = self.strings("header").format(
            utils.escape_html(artist),
            utils.escape_html(track),
        )
        if lines:
            curr_idx = 0
            for i, line in enumerate(lines):
                if progress_ms >= line["time"]:
                    curr_idx = i
            win_start = max(0, curr_idx - 1)
            win_end = min(len(lines), curr_idx + 6)
            rows = []
            for i in range(win_start, win_end):
                t = lines[i]["text"] or self.strings("dot")
                if i == curr_idx:
                    rows.append(
                        f"<b>{self.config['emoji_current']} {utils.escape_html(t)}</b>"
                    )
                else:
                    rows.append(f"<code>{utils.escape_html(t)}</code>")
            return header + "\n".join(rows)
        else:
            return header + not_synced_str + f"<code>{utils.escape_html((plain or '')[:600])}</code>"

    def _markup(self, song_url):
        return [
            [{"text": "🔗 song.link", "url": song_url}],
            [{"text": "❌ Close", "callback": self._close_cb}],
        ]

    async def _close_cb(self, call):
        for track_id, task in list(self._active_tasks.items()):
            task.cancel()
            self._active_tasks.pop(track_id, None)
        try:
            await call.answer()
            await call.delete()
        except Exception:
            pass

    async def run_loop(self, form, mod, track_id, artist_name, track_name, song_url, lines, plain, not_synced_str):
        last_display = ""
        try:
            while True:
                pb = mod.sp.current_playback()
                if not pb or not pb.get("item") or pb["item"]["id"] != track_id:
                    try:
                        await form.edit(
                            self.strings("finished"),
                            reply_markup=[[{"text": "❌ Close", "callback": self._close_cb}]],
                        )
                    except Exception:
                        pass
                    break

                prog = pb.get("progress_ms", 0)
                content = self._build_content(
                    artist_name, track_name, lines, plain, prog, not_synced_str
                )

                if content != last_display:
                    try:
                        await form.edit(content, reply_markup=self._markup(song_url))
                        last_display = content
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
        """- show synchronized lyrics for current Spotify track"""
        mod = self.lookup("SpotifyMod")
        if not mod or not hasattr(mod, "sp") or not mod.sp:
            return await utils.answer(message, self.strings("no_spotifymod"))

        playback = mod.sp.current_playback()
        if not playback or not playback.get("item"):
            return await utils.answer(message, self.strings("no_spotify"))

        track = playback["item"]
        track_id = track["id"]
        artist_name = track["artists"][0]["name"]
        track_name = track["name"]
        song_url = f"https://song.link/s/{track_id}"

        old = self._active_tasks.pop(track_id, None)
        if old:
            old.cancel()

        data = await self._get_lyrics(artist_name, track_name)
        if not data or data.get("instrumental"):
            return await utils.answer(
                message,
                self.strings("no_lyrics").format(utils.escape_html(track_name)),
            )

        synced_raw = data.get("syncedLyrics")
        plain = data.get("plainLyrics", "")

        lines = self._parse_synced(synced_raw) if synced_raw else []
        not_synced_str = self.strings("not_synced")

        prog = playback.get("progress_ms", 0)
        initial_content = self._build_content(
            artist_name, track_name, lines, plain, prog, not_synced_str
        )

        form = await self.inline.form(
            text=initial_content,
            message=message,
            reply_markup=self._markup(song_url),
        )

        task = asyncio.ensure_future(
            self.run_loop(
                form=form,
                mod=mod,
                track_id=track_id,
                artist_name=artist_name,
                track_name=track_name,
                song_url=song_url,
                lines=lines,
                plain=plain,
                not_synced_str=not_synced_str,
            )
        )
        self._active_tasks[track_id] = task
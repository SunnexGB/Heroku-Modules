# meta developer: @H_SunMods
# meta banner: https://r2.fakecrime.bio/uploads/7103b4ca-5fb1-4512-8a70-e720780c29c8.jpg
# current ver
__version__ = (1, 0, 0)

import logging
from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class spotifyph(loader.Module):
    
    strings = {
        "name": "spotify_ph",
        "start_duration": "<tg-emoji emoji-id=5386793861483894694>🎶</tg-emoji><tg-emoji emoji-id=5384507693341906264>🎶</tg-emoji>",
        "start_full_duration": "<tg-emoji emoji-id=5386793861483894694>🎶</tg-emoji><tg-emoji emoji-id=5384401375721463792>🎶</tg-emoji>",
        "mid_duration": "<tg-emoji emoji-id=5386623003389888935>🎶</tg-emoji>",
        "empty_mid": "<tg-emoji emoji-id=5384267235302870604>🎶</tg-emoji>",
        "end_duration": "<tg-emoji emoji-id=5386826786703186322>🎶</tg-emoji>",
        "end_duration_full": "<tg-emoji emoji-id=5386623003389888935>🎶</tg-emoji>",
        "empty_end": "<tg-emoji emoji-id=5386826786703186322>🎶</tg-emoji>",
        "no_prem_start_duration": "ᵔᴥᵔ [---",
        "no_prem_start_full_duration": "ᵔᴥᵔ [~~~",
        "no_prem_mid_duration": "~~~",
        "no_prem_empty_mid": "---",
        "no_prem_end_duration_full": "~~~]",
        "no_prem_empty_end": "---]",
        "not_installed": "<b>SpotifyMod is not installed</b>",
        "nothing_plays": "<b>Nothing plays</b>",
        "sp_duration_desc": "Progress bar (SpotifyMod)",
        "sp_track_desc": "Show artist and song (SpotifyMod)",
        "err": "<b>Error`</b>"
    }

    async def client_ready(self, client, db):
        self._client = client
        utils.register_placeholder("sp_duration", self.sp_duration, self.strings("sp_duration_desc"))
        utils.register_placeholder("sp_track", self.get_sp_track, self.strings("sp_track_desc"))

    def __init__(self):
            self.config = loader.ModuleConfig(
                loader.ConfigValue(
                    "show_text_time",
                    True,
                    "show text time",
                    validator=loader.validators.Boolean(),
                )
            )

    async def get_sp_track(self):
        try:
            s = self.lookup("SpotifyMod")
            if not s or not s.sp:
                return self.strings("not_installed")
            
            p = s.sp.current_user_playing_track()
            if not (p and p.get('item')):
                return self.strings("nothing_plays")

            artist = p['item']['artists'][0]['name']
            track_name = p['item']['name']
            return utils.escape_html(f"{artist} — {track_name}")
        except Exception as e:
            logger.error(f"Error in sp_track: {e}")
            return self.strings("err")

    async def sp_duration(self):
        s = self.lookup("SpotifyMod")
        if not s or not s.sp:
            return self.strings("not_installed")

        playback = s.sp.current_playback()
        if not playback or not playback.get("item"):
            return self.strings("nothing_plays")

        prog_ms = playback.get("progress_ms", 0)
        dur_ms = playback["item"].get("duration_ms", 0)
        
        if dur_ms == 0:
            return "00:00 / 00:00"

        percent = (prog_ms / dur_ms) * 100
        filled_units = int(percent // 16.66)

        # Логика для нищих
        user = getattr(self._client, "heroku_me", getattr(self._client, "me", None))
        is_premium = getattr(user, "premium", False)
        pref = "" if is_premium else "no_prem_"

        if filled_units >= 1:
            start_pos = f"{pref}start_full_duration"
        else:
            start_pos = f"{pref}start_duration"
        bar = self.strings(start_pos)

        for i in range(2, 6):
            if filled_units >= i:
                mid_pos = f"{pref}mid_duration"
            else:
                mid_pos = f"{pref}empty_mid"
            bar += self.strings(mid_pos)
        
        if filled_units >= 6:
            end_key = f"{pref}end_duration_full"
        else:
            end_key = f"{pref}empty_end"
        bar += self.strings(end_key)

        if self.config["show_text_time"]:
            prog_t = f"{prog_ms//60000:02}:{(prog_ms//1000)%60:02}"
            dur_t = f"{dur_ms//60000:02}:{(dur_ms//1000)%60:02}"
            return f"{bar} <code>{prog_t} / {dur_t}</code>"
        return bar
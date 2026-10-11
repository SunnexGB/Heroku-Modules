# Based on telegram-id-age-research by sepiol026-wq
# https://github.com/sepiol026-wq/telegram-id-age-research
# Copyright (C) sepiol026-wq

# Modified: adapted for heroku module, 2026-10-11
# See https://www.gnu.org/licenses/agpl-3.0.html

#meta banner: https://r2.fakecrime.bio/uploads/a7ab74ea-dc88-439d-868d-3804778f0cd9.jpg
#meta pic: https://r2.fakecrime.bio/uploads/a7ab74ea-dc88-439d-868d-3804778f0cd9.jpg
# meta fhsdesc: Узнать id, Узнать ид, дата регистрации
# meta developer: @H_SunMods

from herokutl.types import Message
from .. import loader, utils

@loader.tds
class Datereg(loader.Module):
    strings = {
        "name": "Datereg",
        "_cls_doc": "Show estimates registration date.",
        "usage": "<emoji document_id=5210952531676504517>❌</emoji> <b>Reply to user or specify ID / @username</b>",
        "not_found": "<emoji document_id=5210952531676504517>❌</emoji> <b>User not found</b>",
        "check_id": "Check ID",
        "report": (
            "<tg-emoji emoji-id=5359316344351270996>🫤</tg-emoji> <b>Telegram account age</b>\n\n"
            "<b>{name}</b>"
            "<tg-emoji emoji-id=5226513232549664618>🔢</tg-emoji> ID: <code>{user_id}</code>\n"
            "<tg-emoji emoji-id=5258105663359294787>🗓</tg-emoji> Estimated registration: <b>{date}</b>\n"
            "<tg-emoji emoji-id=5258419835922030550>🕔</tg-emoji> Estimated age: <b>{age}</b>\n\n"
            "<tg-emoji emoji-id=5258503720928288433>ℹ️</tg-emoji> Estimated range: {min_date} – {max_date}\n"
            "Uncertainty: ±{days} {days_unit}."
        ),
        "years": "year|years",
        "months": "month|months",
        "days": "day|days",
        "inline_title": "Enter ID or @username",
        'inline_desc': "@username / ID",
        "inline_result": "Registration date",
    }

    strings_ru = {
        "_cls_doc": "Показывает примерную дату создания аккаунта.",
        "usage": "<emoji document_id=5210952531676504517>❌</emoji> <b>Ответьте на сообщение пользователя или укажите ID / @username</b>",
        "not_found": "<emoji document_id=5210952531676504517>❌</emoji> <b>Пользователь не найден</b>",
        "check_id": "Проверить ID",
        "report": (
            "<tg-emoji emoji-id=5359316344351270996>🫤</tg-emoji> <b>Возраст Telegram аккаунта</b>\n\n"
            "<b>{name}</b>"
            "<tg-emoji emoji-id=5226513232549664618>🔢</tg-emoji> ID: <code>{user_id}</code>\n"
            "<tg-emoji emoji-id=5258105663359294787>🗓</tg-emoji> Примерная регистрация: <b>{date}</b>\n"
            "<tg-emoji emoji-id=5258419835922030550>🕔</tg-emoji> Примерный возраст: <b>{age}</b>\n\n"
            "<tg-emoji emoji-id=5258503720928288433>ℹ️</tg-emoji> Примерный диапазон: {min_date} - {max_date}\n"
            "Погрешность: ±{days} {days_unit}."
        ),
        "years": "год|года|лет",
        "months": "месяц|месяца|месяцев",
        "days": "день|дня|дней",
        "inline_title": "Введите ID или @username",
        'inline_desc': "@username / ID",
        "inline_result": "Дата регистрации",
    }

    def __init__(self):
        self.lib_link = "https://raw.githubusercontent.com/SunnexGB/telegram-id-age-research/refs/heads/main/datelib.py"
        self.inline_query = "datereg  "
        self.date_format = "%d %b %Y"

    async def client_ready(self, client, db):
        self.datereg_lib = await self.import_lib(
            self.lib_link,
            suspend_on_error=True,
        )

    def get_ending(self, number, key):
        forms = self.strings(key).split("|")
        if len(forms) == 2:
            return forms[0] if number == 1 else forms[1]
        if number % 10 == 1 and number % 100 != 11:
            return forms[0]
        if 2 <= number % 10 <= 4 and not 12 <= number % 100 <= 14:
            return forms[1]
        return forms[2]

    def get_data_placelders(self, user_id, name):
        date, min_date, max_date, days = self.datereg_lib.check(user_id)
        time_period = [
            f"{value} {self.get_ending(value, key)}"
            for value, key in zip(self.datereg_lib.get_age(date), ("years", "months", "days"))
            if value
        ]
        return self.strings("report").format(
            name=f"{name}\n" if name else "",
            user_id=user_id,
            date=date.strftime(self.date_format),
            age=", ".join(time_period) or f"0 {self.get_ending(0, 'days')}",
            min_date=min_date.strftime(self.date_format),
            max_date=max_date.strftime(self.date_format),
            days=days,
            days_unit=self.get_ending(days, "days"),
        )

    async def args_handler(self, strip_id):
        strip_id = str(strip_id).strip().lstrip("@")
        try:
            entity = await self.client.get_entity(int(strip_id) if strip_id.isdigit() else strip_id)
        except Exception:
            if not strip_id.isdigit():
                return None
            entity = None
        if entity is None:
            return self.get_data_placelders(int(strip_id), None)
        username = getattr(entity, "username", None)
        name = f"@{username}" if username else getattr(entity, "first_name", None)
        return self.get_data_placelders(entity.id, utils.escape_html(name) if name else None)
    @loader.command(doc_ru="- ответом / id / @username / узнать дату регестрации аккаунта")
    async def dateregcmd(self, message: Message):
        '''- ответом / id / @username / get account registration date'''
        get_id_raw = utils.get_args_raw(message)
        if not get_id_raw:
            reply = await message.get_reply_message()
            if reply:
                get_id_raw = reply.sender_id
        if not get_id_raw:
            await utils.answer(message, self.strings("usage"))
            return
        msg_get_id_raw = await self.args_handler(get_id_raw)
        if msg_get_id_raw is None:
            await utils.answer(message, self.strings("not_found"))
            return
        await utils.answer(
            message, 
            msg_get_id_raw, 
            reply_markup=[
                {
                    "text": self.strings("check_id"),
                    "switch_inline_query_current_chat": self.inline_query,
                }
            ]
        )

    @loader.inline_handler(doc_ru="узнать дату регестрации через инлайн")
    async def datereg(self, query):
        '''get account registration date via inline'''
        get_id_raw = query.args.strip()
        if not get_id_raw:
            return {
                "title": self.strings("inline_title"),
                "description": self.strings['inline_desc'],
                "message": self.strings("usage"),
            }

        get_handler_data = await self.args_handler(get_id_raw)
        if get_handler_data is None:
            await query.e404()
            return

        return {
            "title": self.strings("inline_result"),
            "description": get_id_raw,
            "message": get_handler_data,
        }
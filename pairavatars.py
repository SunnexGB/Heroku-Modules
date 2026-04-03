# requires: https://files.pythonhosted.org/packages/8c/21/c2bcdd5906101a30244eaffc1b6e6ce71a31bd0742a01eb89e660ebfac2d/pillow-12.2.0.tar.gz
# meta banner: https://i.ibb.co/yFVJ6L5D/pairavs.webp
# meta developer: @SunnexGB
# я хочу красивый баннер,не осуждайте.
# add version
__version__ = (1, 0, 1)

import io
from PIL import Image
from herokutl.types import Message
from .. import loader, utils

@loader.tds
class pairavatars(loader.Module):
    """Create pair avatars"""
    strings = {
        "name": "PairAvatars",
        "no_reply": "<tg-emoji emoji-id=5408830797513784663>🚫</tg-emoji> | <b>Reply to photo!</b>",
        "processing": "<tg-emoji emoji-id=5332695273762223342>💫</tg-emoji> | <b>Processing...</b>",
        "error": "<tg-emoji emoji-id=5409235172979672859>⚠️</tg-emoji> | <b>Error`</b>"
    }

    strings_ru = {
        "_cls_doc": "Создаёт парные авы",
        "no_reply": "<tg-emoji emoji-id=5408830797513784663>🚫</tg-emoji> | <b>Ответь на фото!</b>",
        "processing": "<tg-emoji emoji-id=5332695273762223342>💫</tg-emoji> | <b>Обработка...</b>",
        "error": "<tg-emoji emoji-id=5409235172979672859>⚠️</tg-emoji> | <b>Еррорь</b>"
    }

    @loader.command(ru_doc="- Создать парные аватарки (команда работает ТОЛЬКО ответом на сообщение)", only_reply=True)
    async def pairavs(self, message: Message):
        """- Create pair avatars (command work ONLY reply message)"""
        reply = await message.get_reply_message()
        processing_msg = await utils.answer(message, self.strings["processing"])
        try:
            tmp_data = await message.client.download_media(reply.photo, bytes)
            img = Image.open(io.BytesIO(tmp_data))
            w, h = img.size
            center = w // 2
            left_part = img.crop((0, 0, center, h))
            right_part = img.crop((center, 0, w, h))
            out_left, out_right = io.BytesIO(), io.BytesIO()
            left_part.save(out_left, "JPEG", quality=100)
            right_part.save(out_right, "JPEG", quality=100)
            out_left.name, out_right.name = "left.jpg", "right.jpg"
            out_left.seek(0)
            out_right.seek(0)

            await message.client.send_file(
                message.chat_id,
                [out_left, out_right],
                reply_to=reply.id
            )

            await processing_msg.delete()
        except Exception:
            await utils.answer(processing_msg, self.strings["error"])
import asyncio
import secrets
from herokutl import events
from herokutl.tl.types import (
    InputBotInlineResult,
    InputBotInlineMessageRichMessage,
    InputRichMessageMarkdown,
    InputRichMessageHTML,
    InputRichMessage,
    InputReplyToMessage,
)
from herokutl.tl.functions.messages import SendMessageRequest
from .. import loader


class RichMsgLib(loader.Library):
    developer = "@SunnexGB"

    def __init__(self):
        self.active_processes = []

    # держу в курсе,это писал не я,но это вроде работает,если у вас есть нормальный способ сделать рвоно тоже самое,то жду RP
    def send_topic(self, message):
        reply = getattr(message, "reply_to", None)
        if reply and getattr(reply, "forum_topic", False):
            return reply.reply_to_top_id or reply.reply_to_msg_id
        return None

    async def send_myself(self, client, chat_id, rich_message, reply_to=None):
        return await client(SendMessageRequest(
            peer=chat_id,
            message="1",
            rich_message=rich_message,
            reply_to=(
                InputReplyToMessage(reply_to_msg_id=reply_to, top_msg_id=reply_to)
                if reply_to else None
            ),
        ))

    async def send_inline(self, client, inline, chat_id, rich_message, reply_to=None):
        bot = inline.bot
        # я тут осознал что если она будет использоваться в нескольких модулях,то будут конфликты,поэтому нужно юзать secrets
        # или не будет конфликтов,аэ ну просто перестраховка.
        key = "r_m_l_" + secrets.token_hex(8)

        async def rich_event_handler(event):
            if event.text != key:
                return
            await event.answer([
                InputBotInlineResult(
                    id="1",
                    type="article",
                    title="Rich Message Lib",
                    send_message=InputBotInlineMessageRichMessage(rich_message=rich_message),
                ),
            ])

        bot.add_event_handler(rich_event_handler, events.InlineQuery())
        self.active_processes.append(rich_event_handler)
        try:
            get_me = await bot.get_me()
            results = await asyncio.wait_for(
                client.inline_query(get_me.username, key, entity=chat_id),
                timeout=10,
            )
            if results:
                return await results[0].click(chat_id, reply_to=reply_to)
        finally:
            bot.remove_event_handler(rich_event_handler, events.InlineQuery())
            if rich_event_handler in self.active_processes:
                self.active_processes.remove(rich_event_handler)

    async def r_msg(
        self,
        client,
        inline,
        chat_id,
        r_message,
        parse_mode="body", # markdown / html / body
        rich_mode="auto", # auto / self / inline
        rtl=False, # right-to-left хуйня для арабских языков и т п,ее можно будет включить и выключить по желанию.
        noautolink=False, # я хз как обьяснить,но вроде как он отключает обворачивание в html линк теги.
        reply_to=None,
    ):
        
        if parse_mode == "markdown":
            rich_message = InputRichMessageMarkdown(markdown=r_message, rtl=rtl, noautolink=noautolink)
        elif parse_mode == "html":
            rich_message = InputRichMessageHTML(html=r_message, rtl=rtl, noautolink=noautolink)
        else:
            rich_message = InputRichMessage(blocks=r_message, rtl=rtl, noautolink=noautolink)
        if rich_mode == "auto":
            rich_mode = "self" if client.heroku_me.premium else "inline" # нужно для проверки на премиум
        if rich_mode == "self":
            return await self.send_myself(client, chat_id, rich_message, reply_to=reply_to)
        return await self.send_inline(client, inline, chat_id, rich_message, reply_to=reply_to)

    async def cleanup(self, inline):
        bot = inline.bot
        for handler in self.active_processes:
            bot.remove_event_handler(handler, events.InlineQuery())
        self.active_processes.clear()
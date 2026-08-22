# version: 2.1.0
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
    InputSendMessageRichMessageDraftAction, 
)
from herokutl.tl.functions.messages import (
    SendMessageRequest,
    EditMessageRequest,
    EditInlineBotMessageRequest,
    SaveDraftRequest,
    GetRichMessageRequest,
    TranslateRichMessageRequest, 
    ComposeRichMessageWithAIRequest, 
    SetTypingRequest,
)
from herokutl.tl.functions.ephemeral import SendMessageRequest as SendEphemeralMessageRequest 
from .. import loader


rich_text_html = {
    "TextEmpty": lambda t: "",
    "TextPlain": lambda t: t.text,
    "TextConcat": lambda t: "".join(in_rich_text(x) for x in t.texts),
    "TextBold": lambda t: f"<b>{in_rich_text(t.text)}</b>",
    "TextItalic": lambda t: f"<i>{in_rich_text(t.text)}</i>",
    "TextUnderline": lambda t: f"<u>{in_rich_text(t.text)}</u>",
    "TextStrike": lambda t: f"<s>{in_rich_text(t.text)}</s>",
    "TextFixed": lambda t: f"<code>{in_rich_text(t.text)}</code>",
    "TextUrl": lambda t: f'<a href="{t.url}">{in_rich_text(t.text)}</a>',
    "TextSubscript": lambda t: f"<sub>{in_rich_text(t.text)}</sub>",
    "TextSuperscript": lambda t: f"<sup>{in_rich_text(t.text)}</sup>",
    "TextMarked": lambda t: f"<mark>{in_rich_text(t.text)}</mark>",
}

def in_rich_text(text_obj):
    if text_obj is None:
        return ""
    cls = type(text_obj).__name__
    renderer = rich_text_html.get(cls)
    if renderer:
        return renderer(text_obj)
    return in_rich_text(getattr(text_obj, "text", None)) or ""


def caption_logic(caption):
    if caption is None:
        return ""
    text = in_rich_text(getattr(caption, "text", None))
    credit = in_rich_text(getattr(caption, "credit", None))
    if credit:
        return f"<p>{text}<cite>{credit}</cite></p>" if text else f"<p><cite>{credit}</cite></p>"
    return f"<p>{text}</p>" if text else ""

def table_row(row):
    cells = []
    for cell in row.cells:
        tag = "th" if getattr(cell, "header", False) else "td"
        attrs = ""
        if getattr(cell, "colspan", None):
            attrs += f' colspan="{cell.colspan}"'
        if getattr(cell, "rowspan", None):
            attrs += f' rowspan="{cell.rowspan}"'
        if getattr(cell, "align_center", False):
            attrs += ' align="center"'
        elif getattr(cell, "align_right", False):
            attrs += ' align="right"'
        cells.append(f"<{tag}{attrs}>{in_rich_text(cell.text)}</{tag}>")
    return "<tr>" + "".join(cells) + "</tr>"

def list_item(item):
    cls = type(item).__name__
    if cls in ("PageListItemText", "PageListOrderedItemText"):
        text = in_rich_text(item.text)
    elif cls in ("PageListItemBlocks", "PageListOrderedItemBlocks"):
        text = "".join(rich_to_html_handler(b) for b in item.blocks)
    else:
        text = ""
    if getattr(item, "checkbox", False):
        mark = "[x]" if getattr(item, "checked", False) else "[ ]"
        return f"<li>{mark} {text}</li>"
    return f"<li>{text}</li>"

media_tags = {
    "PageBlockPhoto": "img",
    "PageBlockVideo": "video",
    "PageBlockAudio": "audio",
}

# ai solution - ну я просто хз как это норм рреализовать,едим то что дают.
def media_tag_logic(block):
    cls = type(block).__name__
    tag = media_tags.get(cls, "img")
    caption = getattr(block, "caption", None)
    caption_text = in_rich_text(getattr(caption, "text", None)) if caption else ""
    credit_text = in_rich_text(getattr(caption, "credit", None)) if caption else ""
    media_tag = f'<img src=""/>' if tag == "img" else f'<{tag} src=""></{tag}>'
    figcaption = ""
    if caption_text or credit_text:
        cite = f"<cite>{credit_text}</cite>" if credit_text else ""
        figcaption = f"<figcaption>{caption_text}{cite}</figcaption>"
    return f"<figure>{media_tag}{figcaption}</figure>"

def work_w_collage(block):
    items_html = "".join(rich_to_html_handler(item) for item in block.items)
    return items_html + caption_logic(getattr(block, "caption", None))

def work_w_blockquote(block):
    caption = in_rich_text(getattr(block, "caption", None))
    text = in_rich_text(block.text)
    if caption:
        return f"<blockquote>{text}<cite>{caption}</cite></blockquote>"
    return f"<blockquote>{text}</blockquote>"

def work_w_pullquote(block):
    caption = in_rich_text(getattr(block, "caption", None))
    text = in_rich_text(block.text)
    if caption:
        return f"<aside>{text}<cite>{caption}</cite></aside>"
    return f"<aside>{text}</aside>"

rich_and_html = {
    "PageBlockTitle": lambda b: f"<h1>{in_rich_text(b.text)}</h1>",
    "PageBlockSubtitle": lambda b: f"<h2>{in_rich_text(b.text)}</h2>",
    "PageBlockHeader": lambda b: f"<h3>{in_rich_text(b.text)}</h3>",
    "PageBlockSubheader": lambda b: f"<h4>{in_rich_text(b.text)}</h4>",
    "PageBlockKicker": lambda b: f"<p>{in_rich_text(b.text)}</p>",
    "PageBlockHeading1": lambda b: f"<h1>{in_rich_text(b.text)}</h1>",
    "PageBlockHeading2": lambda b: f"<h2>{in_rich_text(b.text)}</h2>",
    "PageBlockHeading3": lambda b: f"<h3>{in_rich_text(b.text)}</h3>",
    "PageBlockHeading4": lambda b: f"<h4>{in_rich_text(b.text)}</h4>",
    "PageBlockHeading5": lambda b: f"<h5>{in_rich_text(b.text)}</h5>",
    "PageBlockHeading6": lambda b: f"<h6>{in_rich_text(b.text)}</h6>",
    "PageBlockParagraph": lambda b: f"<p>{in_rich_text(b.text)}</p>",
    "PageBlockPreformatted": lambda b: f'<pre><code class="language-{b.language}">{in_rich_text(b.text)}</code></pre>',
    "PageBlockFooter": lambda b: f"<footer>{in_rich_text(b.text)}</footer>",
    "PageBlockDivider": lambda b: "<hr/>",
    "PageBlockAnchor": lambda b: f'<a name="{b.name}"></a>',
    "PageBlockBlockquote": work_w_blockquote,
    "PageBlockPullquote": work_w_pullquote,
    "PageBlockBlockquoteBlocks": lambda b: (
        f"<blockquote>{''.join(rich_to_html_handler(x) for x in b.blocks)}"
        f"<cite>{in_rich_text(b.caption)}</cite></blockquote>"
    ),
    "PageBlockPhoto": media_tag_logic,
    "PageBlockVideo": media_tag_logic,
    "PageBlockAudio": media_tag_logic,
    "PageBlockCollage": work_w_collage,
    "PageBlockSlideshow": work_w_collage,
    "PageBlockTable": lambda b: (
        f"<table{' bordered' if getattr(b, 'bordered', False) else ''}"
        f"{' striped' if getattr(b, 'striped', False) else ''}>"
        + (f"<caption>{in_rich_text(b.title)}</caption>" if getattr(b, "title", None) else "")
        + f"{''.join(table_row(row) for row in b.rows)}</table>"
    ),
    "PageBlockList": lambda b: f"<ul>{''.join(list_item(i) for i in b.items)}</ul>",
    "PageBlockOrderedList": lambda b: f"<ol>{''.join(list_item(i) for i in b.items)}</ol>",
    "PageBlockDetails": lambda b: (
        f"<details><summary>{in_rich_text(b.title)}</summary>"
        f"{''.join(rich_to_html_handler(x) for x in b.blocks)}</details>"
    ),
    "PageBlockMap": lambda b: caption_logic(getattr(b, "caption", None)),
    "PageBlockMath": lambda b: f"<tg-math-block>{b.source}</tg-math-block>",
    "PageBlockThinking": lambda b: f"<tg-thinking>{in_rich_text(b.text)}</tg-thinking>",
}

def rich_to_html_handler(block):
    cls = type(block).__name__
    renderer = rich_and_html.get(cls)
    if renderer:
        return renderer(block)
    return f"<p>{in_rich_text(getattr(block, 'text', None))}</p>"

def conver_rich_to_html(rich_message):
    if rich_message is None:
        return ""
    return "\n".join(
        rendered for rendered in (rich_to_html_handler(block) for block in rich_message.blocks)
        if rendered
    )

class RichMsgLib(loader.Library):
    developer = "@SunnexGB"

    def __init__(self):
        self.active_processes = []

    # держу в курсе,это писал не я,но это вроде работает,если у вас есть нормальный способ сделать рвоно тоже самое,то жду PR (в прошлый раз перепутал буквы)
    def rich_send_topic(self, message): # я привел их ко всем рич подобным функциям чтобы их было интуитивно вызывать(наверное)
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

    async def rich_send_inline(self, client, inline, chat_id, rich_message, reply_to=None): 
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
        rich_message = self.rich_params(r_message, parse_mode, rtl, noautolink)
        if rich_mode == "auto":
            rich_mode = "self" if client.heroku_me.premium else "inline" # нужно для проверки на премиум
        if rich_mode == "self":
            return await self.send_myself(client, chat_id, rich_message, reply_to=reply_to)
        return await self.rich_send_inline(client, inline, chat_id, rich_message, reply_to=reply_to)

    # новые методы,которые работают с ричами (выискивались путем лазаня по телекону,генерации методов и структуры + клодик помогал)
    async def rich_edit_message(self, client, chat_id, message_id, r_message, parse_mode="body", rtl=False, noautolink=False):
        rich_message = self.rich_params(r_message, parse_mode, rtl, noautolink)
        return await client(
            EditMessageRequest(
            peer=chat_id,
            id=message_id,
            rich_message=rich_message,
        ))

    async def rich_edit_inline_message(self, client, inline_message_id, r_message, parse_mode="body", rtl=False, noautolink=False):
        rich_message = self.rich_params(r_message, parse_mode, rtl, noautolink)
        return await client(
            EditInlineBotMessageRequest(
            id=inline_message_id,
            rich_message=rich_message,
        ))

    # это было в пуле методов я не смог нормально протестить,но это работает.
    async def rich_save_draft(self, client, chat_id, r_message, parse_mode="body", reply_to=None, rtl=False, noautolink=False):
        rich_message = self.rich_params(r_message, parse_mode, rtl, noautolink)
        return await client(
            SaveDraftRequest(
            peer=chat_id,
            message="",
            rich_message=rich_message,
            reply_to=(
                InputReplyToMessage(reply_to_msg_id=reply_to, top_msg_id=reply_to)
                if reply_to else None
            ),
        ))

    async def rich_get_message(self, client, chat_id, message_id, raw=False):
        # messages.getRichMessage, который возвращает messages.Messages,
        # вернет сырой объект
        result = await client(
            GetRichMessageRequest(
                peer=chat_id, id=message_id
                ))
        rich_message = result.messages[0].rich_message if result.messages else None
        if raw:
            return rich_message
        return conver_rich_to_html(rich_message)

    async def rich_translate(self, client, to_lang, chat_id=None, message_ids=None, r_messages=None, tone=None, raw=False):
        result = await client(
            TranslateRichMessageRequest(
            to_lang=to_lang,
            peer=chat_id,
            id=message_ids,
            text=r_messages,
            tone=tone,
        ))
        if raw:
            return result.result
        return [conver_rich_to_html(rich_message) for rich_message in result.result]

    async def rich_answer_ai(self, client, r_message, parse_mode="body", proofread=None, emojify=None, translate_to_lang=None, tone=None, raw=False):
        rich_message = self.rich_params(r_message, parse_mode)
        result = await client(
            ComposeRichMessageWithAIRequest(
            text=rich_message,
            proofread=proofread,
            emojify=emojify,
            translate_to_lang=translate_to_lang,
            tone=tone,
        ))
        if raw:
            return result.result
        return conver_rich_to_html(result.result)

    async def rich_send_thinking(self, inline, chat_id, r_message, parse_mode="html", top_msg_id=None):
        bot = inline.bot
        rich_message = self.rich_params(r_message, parse_mode)
        peer = await bot.get_input_entity(chat_id)
        return await bot(
            SetTypingRequest(
            peer=peer,
            top_msg_id=top_msg_id,
            action=InputSendMessageRichMessageDraftAction(rich_message=rich_message),
        ))

    async def rich_send_ephemeral(self, client, chat_id, receiver_id, r_message, parse_mode="body", reply_to=None, rtl=False, noautolink=False):
    # являеться просто таким сырым запросом,я хз как с этим работать.
        rich_message = self.rich_params(r_message, parse_mode, rtl, noautolink)
        return await client(
            SendEphemeralMessageRequest(
            peer=chat_id,
            receiver_id=receiver_id,
            message="1",
            rich_message=rich_message,
            reply_to=(
                InputReplyToMessage(reply_to_msg_id=reply_to, top_msg_id=reply_to)
                if reply_to else None
            ),
        ))

    def rich_params(self, r_message, parse_mode="body", rtl=False, noautolink=False):
        if parse_mode == "markdown":
            return InputRichMessageMarkdown(markdown=r_message, rtl=rtl, noautolink=noautolink)
        if parse_mode == "html":
            return InputRichMessageHTML(html=r_message, rtl=rtl, noautolink=noautolink)
        return InputRichMessage(blocks=r_message, rtl=rtl, noautolink=noautolink)

    async def cleanup(self, inline):
        bot = inline.bot
        for handler in self.active_processes:
            bot.remove_event_handler(handler, events.InlineQuery())
        self.active_processes.clear()
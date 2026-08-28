# requires: https://files.pythonhosted.org/packages/54/71/37f69f1370f9f2bc9d8fbc1ab90d3b510e4878cd966d63a602c4833f09fa/simple_rule34-1.0.0.8.tar.gz
# meta banner: https://x0.at/FLUT.jpg
# meta pic: https://x0.at/FLUT.jpg
# meta developer: @H_SunMods
# version: 1.0.0

from SimpleRule34 import Rule34Api
from herokutl.types import Message
from ..types import InlineCall
from .. import loader, utils

@loader.tds
class r34(loader.Module):
    """Модуль для поиска порно-артов"""
    strings = {
        "name": "Rule34",
        "porn_reulsts_doc": "Сколько запросов показывать разом при поиске порно",
        "enter_response_for_search": "Введите запрос или теги для поиска",
        "no_valid_response": "По вашему запросу ничего не найдено",
        "error_description": "Не удалось показать порнушку",
        "try_edit_response": "Попробуйте изменить запрос",
        "main_inline_title": "Теги к порнухе:\n",
        "end_alert": "Всмысле, без порна...",
        "porn_not_found": "Порна не найдено",
        "no_args": "Ты не указал аргументов",
        "enter_response": "Введите запрос",
        "search_porna": "Найти порна!!!",
        "not_found": "Ничего не найдено",
        "back_alert": "Там нету порна",
        "example": "Например: furry",
        "No tags": "Теги отсуцтвуют",
        "porn_tags": "Теги порна:",
        "close": "Закрыть",
        "error": "Ошибка",
    }
    
    strings_en = {
        "porn_reulsts_doc": "How many requests to show at once when searching for porn",
        "enter_response_for_search": "Enter a query or tags to search",
        "no_valid_response": "Nothing found for your query",
        "error_description": "Failed to display the porn",
        "try_edit_response": "Try modifying your query",
        "no_args": "You didn't specify any arguments",
        "_cls_doc": "Module for search porn arts",
        "back_alert": "There's no porn there",
        "main_inline_title": "Porn tags:\n",
        "enter_response": "Enter a query",
        "porn_not_found": "No porn found",
        "end_alert": "Wdym, no porn...",
        "example": "For example: furry",
        "search_porna": "Find porn!",
        "not_found": "Nothing found",
        "porn_tags": "Porn tags:",
        "No tags": "No tags",
        "close": "Close",
        "error": "Error",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                option="porn_reulsts",
                default=15,
                doc=lambda: self.strings["porn_reulsts_doc"],
                validator=loader.validators.Integer(),
            )
        )
        self.r_user_id = 5255009 # owner @dubstep_namaz1337
        self.r_api = 'd82f6db279ce94313e629e791533d456a4309dfeb528ddab6eee4b7472156f0def07ebfd3e64b9dddbf0d3b78f227ba8a5f386533ef1ccb1377d8a97481811dc' # owner @dubstep_namaz1337
        self.def_page = 0
        self.history = {}

    def api_init(self):
        api = Rule34Api(user_id=self.r_user_id, api_key=self.r_api)
        return api

    @staticmethod
    def search_tags(search_query: str):
        return [
            tag.strip().lower().replace(" ", "_")
            for tag in search_query.replace(",", " ").split()
            if tag.strip()
        ]

    async def search_porn(self, search_query: str, page: int = 0):
        api = self.api_init()
        search_tags = self.search_tags(search_query)
        search_tags.append("sort:random")
        porn = await api.post.get_list(
            tags=search_tags, 
            amount=1,
            page=page
        )
        return porn

    async def change_page(self, call: InlineCall, query: str, direction: int):
        if call.message_id not in self.history:
            self.history[call.message_id] = {
                "query": query,
                "page": 0, 
                "urls": {}
            }

        current_page = self.history[call.message_id]["page"]
        next_page = current_page + direction
        if next_page < 0:
            await call.answer(self.strings["back_alert"], show_alert=True)
            return
        if next_page in self.history[call.message_id]["urls"]:
            porn_url = self.history[call.message_id]["urls"][next_page]
        else:
            porn = await self.search_porn(query, page=next_page)
            if not porn:
                await call.answer(self.strings["end_alert"], show_alert=True)
                return
            porn_url = str(porn[0].file.url)
            self.history[call.message_id]["urls"][next_page] = porn_url
        self.history[call.message_id]["page"] = next_page
        try:
            await call.edit(
                text=self.strings["main_inline_title"],
                photo=porn_url,
                reply_markup=[
                    [
                        {
                            "text": "⮜",
                            "callback": self.change_page,
                            "args": [query, -1]
                        },
                        {
                            "text": "🔗",
                            "url": porn_url
                        },
                        {
                            "text": "⮞",
                            "callback": self.change_page,
                            "args": [query, 1]
                        }
                    ],
                    [
                        {
                            "text": self.strings["close"],
                            "action": "close",
                        }
                    ]
                ]
            )
        except Exception:
            await self.change_page(call, query, 1)

    @loader.inline_handler(en_doc="Search porn(at discretion)")
    async def r34_inline_handler(self, event: "loader.InlineCall", page=0):
        """Поиск порна(на выбор)"""
        handler_args = event.args.strip()
        if not handler_args:
            return {
                "title": self.strings["enter_response"],
                "description": self.strings["example"],
                "message": self.strings["enter_response_for_search"],
            }

        api = self.api_init()
        self.search_tags(handler_args).append("sort:random")

        porna = await api.post.get_list(
            tags=self.search_tags(handler_args), 
            amount=self.config["porn_reulsts"], 
            page=page
        )
        if not porna:
            return {
                "title": self.strings["porn_not_found"],
                "description": self.strings["try_edit_response"],
                "message": self.strings["no_valid_response"],
            }

        results = []
        for post in porna:
            photo_url = str(post.file.url)
            porn_url = f"https://rule34.xxx/index.php?page=post&s=view&id={post.id}"
            porn_tags = " ".join(f"#{tag}" for tag in post.tags[:6])
            porn_title = self.strings["porn_tags"]
            thumb = self.inline._web_document(photo_url)
            caption = (
                f"<a href='{photo_url}'>&#8203;</a>"
                f"<b>Tags:</b> {porn_tags}"
            )

            results.append(
                await event.builder.article(
                    id=f"r34_{post.id}",
                    title=porn_title,
                    description=porn_tags if porn_tags else self.strings["No tags"],
                    thumb=thumb,
                    text=caption,
                    parse_mode="html",
                    link_preview=True,
                    buttons=self.inline.generate_markup(
                        [
                            [
                                {
                                    "text": "🔗", "url": porn_url
                                }
                            ]
                        ]
                    ),
                )
            )

        if not results:
            return {
                "title": self.strings["error"],
                "description": self.strings["error_description"],
                "message": self.strings["enter_response"],
            }

        await event.answer(results, cache_time=5)

        
    @loader.command(en_doc="- Search porna art: .r34 no arg(for open search) | #solo, #hentai | genshin ")
    async def r34(self, message: Message):
        """- Найти порно арт: .r34 без аргументов(чтобы открыть поиск) | #solo, #hentai | genshin"""
        args = utils.get_args_raw(message)
        if not args:
            await self.inline.form(
                text=self.strings["no_args"],
                message=message,
                reply_markup=[
                    [
                        {
                            "text": self.strings["search_porna"],
                            "switch_inline_query_current_chat": "r34",
                        }
                    ]
                ]
            )
            return
        while True:
            porn = await self.search_porn(args, page=self.def_page)
            if not porn:
                await utils.answer(message, self.strings["not_found"])
                return
            porn_url = str(porn[0].file.url)
            self.history[message.id] = {
                "query": args, 
                "page": self.def_page, 
                "urls": {self.def_page: porn_url}
            }

            for post in porn:
                porn_tags = " ".join(f"#{tag}" for tag in post.tags[:6])
        
            try:
                await self.inline.form(
                    text=f"{porn_tags}",
                    message=message,
                    photo=porn_url,
                    reply_markup=[
                        [
                            {
                                "text": "⮜",
                                "callback": self.change_page,
                                "args": [args, -1]
                            },
                            {
                                "text": "🔗",
                                "url": porn_url
                            },
                            {
                                "text": "⮞",
                                "callback": self.change_page,
                                "args": [args, 1]
                            }
                        ],
                        [
                            {
                                "text": self.strings["close"],
                                "action": "close",
                            }
                        ]
                    ]
                )
                break
            except Exception:
                self.def_page += 1
                continue
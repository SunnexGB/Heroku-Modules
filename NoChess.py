# requires: aiohttp pyngrok
# meta developer: @H_SunMods
# meta banner: https://r2.fakecrime.bio/uploads/965a3206-4609-4dff-beb0-6831f8b90e12.jpg
# current ver
__version__ = (0, 1, 0)

import json
import socket
import asyncio
import secrets
import logging
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from aiohttp import ClientSession, ClientTimeout, web
from herokutl.types import Message
from pyngrok import conf, ngrok
from .. import loader, utils
from ..inline.types import InlineCall

logging.getLogger("pyngrok").setLevel(logging.WARNING)
logging.getLogger("pyngrok.process").setLevel(logging.WARNING)
logging.getLogger("pyngrok.process.ngrok").setLevel(logging.WARNING)

html_raw = "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/refs/heads/main/Assets/NoChess/raw_assets/index.html"
css_raw = "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/refs/heads/main/Assets/NoChess/raw_assets/style.css"
js_raw = "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/refs/heads/main/Assets/NoChess/raw_assets/javascript.js"
asset_root_raw = "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/NoChess"
botfather_photo_url = "https://r2.fakecrime.bio/uploads/d3e16245-15a2-43f1-b176-493b4d9f1f21.jpg"

@loader.tds
class NoChess(loader.Module):
    """NoChess - web module that allows u to launch a web page either as a functional HTML page or as a Telegram Mini-App. This is an add-on for Chess module by @nullmod"""

    # я пытался кароче сделать тут перевод делая реплейсы в зависимости от стрингов,но это не работает,поэтому да
    strings = {
        "name": "NoChess",
        "starting": "( ﾉ･ｪ･ )ﾉ <b>Starting NoChess...</b>",
        "online": "(*˘︶˘*) <b>NoChess is running</b>",
        "already_running": "ʕᵕᴥᵕʔ <b>NoChess is already running</b>",
        "stopped": "･ﾟ･(｡>д<｡)･ﾟ･ NoChess stopped",
        "not_running": "(✿╹◡╹) NoChess is not running",
        "ngrok_missing": "Set a <code>ngrok_token</code>",
        "ngrok_error": "Ngrok start error: <code>{}</code>",
        "asset_read_error": "Failed to load web assets: <code>{}</code>",
        "open_button": "Open mini-app",
        "stop_button": "Stop",
        "about_text": "<b>Important read:</b>\nSometimes the server won't lift cause there's enough processes running, for example on HikkaHost, for this I just rebooted the server\nNext is that <code>cma</code> setups the app by a template and it's rly crooked, so you'll have to set some web app config settings yourself\nAnd also:\n    1. First launch will start straight with a site link, not as a web app\n    2. Use <code>nochess</code>, and then <code>cma</code> to setup the web app\n    3. After that restart the process by typing <code>nochess -kill</code> and <code>nochess</code> again\nYeah it's hacky as hell, but I was so over doing stuff that I started dumping some routine like working with files on ai, which I didn't like so I decided to quick-release the module before it's too late\nWell and maybe soon I'll make an update, right now it's some pre-alpha version, that's why the version name is like this, later I'll change it to 1.0.0, if people actually dig the module as an idea",
        "cma_start": "( ﾉ･ｪ･ )ﾉ <b>Creating mini app in BotFather...</b>",
        "cma_need_url": "Set mini app web URL first or run <code>.nochess</code> to get it.",
        "cma_done": "(*˘︶˘*) <b>Done.</b>",
        "cma_error": "Error: <code>{}</code>",
        "RuntimeError": "inline bot username not found",
    }

    strings_ru = {
        "_cls_doc": "NoChess - Веб модуль который позволяет запускать веб-пейдж,как HTML страницу с функционалом,так же в виде Telegram Mini-App. Является дополнением к модулю Chess от @nullmod",
        "starting": "( ﾉ･ｪ･ )ﾉ <b>Запуск NoChess...</b>",
        "online": "(*˘︶˘*) <b>NoChess запущен</b>",
        "already_running": "ʕᵕᴥᵕʔ <b>NoChess уже запущен</b>",
        "stopped": "･ﾟ･(｡>д<｡)･ﾟ･ NoChess остановлен",
        "not_running": "(✿╹◡╹) NoChess не запущен",
        "ngrok_missing": "Укажи <code>ngrok_token</code>",
        "ngrok_error": "Ошибка запуска ngrok: <code>{}</code>",
        "asset_read_error": "Не удалось загрузить веб-ассеты: <code>{}</code>",
        "open_button": "Открыть мини-приложение",
        "stop_button": "Остановить",
        "about_text": "<b>Важно к прочтению:</b>\nИногда сервер не может подниматься из за того что запущено достаточно процессов, например на HikkaHost,для этого я просто перезагружал сервер.\nДалее это то что <code>cma</code> сетапает приложение по шаблону и оч криво, поэтому вам придется выставлять некоторые настройки конфигурации веб приложения самим.\nА еще:\n    1. Первый запуск будет запускаться сразу ссылкой на сайт, а не как веб приложение.\n    2. Используйте <code>nochess</code>, а потом <code>cma</code> чтобы настроить веб приложение.\n    3. После чего перезапустите процесс написав <code>nochess -kill</code> и повторно <code>nochess</code>.\nДа это костыли, но мне уже настолько было в падлу что то делать что я уже стал спихивать рутину по типу работы с файлами на ии, что мне не понравилось и я решил быстро релизать модуль пока не стало поздно.\nНу и может быть в скором времени я уже сделаю апдейт, на данный момент это какая то пре-альфа версия, поэтому и название версии такое, в дальнейшем изменю на 1.0.0, если модуль вообще понравиться людям как идея.",
        "cma_start": "( ﾉ･ｪ･ )ﾉ <b>Создаю эпку через BotFather...</b>",
        "cma_need_url": "Сначала укажи URL мини-эпки или запусти <code>.nochess</code>, чтобы получить его",
        "cma_done": "(*˘︶˘*) <b>Готово</b>",
        "cma_error": "Ошибка: <code>{}</code>",
        "RuntimeError": "юз инлайн бота не найден",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "ngrok_token",
                None,
                "Token from ngrok.com | Токен полученый на ngrok.com",
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "mini_app_url",
                None,
                "Mini app direct url | Директ ссылка на ваше мини приложение",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "block_light",
                "#D8E3E7",
                "Light board block color | Цвет светлых полей на доске",
                validator=loader.validators.String()
            ),
            loader.ConfigValue("block_dark",
                "#7699AF",
                "Dark board block color | Цвет тёмных полей на доске",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "select_block",
                "#FF5A5A",
                "Selected block color | Цвет для выделения полей на доске",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "move_pieces_color",
                "#58B4FF",
                "Move highlight color | Цвет подсвечиваниях перехода на другую позицию",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "result_win", 
              "#00BE16", 
                "Winner color | Блок цвета победителя",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "result_lose",
                "#BE0000",
                "Loser color | Блок цвета проигравшего",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "result_draw",
                "#434343",
                "Draw color | Блок цвета при ничьей",
                validator=loader.validators.String()
            ),
            loader.ConfigValue(
                "arrow_color",
                "#BD3667",
                "Arrow color | Цвет стрелки",
                validator=loader.validators.String()
            ),
        )
        
        self.runner = None
        self.tunnel_url = None
        self.access_token = None
        self.games_cache = []
        self.games_dump = ""

    def theme_config_dict(self):
        return {
            "block_light": self.config["block_light"],
            "block_dark": self.config["block_dark"],
            "select_block": self.config["select_block"],
            "move_pieces_color": self.config["move_pieces_color"],
            "result_win": self.config["result_win"],
            "result_lose": self.config["result_lose"],
            "result_draw": self.config["result_draw"],
            "arrow_color": self.config["arrow_color"],
        }

    async def refresh_games_cache(self):
        chess = self.lookup("chess")
        if not chess or not getattr(chess, "games", None):
            self.games_cache = []
            self.games_dump = ""
            return

        chunks = []
        items = list(chess.games.items())

        def sort_key(item):
            key = str(item[0])
            return (0, int(key)) if key.isdigit() else (1, key)

        for _, game in sorted(items, key=sort_key, reverse=True):
            node = None

            if isinstance(game, dict):
                game_obj = game.get("game", {})
                if isinstance(game_obj, dict):
                    node = game_obj.get("root_node") or game_obj.get("node")
                if node is None:
                    node = game.get("root_node") or game.get("node")

            if node is None and hasattr(game, "game"):
                game_obj = getattr(game, "game", None)
                if isinstance(game_obj, dict):
                    node = game_obj.get("root_node") or game_obj.get("node")

            if node is None and hasattr(game, "root_node"):
                node = getattr(game, "root_node", None)

            if node is None and hasattr(game, "node"):
                node = getattr(game, "node", None)

            if node:
                chunks.append(str(node).strip())

        self.games_cache = [x for x in chunks if x]
        self.games_dump = "\n\n".join(self.games_cache)

    async def get_me_json(self):
        me = await self.client.get_me()
        fallback_photo = "https://i.pinimg.com/736x/6e/0a/0c/6e0a0cf688b30ba9de81b81bb32e49f9.jpg"
        full_name = (getattr(me, "first_name", "") or "") + (
            (" " + getattr(me, "last_name", "")) if getattr(me, "last_name", None) else ""
        )
        return {
            "id": getattr(me, "id", None),
            "username": getattr(me, "username", None),
            "first_name": getattr(me, "first_name", None),
            "last_name": getattr(me, "last_name", None),
            "name": full_name.strip() or str(getattr(me, "id", "Unknown")),
            "photo": fallback_photo,
            "enemy_photo": fallback_photo,
        }

    def check_access(self, request):
        token = request.query.get("token") or request.cookies.get("nochess_token")
        return bool(self.access_token and token == self.access_token)

    def ensure_access_token(self):
        if self.access_token:
            return self.access_token
        self.access_token = self.get("access_token")
        if not self.access_token:
            self.access_token = secrets.token_urlsafe(32)
            self.set("access_token", self.access_token)
        return self.access_token

    async def read_remote_asset(self, url):
        timeout = ClientTimeout(total=15)
        async with ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}: {url}")
                return await response.text()

    async def load_web_assets(self):
        html = await self.read_remote_asset(html_raw)
        css = await self.read_remote_asset(css_raw)
        js = await self.read_remote_asset(js_raw)
        return html, css, js

    def localication_script(self):
        return (
            "<script>(async()=>{"
            "try{const me=await fetch('/api/me').then(r=>r.json());window.nochess_profile=me;if(typeof setNoChessProfile==='function'){setNoChessProfile(me);}}catch(_e){}"
            "let rawGames=[];"
            "try{const d=await fetch('/api/games').then(r=>r.json());rawGames=Array.isArray(d.games)?d.games:[];}catch(_e){}"
            "const apply=()=>{if(typeof parsePgnToGameState!=='function'||typeof buildHistoryList!=='function')return false;"
            "parsed_games=(rawGames||[]).map(g=>parsePgnToGameState(g)).filter(Boolean);"
            "buildHistoryList();if(parsed_games.length>0&&typeof loadGame==='function')loadGame(0);return true;};"
            "if(apply())return;"
            "let attempts=0;const iv=setInterval(()=>{attempts++;if(apply()||attempts>40)clearInterval(iv);},250);"
            "})();</script>"
        )

    def inject_runtime_config(self, html, css, js):
        asset_root = asset_root_raw.rstrip("/")
        if asset_root:
            css = css.replace("url('bg.png')", f"url('{asset_root}/other/bg.png')")
        theme_json = json.dumps(self.theme_config_dict(), ensure_ascii=False)
        bootstrap = (
            "<script>"
            f"window.nochess_theme={theme_json};"
            f"window.nochess_asset_root={json.dumps(asset_root)};"
            "</script>"
        )
        html = html.replace('<link rel="stylesheet" href="style.css">', f"<style>{css}</style>")
        html = html.replace('<script src="javascript.js"></script>', bootstrap + f"<script>{js}</script>")
        return html

    async def handle_home(self, request):
        try:
            html, css, js = await self.load_web_assets()
        except Exception as error:
            return web.Response(
                text=self.strings["asset_read_error"].format(utils.escape_html(str(error))),
                status=500,
            )
        html = self.inject_runtime_config(html, css, js)
        html = html.replace("</body>", self.localication_script() + "</body>")
        response = web.Response(text=html, content_type="text/html")
        response.set_cookie(
            "nochess_token",
            self.access_token,
            max_age=86400,
            httponly=True,
            samesite="Lax",
        )
        return response

    async def handle_games(self, request):
        if not self.check_access(request):
            return web.json_response({"error": "Unauthorized"}, status=401)
        if not self.games_cache:
            await self.refresh_games_cache()
        return web.json_response({"games_dump": self.games_dump, "games": list(self.games_cache)})

    async def handle_me(self, request):
        if not self.check_access(request):
            return web.json_response({"error": "Unauthorized"}, status=401)
        return web.json_response(await self.get_me_json())

    async def stop_server(self):
        was_running = bool(self.runner)
        try:
            ngrok.kill()
        except Exception:
            pass
        if self.runner:
            await self.runner.cleanup()
            self.runner = None
        self.tunnel_url = None
        return was_running

    async def send_form(self, message, url):
        await self.inline.form(
            self.strings["online"],
            message=message,
            reply_markup=[
                [{"text": self.strings["open_button"], "url": url}],
                [{"text": self.strings["stop_button"], "callback": self.stop_callback}],
            ],
        )

    async def stop_callback(self, call: InlineCall):
        was_running = await self.stop_server()
        await call.answer(
            self.strings["stopped"] if was_running else self.strings["not_running"],
            show_alert=False,
        )
        try:
            await call.delete()
        except Exception:
            try:
                await call.edit(self.strings["stopped"] if was_running else self.strings["not_running"])
            except Exception:
                pass

    @loader.command(ru_doc="[-kill] Вызываь веб интерфейс для просмотра партии")
    async def nochess(self, message: Message):
        """[-kill] Call web interface to view chess game"""
        try:
            return await self.nochess_args(message)
        except Exception as error:
            await self.stop_server()
            return await utils.answer(
                message,
                self.strings["ngrok_error"].format(utils.escape_html(str(error))),
            )

    async def nochess_args(self, message: Message):
        args = (utils.get_args_raw(message) or "").strip().lower()
        if args == "-kill":
            was_running = await self.stop_server()
            return await utils.answer(message, self.strings["stopped"] if was_running else self.strings["not_running"])
        mini_url = (self.config["mini_app_url"] or "").strip().rstrip("/")
        is_tg_direct = mini_url.startswith("https://t.me/")
        if self.runner:
            if is_tg_direct:
                access = mini_url
            else:
                base = (self.tunnel_url or "").rstrip("/")
                access = f"{base}/?token={self.access_token}" if base and self.access_token else base
            await utils.answer(message, self.strings["already_running"])
            if access:
                await self.send_form(message, access)
            return
        if not self.config["ngrok_token"] and (not mini_url or is_tg_direct):
            return await utils.answer(message, self.strings["ngrok_missing"])
        await self.refresh_games_cache()
        await utils.answer(message, self.strings["starting"])
        self.ensure_access_token()
        sock = socket.socket()
        sock.bind(("", 0))
        port = sock.getsockname()[1]
        sock.close()
        app = web.Application()
        app.router.add_get("/", self.handle_home)
        app.router.add_get("/api/games", self.handle_games)
        app.router.add_get("/api/me", self.handle_me)
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        await web.TCPSite(self.runner, "127.0.0.1", port).start()
        try:
            if self.config["ngrok_token"]:
                conf.get_default().auth_token = self.config["ngrok_token"]
                tunnel = ngrok.connect(port)
                self.tunnel_url = tunnel.public_url.rstrip("/")
            else:
                self.tunnel_url = mini_url
        except Exception as error:
            await self.stop_server()
            return await utils.answer(
                message,
                self.strings["ngrok_error"].format(utils.escape_html(str(error))),
            )
        if is_tg_direct:
            access_url = mini_url
        else:
            base = (self.tunnel_url or "").rstrip("/")
            access_url = f"{base}/?token={self.access_token}" if base and self.access_token else base
        await self.send_form(message, access_url)

    @loader.command(ru_doc="Создает и настраивает эпку")
    async def cma(self, message: Message):
        """Create and setup mini-app"""
        raw_args = (utils.get_args_raw(message) or "").strip()
        parts = raw_args.split()
        web_url = ""
        short_name = "NoChess"
        if parts:
            web_url = parts[0]
        if len(parts) > 1:
            short_name = parts[1]
        if not web_url:
            candidate = (self.tunnel_url or "").strip()
            if not candidate:
                candidate = (self.config["mini_app_url"] or "").strip()
            if candidate.startswith("https://t.me/"):
                candidate = ""
            web_url = candidate
        if not web_url:
            return await utils.answer(message, self.strings["cma_need_url"])
        self.ensure_access_token()
        if web_url.startswith("http") and "t.me/" not in web_url:
            parsed = urlsplit(web_url)
            query = dict(parse_qsl(parsed.query, keep_blank_values=True))
            query["token"] = self.access_token
            web_url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))
        await utils.answer(message, self.strings["cma_start"])
        try:
            bot_username = (await self.inline.bot.get_me()).username
            bot_username = (bot_username or "").strip().lstrip("@")
            if not bot_username:
                raise RuntimeError(self.strings["RuntimeError"])
            await self.client.send_message("@BotFather", "/cancel")
            await asyncio.sleep(0.9)

            async with self.client.conversation("@BotFather", timeout=120) as conv:
                await conv.send_message("/newapp")
                await conv.get_response()
                await asyncio.sleep(0.8)
                await conv.send_message(f"@{bot_username}")
                await conv.get_response()
                await asyncio.sleep(0.8)
                await conv.send_message("NoChessModule")
                await conv.get_response()
                await asyncio.sleep(0.8)
                await conv.send_message("NoChess")
                await conv.get_response()
                await asyncio.sleep(0.8)
                await conv.send_file(botfather_photo_url)
                await conv.get_response()
                await asyncio.sleep(0.8)
                await conv.send_message("/empty")
                await conv.get_response()
                await asyncio.sleep(0.8)
                await conv.send_message(web_url)
                await conv.get_response()
                await asyncio.sleep(0.8)
                await conv.send_message(short_name)
                await conv.get_response()

            direct_link = f"https://t.me/{bot_username}/{short_name}"
            module_ref = None
            try:
                module_ref = self.lookup("NoChess")
            except Exception:
                module_ref = None
            if module_ref:
                module_ref.config["mini_app_url"] = direct_link
            else:
                self.config["mini_app_url"] = direct_link
            await utils.answer(message, self.strings["cma_done"])
        except Exception as error:
            await utils.answer(message, self.strings["cma_error"].format(utils.escape_html(str(error))))

    @loader.command(ru_doc="ВАЖНО К ПРОЧТЕНИЮ")
    async def about(self, message: Message):
        """IMPORTANT READING"""
        await utils.answer(message, self.strings["about_text"])
    async def on_unload(self):
        await self.stop_server()
# requires: aiohttp python-chess
# meta developer: @H_SunMods
# meta banner: https://r2.fakecrime.bio/uploads/965a3206-4609-4dff-beb0-6831f8b90e12.jpg
# current ver
__version__ = (2, 0, 0)

botfather_photo_url = "https://r2.fakecrime.bio/uploads/d3e16245-15a2-43f1-b176-493b4d9f1f21.jpg"

import asyncio
import chess
import html
import json
import logging
import os
import re
import secrets
import socket
import subprocess
import time
from aiohttp import web, WSMsgType, ClientSession

from .. import loader, utils
from ..inline.types import InlineCall

logger = logging.getLogger(__name__)

FRONTEND_URL = "https://raw.githubusercontent.com/sepiol026-wq/Heroku-Modules/fuck/Assets/NoChess/frontend/index.html"

strings = {
    "name": "NoChess",
    "_cls_doc": "Chess web module. Play real-time chess via browser.",
    "_cmd_doc_nochess": "[user] — create a chess game via browser",
    "_cmd_doc_ncstop": "— stop NoChess server",
    "no_opponent": "Error: reply to a user or provide @username to challenge.",
    "online": "Game is live!",
    "starting": "Starting server...",
    "already_running": "Server already running.",
    "stopped": "Server stopped.",
    "not_running": "Server is not running.",
    "tunnel_error": "Serveo tunnel error: <code>{}</code>",
    "open_button": "Open mini-app",
    "stop_button": "Stop",
    "about_text": "<b>NoChess v2.0.0</b>\nFully playable chess — create a game, share the link, play real-time.\nUses python-chess engine, no external Chess module needed.\nSupports checkmate, stalemate, draw by agreement, resignation, threefold repetition, 50-move rule, insufficient material.\nCommands: <code>.nochess @user</code> to challenge.",
    "server_starting": "<code>NoChess server starting...</code>",
    "RuntimeError": "inline bot username not found",
    "not_supported_platform": "(T_T) Unfortunately, it is impossible to install this module on this platform.\n\n(~)~ This is not an error, please do not contact support."
}

strings_ru = {
    "name": "NoChess",
    "_cls_doc": "Шахматный веб-модуль. Играй в шахматы в реальном времени через браузер.",
    "_cmd_doc_nochess": "[юзер] — создать шахматную партию через браузер",
    "_cmd_doc_ncstop": "— остановить сервер NoChess",
    "no_opponent": "Ошибка: укажи юзера через реплай или @username.",
    "online": "Партия запущена!",
    "starting": "Запуск сервера...",
    "already_running": "Сервер уже запущен.",
    "stopped": "Сервер остановлен.",
    "not_running": "Сервер не запущен.",
    "tunnel_error": "Ошибка туннеля Serveo: <code>{}</code>",
    "open_button": "Открыть мини-приложение",
    "stop_button": "Остановить",
    "about_text": "<b>NoChess v2.0.0</b>\nПолноценные шахматы — создай партию, отправь ссылку, играй в реальном времени.\nДвижок python-chess, без внешнего модуля Chess.\nПоддержка мата, пата, ничьей по соглашению, сдачи, троекратного повторения, правила 50 ходов, недостаточного материала.\nКоманды: <code>.nochess @user</code> вызвать на партию.",
    "server_starting": "<code>NoChess сервер запускается...</code>",
    "RuntimeError": "inline bot username not found",
    "not_supported_platform": "(T_T) К сожалению, установка этого модуля на данной платформе невозможна.\n\n(~)~ Это не ошибка, пожалуйста не обращайтесь в поддержку."
}

strings_ua = {
    "name": "NoChess",
    "_cls_doc": "Шаховий веб-модуль. Грай у шахи в реальному часі через браузер.",
    "_cmd_doc_nochess": "[юзер] — створити шахову партію через браузер",
    "_cmd_doc_ncstop": "— зупинити сервер NoChess",
    "no_opponent": "Помилка: вкажи юзера через реплай або @username.",
    "online": "Партія запущена!",
    "starting": "Запуск сервера...",
    "already_running": "Сервер вже запущено.",
    "stopped": "Сервер зупинено.",
    "not_running": "Сервер не запущено.",
    "tunnel_error": "Помилка тунелю Serveo: <code>{}</code>",
    "open_button": "Відкрити міні-застосунок",
    "stop_button": "Зупинити",
    "about_text": "<b>NoChess v2.0.0</b>\nПовноцінні шахи — створи партію, надішли посилання, грай в реальному часі.\nДвигун python-chess, без зовнішнього модуля Chess.\nПідтримка мату, пату, нічиєї за згодою, здачі, триразового повторення, правила 50 ходів, недостатнього матеріалу.\nКоманди: <code>.nochess @user</code> викликати на партію.",
    "server_starting": "<code>NoChess сервер запускається...</code>",
    "RuntimeError": "inline bot username not found",
    "not_supported_platform": "(T_T) На жаль, встановлення цього модуля на цій платформі неможливе.\n\n(~)~ Це не помилка, будь ласка не звертайтесь у підтримку."
}

strings_de = {
    "name": "NoChess",
    "_cls_doc": "Schach-Webmodul. Echtzeit-Schach im Browser.",
    "_cmd_doc_nochess": "[user] — Schachpartie im Browser starten",
    "_cmd_doc_ncstop": "— NoChess-Server stoppen",
    "no_opponent": "Fehler: Nutzer per Reply oder @username angeben.",
    "online": "Partie lauft!",
    "starting": "Server startet...",
    "already_running": "Server lauft bereits.",
    "stopped": "Server gestoppt.",
    "not_running": "Server lauft nicht.",
    "tunnel_error": "Serveo-Tunnel-Fehler: <code>{}</code>",
    "open_button": "Mini-App offnen",
    "stop_button": "Stopp",
    "about_text": "<b>NoChess v2.0.0</b>\nVollwertiges Schach — Partie erstellen, Link teilen, in Echtzeit spielen.\npython-chess Engine, kein externes Chess-Modul notig.\nUnterstutzt Schachmatt, Patt, Remis durch Vereinbarung, Aufgabe, dreifache Stellungswiederholung, 50-Zuge-Regel, unzureichendes Material.\nBefehle: <code>.nochess @user</code> herausfordern.",
    "server_starting": "<code>NoChess Server startet...</code>",
    "RuntimeError": "Inline-Bot-Benutzername nicht gefunden",
    "not_supported_platform": "(T_T) Leider ist die Installation dieses Moduls auf dieser Plattform nicht moglich.\n\n(~)~ Dies ist kein Fehler, bitte kontaktiere nicht den Support."
}

strings_jp = {
    "name": "NoChess",
    "_cls_doc": "チェスウェブモジュール。ブラウザでリアルタイムチェス。",
    "_cmd_doc_nochess": "[ユーザー] — ブラウザでチェスの対局を作成",
    "_cmd_doc_ncstop": "— NoChessサーバーを停止",
    "no_opponent": "エラー: リプライまたは@usernameで相手を指定。",
    "online": "対局開始!",
    "starting": "サーバー起動中...",
    "already_running": "サーバーは既に起動中。",
    "stopped": "サーバー停止。",
    "not_running": "サーバーは起動していません。",
    "tunnel_error": "Serveoトンネルエラー: <code>{}</code>",
    "open_button": "ミニアプリを開く",
    "stop_button": "停止",
    "about_text": "<b>NoChess v2.0.0</b>\nブラウザで対局を作成し、リンクを共有してリアルタイムプレイ。\npython-chessエンジン、外部Chessモジュール不要。\nチェックメイト、ステイルメイト、合意によるドロー、リザイン、3回反復、50手ルール、不十分な駒に対応。\nコマンド: <code>.nochess @user</code> で対局を申し込む。",
    "server_starting": "<code>NoChessサーバー起動中...</code>",
    "RuntimeError": "inline bot username not found",
    "not_supported_platform": "(T_T) 残念ながら、このプラットフォームではこのモジュールをインストールできません。\n\n(~)~ これはエラーではありません、サポートに連絡しないでください。"
}

strings_leet = {
    "name": "NoChess",
    "_cls_doc": "ch3ss w3b m0dul3. r34l-t1m3 ch3ss 1n br0ws3r.",
    "_cmd_doc_nochess": "[us3r] — cr34t3 ch3ss g4m3 v14 br0ws3r",
    "_cmd_doc_ncstop": "— st0p N0Ch3ss s3rv3r",
    "no_opponent": "3rr0r: r3ply 0r @us3rn4m3 t0 ch4ll3ng3.",
    "online": "G4m3 1s l1v3!",
    "starting": "S3rv3r b00t1ng...",
    "already_running": "S3rv3r 4lr34dy up.",
    "stopped": "S3rv3r k1ll3d.",
    "not_running": "S3rv3r n0t up.",
    "tunnel_error": "S3rv30 tunn3l f41l: <code>{}</code>",
    "open_button": "0p3n m1n1-4pp",
    "stop_button": "K1ll",
    "about_text": "<b>N0Ch3ss v2.0.0</b>\nFull ch3ss — cr34t3 g4m3, sh4r3 l1nk, pl4y r34l-t1m3.\npyth0n-ch3ss 3ng1n3, n0 3xt3rn4l Ch3ss m0dul3.\nSupp0rts ch3ckm4t3, st4l3m4t3, dr4w, r3s1gn, 3x r3p3t1t10n, 50-m0v3, 1nsuff m4t3r14l.\nC0mm4nds: <code>.n0ch3ss @us3r</code> t0 ch4ll3ng3.",
    "server_starting": "<code>N0Ch3ss s3rv3r b00t1ng...</code>",
    "RuntimeError": "1nl1n3 b0t h4ndl3 n0t f0und",
    "not_supported_platform": "(T_T) N0 sh0t th1s m0dul3 w0rks 0n th1s pl4tf0rm.\n\n(~)~ N0t 4 bug, d0n't h1t up supp0rt."
}

strings_neofit = {
    "name": "NoChess",
    "_cls_doc": "chess ting for the mandem. real-time chess in browser.",
    "_cmd_doc_nochess": "[user] — link up a chess game in the browser innit",
    "_cmd_doc_ncstop": "— shut down NoChess server",
    "no_opponent": "Bruv: reply or @username to run up on someone.",
    "online": "Game is live!",
    "starting": "Server booting...",
    "already_running": "Server already running.",
    "stopped": "Server shut down.",
    "not_running": "Server not running.",
    "tunnel_error": "Serveo tunnel bricked: <code>{}</code>",
    "open_button": "Pop the mini-app",
    "stop_button": "Cut it",
    "about_text": "<b>NoChess v2.0.0</b>\nFull chess — create a game, share the link, play real-time.\npython-chess engine, no external Chess module.\nSupports checkmate, stalemate, draw, resign, 3x repetition, 50-move, insufficient material.\nCommands: <code>.nochess @user</code> to challenge.",
    "server_starting": "<code>NoChess server booting...</code>",
    "RuntimeError": "inline bot handle MIA",
    "not_supported_platform": "(T_T) No shot this module works on this platform.\n\n(~)~ Not a bug, don't hit up support."
}

strings_tiktok = {
    "name": "NoChess",
    "_cls_doc": "Шахматный веб-модуль. Играй в шахматы в реальном времени через браузер.",
    "_cmd_doc_nochess": "[юзер] — Замутить шахматную партию в браузере",
    "_cmd_doc_ncstop": "— Вырубает NoChess сервер",
    "no_opponent": "Ошибка: укажи юзера через реплай или @username, бро.",
    "online": "Партия замутилась!",
    "starting": "Сервер мутится...",
    "already_running": "Сервер уже работает, не тупи.",
    "stopped": "Сервер вырублен.",
    "not_running": "Сервер не запущен.",
    "tunnel_error": "Serveo тунель крашнулся: <code>{}</code>",
    "open_button": "Открыть мини-апп",
    "stop_button": "Стопэ",
    "about_text": "<b>NoChess v2.0.0</b>\nПолноценные шахматы — мутишь партию, кидаешь ссылку, играешь в реалтайме.\nДвижок python-chess, без внешнего модуля Chess.\nПоддержка мата, пата, ничьи, сдачи, 3х повтора, 50 ходов, недостаточного материала.\nКоманды: <code>.nochess @user</code> кинуть вызов.",
    "server_starting": "<code>NoChess сервер мутится...</code>",
    "RuntimeError": "inline bot username not found",
    "not_supported_platform": "(T_T) К сожалению, установка этого модуля на данной платформе невозможна.\n\n(~)~ Это не ошибка, пожалуйста не обращайтесь в поддержку."
}

strings_uwu = {
    "name": "NoChess",
    "_cls_doc": "chess web moduwe. pway weaw-time chess in bwowsew~",
    "_cmd_doc_nochess": "[usew] — cweate a chess game in da bwowsew~",
    "_cmd_doc_ncstop": "— stop da NoChess sewvew~",
    "no_opponent": "oopsie: wepwy or @usewname to chawwenge pwease~",
    "online": "Game is wive!",
    "starting": "Sewvew booting...",
    "already_running": "Sewvew awweady wunning~",
    "stopped": "Sewvew stopped~",
    "not_running": "Sewvew not wunning~",
    "tunnel_error": "Sewveo tunnew-bun oopsie: <code>{}</code>",
    "open_button": "Open minyi-app~",
    "stop_button": "Stahp pwease",
    "about_text": "<b>NoChess v2.0.0</b>\nFuww chess — cweate game, shawe wink, pway weaw-time.\npython-chess engine, no extewnaw Chess moduwe.\nSuppowts checkmate, stalemate, dwaw, wesign, 3x wepetition, 50-move, insufficient matewiaw.\nCommands: <code>.nochess @usew</code> to chawwenge~",
    "server_starting": "<code>NoChess sewvew booting...</code>",
    "RuntimeError": "inwine bot usewname not found",
    "not_supported_platform": "(T_T) Unfowtunatewy, instawwation of dis moduwe on dis pwatfowm is impossibwe.\n\n(~)~ Dis is not an ewwow, pwease do not contact suppowt."
}


@loader.tds
class NoChessMod(loader.Module):
    strings = strings

    strings_ru = strings_ru
    strings_ua = strings_ua
    strings_de = strings_de
    strings_jp = strings_jp
    strings_leet = strings_leet
    strings_neofit = strings_neofit
    strings_tiktok = strings_tiktok
    strings_uwu = strings_uwu

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "serveo_subdomain",
                "",
                "Custom serveo subdomain (leave empty for random) | Кастомный поддомен serveo (оставь пустым для случайного)",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "mini_app_url",
                "",
                "Mini-app URL from BotFather (leave empty for serveo) | URL мини-приложения от BotFather (оставь пустым для serveo)",
                validator=loader.validators.String(),
            ),
        )
        self.runner = None
        self.tunnel_url = None
        self.access_token = None
        self.games = {}
        self._frontend_html = None
        self._serveo_proc = None

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        self._me = await client.get_me()

    async def refresh_games_cache(self):
        pass

    def ensure_access_token(self):
        if not self.access_token:
            self.access_token = secrets.token_hex(12)

    @staticmethod
    def _strip_ansi(text):
        return re.sub(r'\x1b\[[0-9;]*m', '', text)

    async def _kill_serveo(self):
        proc = self._serveo_proc
        if proc is None:
            return
        try:
            proc.kill()
        except ProcessLookupError:
            pass
        except Exception:
            pass
        try:
            await asyncio.wait_for(proc.wait(), timeout=3)
        except (asyncio.TimeoutError, Exception):
            pass
        self._serveo_proc = None

    async def stop_server(self):
        await self._kill_serveo()
        was_running = self.runner is not None
        if self.runner:
            try:
                await self.runner.cleanup()
            except Exception:
                pass
            self.runner = None
        self.tunnel_url = None
        self.access_token = None
        return was_running

    async def start_server(self, port):
        app = web.Application()
        app.router.add_get("/", self.handle_home)
        app.router.add_get("/ws/{game_id}", self.handle_ws)
        app.router.add_get("/api/game/{game_id}/legal", self.handle_legal)
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        await web.TCPSite(self.runner, "127.0.0.1", port).start()
        return port

    async def handle_home(self, request):
        if self._frontend_html is None:
            async with ClientSession() as sess:
                async with sess.get(FRONTEND_URL) as resp:
                    if resp.status == 200:
                        self._frontend_html = await resp.text()
                    else:
                        return web.Response(status=500, text="Failed to load frontend")
        return web.Response(body=self._frontend_html, content_type="text/html")

    def _make_game_state(self, game):
        board = game["board"]
        fen = board.fen()
        turn = "w" if board.turn else "b"
        moves = []
        for m in board.move_stack:
            moves.append(m.uci())
        in_check = board.is_check()
        return {
            "fen": fen,
            "turn": turn,
            "status": game.get("status", "playing"),
            "result": game.get("result"),
            "reason": game.get("reason"),
            "moves": moves,
            "white": game.get("white", ""),
            "black": game.get("black", ""),
            "in_check": in_check,
        }

    async def handle_legal(self, request):
        game_id = request.match_info["game_id"]
        square = request.query.get("square", "")
        game = self.games.get(game_id)
        if not game:
            return web.json_response({"moves": []}, status=404)
        legal = [m.uci() for m in game["board"].legal_moves]
        if square:
            legal = [m for m in legal if m.startswith(square)]
        return web.json_response({"moves": legal})

    async def handle_ws(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        game_id = request.match_info["game_id"]
        game = self.games.get(game_id)
        if not game:
            await ws.send_json({"type": "error", "message": "Game not found"})
            await ws.close()
            return ws
        try:
            auth_msg = await asyncio.wait_for(ws.receive(), timeout=10)
            if auth_msg.type != WSMsgType.TEXT:
                await ws.close(code=4003)
                return ws
            try:
                auth_data = json.loads(auth_msg.data)
            except json.JSONDecodeError:
                await ws.close(code=4003)
                return ws
            if auth_data.get("type") != "auth":
                await ws.close(code=4003)
                return ws
            init_data = auth_data.get("initData", "")
            player_id = None
            if init_data:
                from urllib.parse import parse_qs
                parsed = parse_qs(init_data)
                user_json = parsed.get("user", ["{}"])[0]
                try:
                    user = json.loads(user_json)
                    player_id = str(user.get("id", ""))
                except Exception:
                    pass
            if not player_id:
                player_id = auth_data.get("playerId", "")
            white_id = str(game.get("white_id", ""))
            black_id = str(game.get("black_id", ""))
            if player_id and player_id not in (white_id, black_id):
                await ws.close(code=4003)
                return ws
            if player_id == white_id:
                await ws.send_json({"type": "auth_ok", "color": "white"})
            elif player_id == black_id:
                await ws.send_json({"type": "auth_ok", "color": "black"})
        except asyncio.TimeoutError:
            await ws.close(code=4003)
            return ws
        game["clients"].add(ws)
        try:
            gs = self._make_game_state(game)
            await ws.send_json({"type": "game_state", "game": gs})
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                    except json.JSONDecodeError:
                        continue
                    if data.get("type") == "move":
                        try:
                            move = chess.Move.from_uci(data["uci"])
                            if move not in game["board"].legal_moves:
                                await ws.send_json({"type": "illegal", "uci": data["uci"]})
                                continue
                            game["board"].push(move)
                            board = game["board"]
                            game["status"] = "playing"
                            game["result"] = None
                            game["reason"] = None
                            outcome = board.outcome()
                            if outcome:
                                if outcome.winner is not None:
                                    game["status"] = "finished"
                                    game["result"] = "1-0" if outcome.winner else "0-1"
                                    game["reason"] = "checkmate"
                                else:
                                    game["status"] = "finished"
                                    game["result"] = "1/2-1/2"
                                    game["reason"] = "stalemate" if board.is_stalemate() else (
                                        "insufficient" if board.is_insufficient_material() else (
                                            "fifty_moves" if board.is_fifty_moves() else (
                                                "threefold" if board.is_repetition(3) else "draw"
                                            )
                                        )
                                    )
                            gs = self._make_game_state(game)
                            broadcast_msg = {"type": "game_state", "game": gs}
                            if game["status"] == "finished":
                                broadcast_msg = {"type": "game_over", "result": game["result"], "reason": game.get("reason", "")}
                        except Exception:
                            await ws.send_json({"type": "illegal", "uci": data.get("uci", "")})
                            continue
                    elif data.get("type") == "resign":
                        game["status"] = "finished"
                        game["result"] = "0-1" if game["board"].turn else "1-0"
                        game["reason"] = "resign"
                        broadcast_msg = {"type": "game_over", "result": game["result"], "reason": "resign"}
                    elif data.get("type") == "draw":
                        game["status"] = "finished"
                        game["result"] = "1/2-1/2"
                        game["reason"] = "agreement"
                        broadcast_msg = {"type": "game_over", "result": game["result"], "reason": "agreement"}
                    else:
                        continue
                    gs2 = self._make_game_state(game)
                    for client in list(game["clients"]):
                        if not client.closed:
                            try:
                                if client is ws:
                                    await client.send_json({"type": "game_state", "game": gs2})
                                else:
                                    await client.send_json(broadcast_msg)
                            except Exception:
                                pass
                elif msg.type == WSMsgType.ERROR:
                    pass
        except Exception:
            pass
        finally:
            game["clients"].discard(ws)
        return ws

    async def _start_serveo(self, port):
        await self._kill_serveo()
        subdomain = (self.config["serveo_subdomain"] or "").strip()
        if subdomain:
            remote = f"{subdomain}:80:localhost:{port}"
        else:
            remote = f"80:localhost:{port}"
        cmd = [
            "ssh", "-T",
            "-o", "StrictHostKeyChecking=accept-new",
            "-o", "ServerAliveInterval=60",
            "-o", "ExitOnForwardFailure=yes",
            "-o", "ConnectTimeout=15",
            "-R", remote,
            "serveo.net",
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        self._serveo_proc = proc
        url = None
        deadline = asyncio.get_event_loop().time() + 20
        buf = b""
        while asyncio.get_event_loop().time() < deadline:
            try:
                line = await asyncio.wait_for(proc.stdout.readline(), timeout=0.5)
            except asyncio.TimeoutError:
                if proc.returncode is not None:
                    buf_str = self._strip_ansi(buf.decode(errors="replace"))
                    raise RuntimeError(f"SSH exited {proc.returncode}: {buf_str}")
                continue
            if not line:
                if proc.returncode is not None:
                    buf_str = self._strip_ansi(buf.decode(errors="replace"))
                    raise RuntimeError(f"SSH exited {proc.returncode}: {buf_str}")
                await asyncio.sleep(0.5)
                continue
            buf += line
            line_str = self._strip_ansi(line.decode(errors="replace"))
            match = re.search(r'https?://[\w.-]+\.serveo(?:usercontent)?\.(?:net|com)', line_str)
            if match:
                url = match.group(0).rstrip("/")
                break
        if not url:
            buf_str = self._strip_ansi(buf.decode(errors="replace"))
            raise RuntimeError(f"No serveo URL received: {buf_str}")
        return url

    async def _auto_cma(self):
        try:
            from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl
            bot_username = (await self.inline.bot.get_me()).username
            bot_username = (bot_username or "").strip().lstrip("@")
            if not bot_username:
                return None
            web_url = (self.tunnel_url or "").strip()
            if not web_url or "t.me/" in web_url:
                return None
            token = self.access_token
            parsed = urlsplit(web_url)
            query = dict(parse_qsl(parsed.query, keep_blank_values=True))
            query["token"] = token
            web_url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), parsed.fragment))
            await self._client.send_message("@BotFather", "/cancel")
            await asyncio.sleep(0.9)
            async with self._client.conversation("@BotFather", timeout=120) as conv:
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
                await conv.send_message("NoChess")
                await conv.get_response()
            direct_link = f"https://t.me/{bot_username}/NoChess"
            self.config["mini_app_url"] = direct_link
            return direct_link
        except Exception:
            return None

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
        self.games.clear()
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

    def _new_game_id(self):
        return secrets.token_hex(16)

    @loader.command(
        ru_doc="[юзер] — создать шахматную партию через браузер",
        ua_doc="[юзер] — створити шахову партію через браузер",
        de_doc="[user] — Schachpartie im Browser starten",
        jp_doc="[ユーザー] — ブラウザでチェスの対局を作成",
        leet_doc="[us3r] — cr34t3 ch3ss g4m3 v14 br0ws3r",
        neofit_doc="[user] — link up a chess game in the browser innit",
        tiktok_doc="[юзер] — Замутить шахматную партию в браузере",
        uwu_doc="[usew] — cweate a chess game in da bwowsew~",
    )
    async def nochess(self, message):
        try:
            return await self._nochess_run(message)
        except Exception as error:
            await self.stop_server()
            return await utils.answer(
                message,
                self.strings["tunnel_error"].format(utils.escape_html(str(error))),
            )

    async def _nochess_run(self, message):
        opponent = None
        opponent_name = None
        if message.is_reply:
            reply = await message.get_reply_message()
            if reply and getattr(reply, "sender_id", None):
                opponent = reply.sender_id
                ent = await self._client.get_entity(opponent)
                opponent_name = getattr(ent, "first_name", None) or str(opponent)
        else:
            args = utils.get_args_raw(message)
            if args:
                try:
                    ent = await self._client.get_entity(args)
                    opponent = ent.id
                    opponent_name = getattr(ent, "first_name", None) or str(opponent)
                except Exception:
                    await utils.answer(message, self.strings["no_opponent"])
                    return
        if opponent is None:
            await utils.answer(message, self.strings["no_opponent"])
            return

        my_name = (
            getattr(self._me, "first_name", None)
            or getattr(self._me, "username", None)
            or str(getattr(self._me, "id", "?"))
        )

        if not self.runner:
            await utils.answer(message, self.strings["starting"])
            self.ensure_access_token()
            sock = socket.socket()
            sock.bind(("", 0))
            port = sock.getsockname()[1]
            sock.close()
            await self.start_server(port)
            try:
                self.tunnel_url = await self._start_serveo(port)
            except Exception as error:
                await self.stop_server()
                return await utils.answer(
                    message,
                    self.strings["tunnel_error"].format(utils.escape_html(str(error))),
                )
        elif message.is_reply:
            await utils.answer(message, self.strings["already_running"])

        mini_url = (self.config["mini_app_url"] or "").strip()
        if not mini_url:
            await self._auto_cma()

        game_id = self._new_game_id()
        board = chess.Board()
        my_id = str(getattr(self._me, "id", ""))
        self.games[game_id] = {
            "board": board,
            "status": "playing",
            "result": None,
            "reason": None,
            "clients": set(),
            "white": my_name,
            "black": opponent_name,
            "white_id": my_id,
            "black_id": str(opponent),
            "created_at": int(time.time()),
        }

        mini_url = (self.config["mini_app_url"] or "").strip().rstrip("/")
        if mini_url.startswith("https://t.me/"):
            game_url = f"{mini_url}?startapp={game_id}"
        else:
            game_url = f"{self.tunnel_url}/?game={game_id}"
        await self.send_form(message, game_url)

    @loader.command(
        ru_doc="Останавливает сервер NoChess",
        ua_doc="Зупиняє сервер NoChess",
        de_doc="Stoppt den NoChess-Server",
        jp_doc="NoChessサーバーを停止します",
        leet_doc="St0p5 N0Ch3ss s3rv3r",
        neofit_doc="Shuts down NoChess server",
        tiktok_doc="Вырубает NoChess сервер",
        uwu_doc="Stops da NoChess sewvew~",
    )
    async def ncstopcmd(self, message):
        was_running = await self.stop_server()
        self.games.clear()
        await utils.answer(message, self.strings["stopped"] if was_running else self.strings["not_running"])

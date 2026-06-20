# meta developer: @sepiol026-wq
# requires: python-chess aiohttp>=3.8.0
# scope: hikka_only
# meta pic: https://img.icons8.com/color/480/chess.png

__version__ = (1, 0, 0)

import asyncio
import chess
import html
import json
import logging
import os
import secrets
import socket
import subprocess
import time
from pathlib import Path

from aiohttp import web, WSMsgType

from .. import loader, utils

logger = logging.getLogger(__name__)

MOD_DIR = Path(__file__).parent

strings_ua = {
    "game_created": "🎮 <b>NoChess</b>\n\nПартія створена!\n\n🔗 <a href=\"{}\">{}</a>\n\nВідкрий посилання щоб грати.",
    "game_created_opponent": "🎮 <b>NoChess</b>\n\n{} викликав {} на партію!\n\n🔗 <a href=\"{}\">{}</a>\n\nОбидва гравці відкрийте посилання.",
    "no_opponent": "❌ Вкажи юзера через реплай або @username.",
    "no_server": "❌ Сервер не запущений. Спершу створи гру через <code>.nochess</code>.",
    "server_starting": "⏳ Запускаю сервер...",
    "server_already_running": "⚠️ Сервер вже працює: {}",
    "game_not_found": "❌ Гру не знайдено.",
    "asset_read_error": "❌ Помилка завантаження: {}",
    "declined": "🚫 Запрошення відхилено.",
    "check": "Шах!",
    "checkmate": "Мат! {} переміг.",
    "stalemate": "Пат! Нічия.",
    "draw": "Нічия.",
    "insufficient": "Недостатньо матеріалу. Нічия.",
    "threefold": "Триразове повторення. Нічия.",
    "fifty_moves": "50 ходів без взяття. Нічия.",
    "resigned": "{} здався. {} переміг.",
}

strings_en = {
    "game_created": "🎮 <b>NoChess</b>\n\nGame created!\n\n🔗 <a href=\"{}\">{}</a>\n\nOpen the link to play.",
    "game_created_opponent": "🎮 <b>NoChess</b>\n\n{} challenged {}!\n\n🔗 <a href=\"{}\">{}</a>\n\nBoth players open the link.",
    "no_opponent": "❌ Specify a user via reply or @username.",
    "no_server": "❌ Server not running. Create a game first with <code>.nochess</code>.",
    "server_starting": "⏳ Starting server...",
    "server_already_running": "⚠️ Server already running: {}",
    "game_not_found": "❌ Game not found.",
    "asset_read_error": "❌ Load error: {}",
    "declined": "🚫 Invitation declined.",
    "check": "Check!",
    "checkmate": "Checkmate! {} wins.",
    "stalemate": "Stalemate! Draw.",
    "draw": "Draw.",
    "insufficient": "Insufficient material. Draw.",
    "threefold": "Threefold repetition. Draw.",
    "fifty_moves": "50 moves without capture. Draw.",
    "resigned": "{} resigned. {} wins.",
}


@loader.tds
class NoChessMod(loader.Module):
    strings_ua = strings_ua
    strings_en = strings_en

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "default_time",
                300,
                "Default game time in seconds (0 = no timer)",
                validator=loader.validators.Integer(minimum=0),
            ),
            loader.ConfigValue(
                "block_light",
                "#D8E3E7",
                "Light block color",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "block_dark",
                "#7699AF",
                "Dark block color",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "select_block",
                "#FFDF5A",
                "Select block color",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "move_pieces_color",
                "#58B4FF",
                "Move pieces color",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "result_win",
                "#00BE16",
                "Result win color",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "result_lose",
                "#BE0000",
                "Result lose color",
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "result_draw",
                "#434343",
                "Result draw color",
                validator=loader.validators.String(),
            ),
        )
        self.games = {}
        self.runner = None
        self.tunnel_url = None
        self.app = None
        self._serveo_proc = None
        self._static_path = MOD_DIR / "frontend" / "out"

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        self._me = await client.get_me()

    def _get_serializable_game(self, game_id):
        g = self.games.get(game_id)
        if not g:
            return None
        board = g["board"]
        return {
            "id": game_id,
            "fen": board.fen(),
            "turn": "w" if board.turn == chess.WHITE else "b",
            "moves": [m.uci() for m in board.move_stack],
            "status": g["status"],
            "result": g.get("result"),
            "reason": g.get("reason"),
            "white": g.get("white"),
            "black": g.get("black"),
            "time_white": g.get("time_white"),
            "time_black": g.get("time_black"),
        }

    async def broadcast_game(self, game_id):
        g = self.games.get(game_id)
        if not g:
            return
        state = self._get_serializable_game(game_id)
        dead = set()
        for ws in g.get("clients", set()):
            try:
                await ws.send_json({"type": "game_state", "game": state})
            except Exception:
                dead.add(ws)
        g["clients"] -= dead

    def _game_over_reason(self, board):
        if board.is_checkmate():
            return "checkmate"
        if board.is_stalemate():
            return "stalemate"
        if board.is_insufficient_material():
            return "insufficient"
        if board.is_fivefold_repetition() or board.is_repetition(3):
            return "threefold"
        if board.is_fifty_moves():
            return "fifty_moves"
        if board.can_claim_draw():
            return "draw"
        return None

    async def handle_move(self, game_id, uci):
        g = self.games.get(game_id)
        if not g:
            return
        if g["status"] != "playing":
            return
        board = g["board"]
        try:
            move = chess.Move.from_uci(uci)
        except ValueError:
            return
        if move not in board.legal_moves:
            return
        board.push(move)
        reason = self._game_over_reason(board)
        if reason:
            g["status"] = "finished"
            g["reason"] = reason
            if reason == "checkmate":
                loser = "white" if board.turn == chess.WHITE else "black"
                winner = "black" if loser == "white" else "white"
                g["result"] = "1-0" if winner == "white" else "0-1"
            else:
                g["result"] = "1/2-1/2"
        await self.broadcast_game(game_id)

    async def ws_handler(self, request):
        ws = web.WebSocketResponse(max_msg_size=1024)
        await ws.prepare(request)
        game_id = request.match_info["game_id"]
        g = self.games.get(game_id)
        if not g:
            await ws.send_json({"type": "error", "message": self.strings["game_not_found"]})
            await ws.close()
            return ws
        g.setdefault("clients", set()).add(ws)
        try:
            state = self._get_serializable_game(game_id)
            await ws.send_json({"type": "game_state", "game": state})
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                    except json.JSONDecodeError:
                        continue
                    if data.get("type") == "move":
                        await self.handle_move(game_id, data.get("uci", ""))
                elif msg.type == WSMsgType.ERROR:
                    logger.error("WS error: %s", ws.exception())
        finally:
            g.get("clients", set()).discard(ws)
        return ws

    async def handle_api_game(self, request):
        game_id = request.match_info["game_id"]
        state = self._get_serializable_game(game_id)
        if not state:
            return web.json_response({"error": "not found"}, status=404)
        return web.json_response(state)

    async def handle_api_turn(self, request):
        game_id = request.match_info["game_id"]
        g = self.games.get(game_id)
        if not g:
            return web.json_response({"error": "not found"}, status=404)
        board = g["board"]
        try:
            data = await request.json()
            uci = data.get("uci")
            move = chess.Move.from_uci(uci)
        except (ValueError, json.JSONDecodeError, TypeError):
            return web.json_response({"error": "invalid move"}, status=400)
        if move not in board.legal_moves:
            return web.json_response({"error": "illegal move"}, status=400)
        board.push(move)
        reason = self._game_over_reason(board)
        if reason:
            g["status"] = "finished"
            g["reason"] = reason
            if reason == "checkmate":
                loser = "white" if board.turn == chess.WHITE else "black"
                winner = "black" if loser == "white" else "white"
                g["result"] = "1-0" if winner == "white" else "0-1"
            else:
                g["result"] = "1/2-1/2"
        await self.broadcast_game(game_id)
        return web.json_response(self._get_serializable_game(game_id))

    async def handle_api_legal_moves(self, request):
        game_id = request.match_info["game_id"]
        g = self.games.get(game_id)
        if not g:
            return web.json_response({"error": "not found"}, status=404)
        square = request.query.get("square", "")
        board = g["board"]
        try:
            sq = chess.parse_square(square) if len(square) == 2 else None
        except ValueError:
            sq = None
        if sq is None:
            return web.json_response({"moves": []})
        moves = [m.uci() for m in board.legal_moves if m.from_square == sq]
        return web.json_response({"square": square, "moves": moves})

    async def handle_index(self, request):
        index_file = self._static_path / "index.html"
        if index_file.is_file():
            return web.FileResponse(index_file)
        return web.Response(text="NoChess frontend not built", status=500)

    def build_app(self):
        app = web.Application()
        app.router.add_get("/", self.handle_index)
        app.router.add_get("/ws/{game_id}", self.ws_handler)
        app.router.add_get("/api/game/{game_id}", self.handle_api_game)
        app.router.add_post("/api/game/{game_id}/move", self.handle_api_turn)
        app.router.add_get("/api/game/{game_id}/legal", self.handle_api_legal_moves)
        return app

    def _find_free_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()
        return port

    async def start_server(self):
        if self.runner:
            return
        port = self._find_free_port()
        self.app = self.build_app()
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, "127.0.0.1", port)
        await site.start()
        return port

    async def stop_server(self):
        await self._kill_serveo()
        if self.runner:
            await self.runner.cleanup()
            self.runner = None
        self.app = None

    async def _kill_serveo(self):
        proc = self._serveo_proc
        if proc and proc.returncode is None:
            try:
                proc.terminate()
                try:
                    await asyncio.wait_for(proc.wait(), timeout=3)
                except asyncio.TimeoutError:
                    proc.kill()
                    await proc.wait()
            except ProcessLookupError:
                pass
        self._serveo_proc = None
        self.tunnel_url = None

    async def _start_serveo(self, port):
        await self._kill_serveo()
        self._serveo_proc = await asyncio.create_subprocess_exec(
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null",
            "-o", "ExitOnForwardFailure=yes",
            "-R", f"80:localhost:{port}",
            "serveo.net",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
        for _ in range(200):
            line = await self._serveo_proc.stdout.readline()
            if not line:
                break
            decoded = line.decode()
            for word in decoded.split():
                if ".serveo.net" in word or ".serveo." in word:
                    self.tunnel_url = "https://" + word.strip()
                    return self.tunnel_url
        if self._serveo_proc.returncode is not None:
            raise RuntimeError("Serveo exited")
        raise RuntimeError("Timeout waiting for serveo URL")

    def _new_game_id(self):
        return secrets.token_hex(16)

    @loader.command()
    async def nochess(self, message):
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

        my_name = (
            getattr(self._me, "first_name", None)
            or getattr(self._me, "username", None)
            or str(getattr(self._me, "id", "?"))
        )

        if not self.runner:
            await utils.answer(message, self.strings["server_starting"])
            port = await self.start_server()
            await self._start_serveo(port)

        game_id = self._new_game_id()
        board = chess.Board()
        self.games[game_id] = {
            "board": board,
            "status": "playing",
            "result": None,
            "reason": None,
            "clients": set(),
            "white": my_name,
            "black": opponent_name,
            "created_at": int(time.time()),
        }

        game_url = f"{self.tunnel_url}/?game={game_id}"
        if opponent:
            text = self.strings["game_created_opponent"].format(
                utils.escape_html(my_name),
                utils.escape_html(opponent_name or str(opponent)),
                game_url,
                game_url,
            )
        else:
            text = self.strings["game_created"].format(game_url, game_url)
        await utils.answer(message, text)

    @loader.command()
    async def nchess(self, message):
        await self.nochess(message)

    @loader.command()
    async def nochess_stop(self, message):
        await self.stop_server()
        self.games.clear()
        await utils.answer(message, "🛑 NoChess server stopped.")

    @loader.command()
    async def nchess_stop(self, message):
        await self.nochess_stop(message)

    @loader.unrestricted_loop(interval=300, autostart=True)
    async def cleanup_loop(self):
        now = int(time.time())
        to_delete = []
        for game_id, g in self.games.items():
            age = now - g["created_at"]
            if g["status"] == "finished" and age > 3600:
                to_delete.append(game_id)
            elif age > 86400:
                to_delete.append(game_id)
        for game_id in to_delete:
            self.games.pop(game_id, None)
        if not self.games and self.runner:
            await self.stop_server()

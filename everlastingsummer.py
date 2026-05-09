# meta developer: @H_SunMods
#meta banner: https://i.ibb.co/LdN9FXjc/logo.webp
# __version__ 
__version__ = ("alpha", "1.0", 0)

import asyncio
import copy
import json
from urllib.request import Request, urlopen
from herokutl.types import Message
from .. import loader, utils
from ..types import InlineCall


prologue_dialogs_url = "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/Everlasting_Summer/ddialogs/prologue_only.json"
routes_url = "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/Everlasting_Summer/ddialogs/routes_prologue.json"
menu_background_url = "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/Everlasting_Summer/images/1920/in_telegram_images/Start_Menu.jpg"
save_background_url = "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/Everlasting_Summer/images/1920/in_telegram_images/Save_Menu.png"


@loader.tds
class EverlastingSummer(loader.Module):
    """Встретив Семёна, главного героя игры, вы никогда бы не обратили на него внимания. Просто обычный молодой человек среди тысяч, даже сотен тысяч таких, как он, в каждом обычном городе. Но однажды с ним происходит нечто совершенно необычное: он засыпает в автобусе зимой и просыпается... посреди жаркого лета. Перед ним - "Совёнок" - пионерский лагерь, а за ним - его прежняя жизнь. Чтобы понять, что с ним произошло, Семёну придется познакомиться с местными жителями (и, возможно, даже найти любовь), сориентироваться в сложном лабиринте человеческих отношений и своих собственных проблем, а также разгадать тайны лагеря. И ответить на главный вопрос - как вернуться? Стоит ли ему возвращаться?"""
    strings = {
        "name": "EverlastingSummer",
        "menu": "<b>Пролог</b>",
        "disclaimer": (
            "Игра является плодом фантазии её разработчиков\n"
            "и не ставит перед собой цели затронуть или иным\n"
            "образом оскорбить кого-либо по религиозному,расовому,\n"
            "социальному, экономическому или видовому признаку.\n"
            "Также любое ущемление чувства прекрасного, активной\n"
            "гражданской позиции или иных высоких душевных порывов\n"
            "игроков разработчики оставляют на их совести.\n"
            "Совпадения героев с вашими реальными (и воображаемыми)\n"
            "знакомыми,соседями,коллегами, тульпами считать случайным.\n"
            "Все героини достигли восемнадцатилетнего возраста,\n"
            "и они дали письменное согласие на участие в игре\n"
            "(выписка из истории болезни сценариста предоставляется по требованию).\n"
            "При разработке не пострадало ни одного маскота, животного или человека. Приятной игры!"
        ),
        "bad": "<b>Не удалось загрузить сценарий</b>",
        "end": "<b>{}</b>",
        "save_header": "<b>Сохранения</b>",
        "load_header": "<b>Загрузить игру</b>",
        "default_route_question": "<b>Что выберете?</b>",
        "or_game": "Игра",
        "or_character": "Персонаж",
        "cutscene_text": "<tg-emoji emoji-id=5332542518955374404>💫</tg-emoji>",
        "opening_title": "<b>Опенинг</b>",
        "opening_next": "Пропустить опенинг",
        "saved": "игра сохранена в слот № {}",
        "loaded": "Сохранение № {} загружено",
        "empty": "Слот {} пуст",
        "rewrite": "Слот {} уже занят. Перезаписать?",
        "state_slots_from_menu": "slots_from_menu",
        "chapter_prologue": "prologue",
        "save_action": "save",
        "load_action": "load",
        "mode_ask_rewrite": "ask_rewrite",
        "mode_ended": "ended",
        "mode_menu": "menu",
        "mode_play": "play",
        "mode_slots": "slots",
        "type_label": "label",
        "type_jump": "jump",
        "type_scene": "scene",
        "type_dialogue": "dialogue",
        "type_narration": "narration",
        "type_route": "route",
        "type_opening": "opening",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(loader.ConfigValue("cut_speed", 3))
        self.dialogs_url = prologue_dialogs_url
        self.routes_url = routes_url
        self.menu_image = menu_background_url
        self.save_image = save_background_url
        self.dialogs_data = None
        self.routes_data = None
        self.label_index = {}

    async def json_load(self, url: str):
        last_error = None
        for i in range(3):
            try:
                def run():
                    req = Request(url, headers={"User-Agent": "Mozilla/5.0 HSunMods"})
                    with urlopen(req, timeout=60) as x:
                        return json.loads(x.read().decode("utf-8"))
                return await asyncio.to_thread(run)
            except Exception as e:
                last_error = e
                if i < 2:
                    await asyncio.sleep(1.5 * (i + 1))
        raise last_error

    async def load_data(self, force: bool = False):
        if self.dialogs_data is not None and self.routes_data is not None and not force:
            return True
        try:
            self.dialogs_data = await self.json_load(self.dialogs_url)
            self.routes_data = await self.json_load(self.routes_url)
        except Exception:
            return False

        prologue_nodes = self.dialogs_data.get(self.strings["chapter_prologue"])
        if not isinstance(prologue_nodes, list):
            return False
        self.dialogs_data = {self.strings["chapter_prologue"]: prologue_nodes}

        self.label_index = {}
        for node_index, node in enumerate(prologue_nodes):
            if isinstance(node, dict) and node.get("type") == self.strings["type_label"]:
                self.label_index[node.get("name")] = (self.strings["chapter_prologue"], node_index)
        return True

    def state_get(self):
        return self.get(
            "state",
            {
                "mode": self.strings["mode_menu"],
                "chapter": self.strings["chapter_prologue"],
                "idx": 0,
                "pending": None,
                "scene": {},
                "vars": {},
            },
        )

    def state_set(self, state_data):
        self.set("state", state_data)

    def slots_get(self):
        return self.get("slots", {})

    def slots_set(self, slots_data):
        self.set("slots", slots_data)

    async def ui(self, target, text, kb=None, photo=None):
        if isinstance(target, InlineCall):
            if photo:
                try:
                    return await target.edit(text, reply_markup=kb, photo=photo)
                except TypeError:
                    try:
                        return await target.edit(text, reply_markup=kb, file=photo)
                    except Exception:
                        pass
                except Exception:
                    pass
            try:
                return await target.edit(text, reply_markup=kb)
            except Exception:
                raise
        if photo:
            try:
                return await utils.answer(target, text, reply_markup=kb, photo=photo)
            except Exception:
                pass
        return await utils.answer(target, text, reply_markup=kb)

    def menu_kb(self):
        return [
            [{"text": "Начать пролог", "callback": self.new_game}],
            [{"text": "Сохранения", "callback": self.save_menu, "args": (self.strings["load_action"],)}],
            [{"text": "Дисклеймер", "callback": self.disclaimer_msg}],
        ]

    def start_kb(self):
        return [
            [{"text": "➤", "callback": self.next_step}],
            [{"text": "Сохранить", "callback": self.save_menu, "args": (self.strings["save_action"],)}],
            [{"text": "Меню", "callback": self.menu}],
        ]

    def save_kb(self, mode: str):
        slots = self.slots_get()
        row = []
        for i in range(1, 6):
            k = str(i)
            b = {"text": k, "callback": self.save_action, "args": (mode, i)}
            if k in slots:
                b["style"] = "success"
            row.append(b)
        return [row, [{"text": "Назад", "callback": self.back_from_saves}]]

    def choice_kb(self, route_id: str):
        opts = self.routes_data.get(route_id, {}).get("options", {})
        rows = []
        for i, txt in enumerate(opts.keys()):
            rows.append([{"text": txt, "callback": self.pick_option, "args": (route_id, i)}])
        rows.append([{"text": "Сохранить", "callback": self.save_menu, "args": (self.strings["save_action"],)}])
        rows.append([{"text": "Меню", "callback": self.menu}])
        return rows

    def opening_kb(self):
        return [[{"text": self.strings["opening_next"], "callback": self.opening_done}]]

    def state_preservation(self, state_data):
        return {
            "chapter": state_data.get("chapter"),
            "idx": state_data.get("idx", 0),
            "part": state_data.get("part", 0),
            "pending": copy.deepcopy(state_data.get("pending")),
            "scene": copy.deepcopy(state_data.get("scene")),
            "vars": copy.deepcopy(state_data.get("vars", {})),
            "mode": self.strings["mode_play"],
        }

    def scene_photo(self, state_data):
        u = (state_data.get("scene") or {}).get("raw_url")
        return u if isinstance(u, str) else None

    def wait_text(self, t: str):
        return [x.strip() for x in t.split("{w}") if x.strip()] or [t]

    def render_dialogs(self, state_data):
        pending_node = state_data.get("pending") or {}
        if pending_node.get("type") == self.strings["type_dialogue"]:
            who = (pending_node.get("character") or pending_node.get("char_id") or self.strings["or_character"]).strip()
            txt = " ".join(pending_node.get("parts", [])[: pending_node.get("part", 1)])
            return f"<b>{who}:</b>\n<blockquote>{txt}</blockquote>"
        if pending_node.get("type") == self.strings["type_narration"]:
            return " ".join(pending_node.get("parts", [])[: pending_node.get("part", 1)])
        return ""

    def is_ending_label(self, name: str):
        return name in self.routes_data.get("endings", {}).get("labels", [])

    async def go(self, target, state_data):
        cut_scene_speed_fallback = self.config["cut_speed"]
        while True:
            chapter_nodes = self.dialogs_data.get(self.strings["chapter_prologue"], [])
            node_index = state_data.get("idx", 0)
            if node_index >= len(chapter_nodes):
                ending_name = self.routes_data.get("endings", {}).get("fallback", "main_bad_ending")
                state_data["mode"] = self.strings["mode_ended"]
                state_data["ending"] = ending_name
                self.state_set(state_data)
                await self.ui(target, self.strings["end"].format(ending_name), self.menu_kb(), self.scene_photo(state_data))
                return

            current_node = chapter_nodes[node_index]
            node_type = current_node.get("type")

            if node_type == self.strings["type_label"]:
                if self.is_ending_label(current_node.get("name")):
                    state_data["mode"] = self.strings["mode_ended"]
                    state_data["ending"] = current_node.get("name")
                    self.state_set(state_data)
                    await self.ui(target, self.strings["end"].format(current_node.get("name")), self.menu_kb(), self.scene_photo(state_data))
                    return
                state_data["idx"] = node_index + 1
                continue

            if node_type == self.strings["type_jump"]:
                jump_target = self.label_index.get(current_node.get("label"))
                if jump_target:
                    state_data["chapter"], state_data["idx"] = jump_target
                else:
                    state_data["idx"] = node_index + 1
                continue

            if node_type == self.strings["type_scene"]:
                state_data["scene"] = {
                    "raw_url": current_node.get("raw_url"),
                    "location": current_node.get("location"),
                    "action": current_node.get("action"),
                    "kind": current_node.get("kind"),
                    "name": current_node.get("name"),
                }
                state_data["idx"] = node_index + 1
                next_node = chapter_nodes[state_data["idx"]] if state_data["idx"] < len(chapter_nodes) else None
                if isinstance(next_node, dict) and next_node.get("type") == self.strings["type_scene"]:
                    scene_duration = current_node.get("duration")
                    if scene_duration is None:
                        if cut_scene_speed_fallback is None:
                            scene_delay_seconds = 0.0
                        else:
                            try:
                                scene_delay_seconds = float(cut_scene_speed_fallback)
                            except Exception:
                                scene_delay_seconds = 0.0
                    else:
                        try:
                            scene_delay_seconds = float(scene_duration)
                        except Exception:
                            scene_delay_seconds = 0.0
                    if scene_delay_seconds < 0:
                        scene_delay_seconds = 0.0
                    self.state_set(state_data)
                    await self.ui(target, self.strings["cutscene_text"], None, self.scene_photo(state_data))
                    if scene_delay_seconds > 0:
                        await asyncio.sleep(scene_delay_seconds)
                    continue
                continue

            if node_type in {self.strings["type_dialogue"], self.strings["type_narration"]}:
                state_data["pending"] = {
                    "type": node_type,
                    "parts": self.wait_text(current_node.get("text", "")),
                    "part": 1,
                    "char_id": current_node.get("char_id"),
                    "character": current_node.get("character"),
                }
                state_data["mode"] = self.strings["mode_play"]
                self.state_set(state_data)
                await self.ui(target, self.render_dialogs(state_data), self.start_kb(), self.scene_photo(state_data))
                return

            if node_type == self.strings["type_route"]:
                route_id = current_node.get("id")
                route_question = self.routes_data.get(route_id, {}).get("question") or self.strings["default_route_question"]
                state_data["pending"] = {"type": self.strings["type_route"], "id": route_id}
                state_data["mode"] = self.strings["mode_play"]
                self.state_set(state_data)
                await self.ui(target, route_question, self.choice_kb(route_id), self.scene_photo(state_data))
                return

            if node_type == self.strings["type_opening"] or (node_type == self.strings["type_label"] and current_node.get("kind") == self.strings["type_opening"]):
                state_data["scene"] = {
                    "raw_url": current_node.get("raw_url"),
                    "location": current_node.get("location"),
                    "action": current_node.get("action"),
                    "kind": current_node.get("kind") or self.strings["type_opening"],
                    "name": current_node.get("name") or self.strings["type_opening"],
                }
                state_data["pending"] = {"type": self.strings["type_opening"]}
                state_data["mode"] = self.strings["mode_play"]
                state_data["idx"] = node_index + 1
                self.state_set(state_data)
                await self.ui(target, self.strings["opening_title"], self.opening_kb(), self.scene_photo(state_data))
                return

            state_data["idx"] = node_index + 1

    async def menu(self, call: InlineCall):
        state = self.state_get()
        state["mode"] = self.strings["mode_menu"]
        state["pending"] = None
        self.state_set(state)
        await self.ui(call, self.strings["menu"], self.menu_kb(), self.menu_image)

    async def disclaimer_msg(self, call: InlineCall):
        await self.ui(call, self.strings["disclaimer"], [[{"text": "Назад", "callback": self.menu}]], self.menu_image)

    async def new_game(self, call: InlineCall):
        ok = await self.load_data(force=False)
        if not ok:
            await call.answer(self.strings["bad"], show_alert=True)
            return
        state = self.state_get()
        state.update(
            {
                "chapter": self.strings["chapter_prologue"],
                "idx": 0,
                "part": 0,
                "pending": None,
                "scene": {},
                "vars": {},
                "mode": self.strings["mode_play"],
            }
        )
        self.state_set(state)
        await self.go(call, state)

    async def next_step(self, call: InlineCall):
        state = self.state_get()
        pending_node = state.get("pending") or {}
        if pending_node.get("type") == self.strings["type_opening"]:
            await self.menu(call)
            return
        if pending_node.get("type") in {self.strings["type_dialogue"], self.strings["type_narration"]}:
            if pending_node.get("part", 1) < len(pending_node.get("parts", [])):
                pending_node["part"] += 1
                state["pending"] = pending_node
                self.state_set(state)
                await self.ui(call, self.render_dialogs(state), self.start_kb(), self.scene_photo(state))
                return
            state["idx"] += 1
            state["pending"] = None
            self.state_set(state)
            await self.go(call, state)
            return
        await self.go(call, state)

    async def opening_done(self, call: InlineCall):
        state = self.state_get()
        state["pending"] = None
        state["mode"] = self.strings["mode_menu"]
        self.state_set(state)
        await self.menu(call)

    async def pick_option(self, call: InlineCall, route_id: str, option_index: int):
        state = self.state_get()
        option_items = list((self.routes_data.get(route_id, {}).get("options") or {}).items())
        if option_index < 0 or option_index >= len(option_items):
            return
        _, option_data = option_items[option_index]
        jump_label = option_data.get("jump")
        if jump_label and jump_label in self.label_index:
            state["chapter"], state["idx"] = self.label_index[jump_label]
        else:
            state["idx"] += 1
        state["pending"] = None
        self.state_set(state)
        await self.go(call, state)

    async def save_menu(self, call: InlineCall, mode: str):
        state = self.state_get()
        state[self.strings["state_slots_from_menu"]] = state.get("mode") == self.strings["mode_menu"]
        state["mode"] = self.strings["mode_slots"]
        self.state_set(state)
        title_text = self.strings["save_header"] if mode == self.strings["save_action"] else self.strings["load_header"]
        await self.ui(call, title_text, self.save_kb(mode), self.save_image)

    async def back_from_saves(self, call: InlineCall):
        state = self.state_get()
        if state.get(self.strings["state_slots_from_menu"]):
            state[self.strings["state_slots_from_menu"]] = False
            state["mode"] = self.strings["mode_menu"]
            state["pending"] = None
            self.state_set(state)
            await self.menu(call)
            return
        if state.get("chapter") and state.get("mode") != self.strings["mode_menu"]:
            state["mode"] = self.strings["mode_play"]
            self.state_set(state)
            pending_node = state.get("pending")
            if pending_node and pending_node.get("type") == self.strings["type_route"]:
                route_id = pending_node.get("id")
                question_text = self.routes_data.get(route_id, {}).get("question") or self.strings["default_route_question"]
                await self.ui(call, question_text, self.choice_kb(route_id), self.scene_photo(state))
                return
            await self.ui(call, self.render_dialogs(state) or self.strings["or_game"], self.start_kb(), self.scene_photo(state))
            return
        await self.menu(call)

    async def save_action(self, call: InlineCall, mode: str, n: int):
        slots = self.slots_get()
        state = self.state_get()
        slot_key = str(n)
        if mode == self.strings["save_action"]:
            if slot_key in slots:
                state["mode"] = self.strings["mode_ask_rewrite"]
                self.state_set(state)
                kb = [
                    [
                        {"text": "Да", "callback": self.rewrite_true, "args": (n,)},
                        {"text": "Нет", "callback": self.save_menu, "args": (self.strings["save_action"],)},
                    ],
                    [{"text": "Назад", "callback": self.back_from_saves}],
                ]
                await self.ui(call, self.strings["rewrite"].format(n), kb, self.save_image)
                return
            slots[slot_key] = self.state_preservation(state)
            self.slots_set(slots)
            await call.answer(self.strings["saved"].format(n), show_alert=True)
            await self.save_menu(call, self.strings["save_action"])
            return
        if slot_key not in slots:
            await call.answer(self.strings["empty"].format(n), show_alert=True)
            return
        loaded_state = copy.deepcopy(slots[slot_key])
        self.state_set(loaded_state)
        await call.answer(self.strings["loaded"].format(n), show_alert=True)
        await self.go(call, loaded_state)

    async def rewrite_true(self, call: InlineCall, n: int):
        slots = self.slots_get()
        state = self.state_get()
        slots[str(n)] = self.state_preservation(state)
        self.slots_set(slots)
        await call.answer(self.strings["saved"].format(n), show_alert=True)
        await self.save_menu(call, self.strings["save_action"])

    @loader.command()
    async def bl(self, message: Message):
        """Запустить ваше бесконечное лето,нууу точнее пока что его пролог."""
        ok = await self.load_data()
        if not ok:
            await utils.answer(message, self.strings["bad"])
            return
        await self.ui(message, self.strings["menu"], self.menu_kb(), self.menu_image)

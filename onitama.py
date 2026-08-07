# requires: pillow requests
# meta developer: @H_SunMods
# meta banner: https://r2.fakecrime.bio/uploads/00b416c7-4987-4eed-a314-497c159b5403.jpg
# meta pic: https://r2.fakecrime.bio/uploads/00b416c7-4987-4eed-a314-497c159b5403.jpg
# meta fhsdesc: mini-game, game, onitama, strategy, sunnex
# meta tags: mini-game, game, onitama, strategy, sunnex
#current version

__version__ = (1, 0, 0)

from herokutl.types import Message
from .. import loader, utils
from ..types import InlineCall
from PIL import Image, ImageDraw
from io import BytesIO
from typing import TypedDict, Optional
import random
import requests


class Player(TypedDict):
    id: int
    name: str
    color: Optional[bool]

tiger = [
    [0, 0, 2, 0, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 2, 0, 0],
    [0, 0, 0, 0, 0]
]

crab = [
    [0, 0, 0, 0, 0],
    [0, 0, 2, 0, 0],
    [2, 0, 1, 0, 2],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
]

monkey = [
    [0, 0, 0, 0, 0],
    [0, 2, 0, 2, 0],
    [0, 0, 1, 0, 0],
    [0, 2, 0, 2, 0],
    [0, 0, 0, 0, 0]
]

crane = [
    [0, 0, 0, 0, 0],
    [0, 0, 2, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 2, 0, 2, 0],
    [0, 0, 0, 0, 0]
]

dragon = [
    [0, 0, 0, 0, 0],
    [2, 0, 0, 0, 2],
    [0, 0, 1, 0, 0],
    [0, 2, 0, 2, 0],
    [0, 0, 0, 0, 0]
]

elephant = [
    [0, 0, 0, 0, 0],
    [0, 2, 0, 2, 0],
    [0, 2, 1, 2, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
]

mantis = [
    [0, 0, 0, 0, 0],
    [0, 2, 0, 2, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 2, 0, 0],
    [0, 0, 0, 0, 0]
]

boar = [
    [0, 0, 0, 0, 0],
    [0, 0, 2, 0, 0],
    [0, 2, 1, 2, 0],
    [0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0]
]

frog = [
    [0, 0, 0, 0, 0],
    [0, 2, 0, 0, 0],
    [2, 0, 1, 0, 0],
    [0, 0, 0, 2, 0],
    [0, 0, 0, 0, 0]
]

goose = [
    [0, 0, 0, 0, 0],
    [0, 2, 0, 0, 0],
    [0, 2, 1, 2, 0],
    [0, 0, 0, 2, 0],
    [0, 0, 0, 0, 0]
]

horse = [
    [0, 0, 0, 0, 0],
    [0, 0, 2, 0, 0],
    [0, 2, 1, 0, 0],
    [0, 0, 2, 0, 0],
    [0, 0, 0, 0, 0]
]

eel = [
    [0, 0, 0, 0, 0],
    [0, 2, 0, 0, 0],
    [0, 0, 1, 2, 0],
    [0, 2, 0, 0, 0],
    [0, 0, 0, 0, 0]
]

rabbit = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 2, 0],
    [0, 0, 1, 0, 2],
    [0, 2, 0, 0, 0],
    [0, 0, 0, 0, 0]
]

rooster = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 2, 0],
    [0, 2, 1, 2, 0],
    [0, 2, 0, 0, 0],
    [0, 0, 0, 0, 0]
]

ox = [
    [0, 0, 0, 0, 0],
    [0, 0, 2, 0, 0],
    [0, 0, 1, 2, 0],
    [0, 0, 2, 0, 0],
    [0, 0, 0, 0, 0]
]

cobra = [
    [0, 0, 0, 0, 0],
    [0, 0, 0, 2, 0],
    [0, 2, 1, 0, 0],
    [0, 0, 0, 2, 0],
    [0, 0, 0, 0, 0]
]

cards = {
    "tiger": tiger,
    "crab": crab,
    "monkey": monkey,
    "crane": crane,
    "dragon": dragon,
    "elephant": elephant,
    "mantis": mantis,
    "boar": boar,
    "frog": frog,
    "goose": goose,
    "horse": horse,
    "eel": eel,
    "rabbit": rabbit,
    "rooster": rooster,
    "ox": ox,
    "cobra": cobra,
}
card_names = list(cards.keys())

# чтобы не потеряться просто подпишу что тут настройка баннера,с моего макета из фигмы.
maket_size = (1746, 1203)
bg_color = (112, 150, 37, 255)
card_bg_color = (178, 239, 58, 255)
blocks_colors = {
    0: (43, 183, 90, 255),
    1: (255, 170, 146, 255),
    2: (255, 107, 64, 255),
}
card_border = (146, 255, 105, 255)
card_margin = 18
card_grid_block_size = 50
player_one_card_boxes = [(383, 257, 668, 542), (724, 257, 1009, 542)]
player_two_card_boxes = [(383, 661, 668, 946), (724, 661, 1009, 946)]
spare_card_box = (1205, 459, 1490, 744)
human_pos = (632, 50)
nig_pos = (632, 1026) # без рассизма,прост весело.
emj_size = (127, 127)

image_cache = {}
try:
    i_lanczos = Image.Resampling.LANCZOS
except AttributeError:
    i_lanczos = Image.LANCZOS


def dl_img(url):
    if not url:
        return None
    if url not in image_cache:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            image_cache[url] = response.content
        except Exception:
            image_cache[url] = None
    return image_cache[url]


def init_board():
    board = [[None for _ in range(5)] for _ in range(5)]
    for column in range(5):
        if column == 2:
            piece_type = "king"
        else:
            piece_type = "pawn"
        board[0][column] = {"color": True, "type": piece_type}
        board[4][column] = {"color": False, "type": piece_type}
    return board


def init_game_skins(cell):
    if cell is None:
        return "⠀"
    if cell["color"] is True:
        if cell["type"] == "king":
            return "🤴🏻"
        else:
            return "👶🏻"
    else:
        if cell["type"] == "king":
            return "🤴🏿"
        else:
            return "👶🏿"


def create_movment_card(image, box, card_name, rotated):
    draw = ImageDraw.Draw(image)
    draw.rectangle(box, fill=card_bg_color)
    matrix = cards[card_name]
    if rotated:
        rows = matrix[::-1]
    else:
        rows = matrix
    scale = 4
    grid_size = card_grid_block_size * 5
    layer = Image.new("RGBA", (grid_size * scale, grid_size * scale), (0, 0, 0, 0))
    layer_draw = ImageDraw.Draw(layer)
    for row_index, row in enumerate(rows):
        if rotated:
            cells = row[::-1]
        else:
            cells = row
        for column_index, value in enumerate(cells):
            left = column_index * card_grid_block_size * scale
            top = row_index * card_grid_block_size * scale
            right = left + card_grid_block_size * scale
            bottom = top + card_grid_block_size * scale
            layer_draw.rounded_rectangle(
                (left, top, right, bottom),
                radius=6 * scale,
                fill=blocks_colors.get(value, blocks_colors[0]),
                outline=card_border,
                width=2 * scale,
            )
    re_s_layer = layer.resize((grid_size, grid_size), i_lanczos)
    anchor_x = box[0] + card_margin
    anchor_y = box[1] + card_margin
    image.paste(re_s_layer, (anchor_x, anchor_y), re_s_layer)

class Game:
    def __init__(self, white_player: Player, black_player: Player):
        self.players = {True: white_player, False: black_player}
        self.board = init_board()
        r_cards_sample = random.sample(card_names, 5)
        self.hands = {
            True: [r_cards_sample[0], r_cards_sample[1]],
            False: [r_cards_sample[2], r_cards_sample[3]],
        }
        self.spare_card = r_cards_sample[4]
        self.turn = random.choice((True, False))
        self.selected_card = None
        self.selected_piece = None
        self.finished = False
        self.winner = None

    def switch_turn(self):
        self.turn = not self.turn

    def move_offsets(self, card_name, color):
        matrix = cards[card_name]
        offsets = []
        for row_index in range(5):
            for column_index in range(5):
                if matrix[row_index][column_index] == 2:
                    d_row = row_index - 2
                    d_column = column_index - 2
                    if color is True:
                        d_row = -d_row
                        d_column = -d_column
                    offsets.append((d_row, d_column))
        return offsets

    def approved_moves(self, row, column, card_name, color):
        blcok_moves = []
        for d_row, d_column in self.move_offsets(card_name, color):
            move_poin_row = row + d_row
            move_poin_column = column + d_column
            if move_poin_row < 0 or move_poin_row > 4 or move_poin_column < 0 or move_poin_column > 4:
                continue
            move_poin_cell = self.board[move_poin_row][move_poin_column]
            if move_poin_cell is None or move_poin_cell["color"] != color:
                blcok_moves.append((move_poin_row, move_poin_column))
        return blcok_moves

    def done_move(self, from_row, from_column, to_row, to_column):
        piece = self.board[from_row][from_column]
        self.board[from_row][from_column] = None
        self.board[to_row][to_column] = piece
        hand = self.hands[self.turn]
        played_card = self.selected_card
        card_index = hand.index(played_card)
        hand[card_index] = self.spare_card
        self.spare_card = played_card

    def check_winner(self):
        for color in (True, False):
            opponent_king_alive = False
            for row in self.board:
                for cell in row:
                    if cell and cell["color"] != color and cell["type"] == "king":
                        opponent_king_alive = True
            if not opponent_king_alive:
                return color

        white_spawn = self.board[4][2]
        if white_spawn and white_spawn["color"] is True and white_spawn["type"] == "king":
            return True

        black_spawn = self.board[0][2]
        if black_spawn and black_spawn["color"] is False and black_spawn["type"] == "king":
            return False
        return None


@loader.tds
class onitama(loader.Module):
    """Onitama - это мини игра для двоих с полем 5 на 5."""

    strings = {
        "name": "Onitama",
        "invite_msg": "<b>{owner_name}</b> приглашает тебя сыграть в Онитаму!\nПринять вызов?",
        "accept_button": "Принять",
        "decline_button": "Отклонить",
        "othelp_btn": "Перейти",
        "cant_accept_own": "Сам с собой что ли играть собрался? Давай уж в другой раз",
        "not_for_u": "Это приглашение не для тебя",
        "invite_cancelled": "Приглашение отменено",
        "invite_declined": "Приглашение отклонено",
        "invalid_user": "Не удалось найти этого пользователя",
        "move_msg": "<b>{human} VS {nigga}\n{w_arrow}🤴🏻 {human}\n{b_arrow}🤴🏿 {nigga}</b>",
        # "move_msg": "<b>{human} VS {nigga}</b>\n<b>{w_arrow}🤴🏻 {human}</b>\n<b>{b_arrow}🤴🏿 {nigga}</b>",
        "win_msg": "<b>{win_name} победил(а)!</b>",
        "game_not_found": "Эта игра уже мертва",
        "not_ur_turn": "Сейчас не твой ход",
        "not_u_card": "Это не твоя карта, дурак!",
        "first_selectt": "Сначала выбери карту",
        "select_own_piece": "Выбери одну из своих фигур",
        "illegal_move": "Ты не можешь сделать ход на эту клетку.",
        "oth_msg": "Подробный гайд можно посмотреть у меня в канале,так как мне было лень писать целуюю полноценную команду."
    }

    def __init__(self):
        self.games = {}
        self.king_white_img = "https://github.com/SunnexGB/Heroku-Modules/blob/main/Assets/onitama/white.png?raw=true"
        self.king_nig_img = "https://github.com/SunnexGB/Heroku-Modules/blob/main/Assets/onitama/black.png?raw=true"
        self.win_img = "https://github.com/SunnexGB/Heroku-Modules/blob/main/Assets/onitama/win_img.png?raw=true"
        self.urlhelp = "https://t.me/H_SunMods/86"

    @loader.command()
    async def othelp(self, message: Message):
        """- Показать правила игры"""
        await self.inline.form(
            self.strings["oth_msg"],
            message=message,
            reply_markup=[
                [
                    {"text": self.strings["othelp_btn"], "url": self.urlhelp}
                ],
            ],
        )
    @loader.command()
    async def ot(self, message: Message):
        """- Ответом / @username / id. начать игру"""
        guest_id = None
        if message.is_reply:
            reply_message = await message.get_reply_message()
            guest_id = reply_message.sender_id
        else:
            args = utils.get_args_raw(message)
            if args:
                try:
                    target_entity = await self.client.get_entity(args)
                    guest_id = target_entity.id
                except Exception:
                    await utils.answer(message, self.strings["invalid_user"])
                    return

        owner = await message.get_sender()
        owner_name = utils.escape_html(owner.first_name or "Player")
        await self.inline.form(
            text=self.strings["invite_msg"].format(owner_name=owner_name),
            message=message,
            reply_markup=[
                [
                    {
                        "text": self.strings["accept_button"],
                        "callback": self.if_invite_accept,
                        "args": (owner.id, owner_name, guest_id),
                        "disable_security": True,
                    },
                    {
                        "text": self.strings["decline_button"],
                        "callback": self.if_invite_decline,
                        "args": (owner.id, guest_id),
                        "disable_security": True,
                    },
                ]
            ],
            disable_security=True,
        )

    async def if_invite_accept(self, call: InlineCall, owner_id: int, owner_name: str, guest_id: int):
        if call.from_user.id == owner_id:
            await call.answer(self.strings["cant_accept_own"], show_alert=True)
            return
        if guest_id and call.from_user.id != guest_id:
            await call.answer(self.strings["not_for_u"], show_alert=True)
            return

        opponent_entity = await self.client.get_entity(call.from_user.id)
        opponent_name = utils.escape_html(opponent_entity.first_name or "Player")
        owner_player: Player = {"id": owner_id, "name": owner_name, "color": None}
        opponent_player: Player = {"id": call.from_user.id, "name": opponent_name, "color": None}
        if random.choice((True, False)): # норм да?
            white_player, black_player = owner_player, opponent_player
        else:
            white_player, black_player = opponent_player, owner_player
        white_player["color"] = True
        black_player["color"] = False
        game = Game(white_player, black_player)
        self.games[call.message.chat.id] = game
        await self.kb_upd(call, game)

    async def if_invite_decline(self, call: InlineCall, owner_id: int, guest_id: int):
        if call.from_user.id == owner_id:
            await call.edit(
                text=self.strings["invite_cancelled"],
                disable_security=True,
            )
            return
        if guest_id and call.from_user.id != guest_id:
            await call.answer(self.strings["not_for_u"], show_alert=True)
            return
        await call.edit(
            text=self.strings["invite_declined"],
            disable_security=True,
        )

    async def card_sw(self, call: InlineCall, card_name: str):
        game = self.games.get(call.message.chat.id)
        if not game or game.finished:
            await call.answer(self.strings["game_not_found"], show_alert=True)
            return

        color = game.turn
        if call.from_user.id != game.players[color]["id"]:
            await call.answer(self.strings["not_ur_turn"], show_alert=True)
            return
        if card_name not in game.hands[color]:
            await call.answer(self.strings["not_u_card"], show_alert=True)
            return

        if game.selected_card == card_name:
            game.selected_card = None
        else:
            game.selected_card = card_name
        game.selected_piece = None
        await self.r_kb(call, game)

    async def moves_cells_logic(self, call: InlineCall, row: int, column: int): #idk
        game = self.games.get(call.message.chat.id)
        if not game or game.finished:
            await call.answer(self.strings["game_not_found"], show_alert=True)
            return

        color = game.turn
        if call.from_user.id != game.players[color]["id"]:
            await call.answer(self.strings["not_ur_turn"], show_alert=True)
            return
        if game.selected_card is None:
            await call.answer(self.strings["first_selectt"], show_alert=True)
            return

        clicked_cell = game.board[row][column]
        if game.selected_piece is None:
            if clicked_cell is None or clicked_cell["color"] != color:
                await call.answer(self.strings["select_own_piece"], show_alert=True)
                return
            game.selected_piece = (row, column)
            await self.r_kb(call, game)
            return
        piece_row, piece_column = game.selected_piece

        if row == piece_row and column == piece_column:
            game.selected_piece = None
            await self.r_kb(call, game)
            return

        if clicked_cell is not None and clicked_cell["color"] == color:
            game.selected_piece = (row, column)
            await self.r_kb(call, game)
            return

        approved_moves = game.approved_moves(piece_row, piece_column, game.selected_card, color)
        if (row, column) not in approved_moves:
            await call.answer(self.strings["illegal_move"], show_alert=True)
            return

        game.done_move(piece_row, piece_column, row, column)
        winner_color = game.check_winner()
        game.selected_card = None
        game.selected_piece = None
        if winner_color is not None:
            game.finished = True
            game.winner = winner_color
            await self.kb_upd(call, game)
            del self.games[call.message.chat.id]
            return
        game.switch_turn()
        await self.kb_upd(call, game)

    def select_player_move(self, game):
        white = game.players[True]
        black = game.players[False]

        if game.finished:
            win_name = game.players[game.winner]["name"]
            return self.strings["win_msg"].format(win_name=win_name)

        if game.turn is True:
            white_arrow = " >"
            black_arrow = ""
        else:
            white_arrow = ""
            black_arrow = " >"

        return self.strings["move_msg"].format(
            human=white["name"], 
            nigga=black["name"], 
            w_arrow=white_arrow, 
            b_arrow=black_arrow, 
        )

    def hands_btns(self, game, color):
        hand = game.hands[color]
        row = []
        for card_name in hand:
            hands_card_name = card_name.capitalize()
            is_selected = game.turn == color and game.selected_card == card_name
            button = {
                "text": hands_card_name,
                "callback": self.card_sw,
                "args": (card_name,),
                "disable_security": True,
            }
            if is_selected:
                button["style"] = "primary"
            row.append(button)
        return row

    def create_boardr(self, game):
        color = game.turn
        approved_moves = []
        if game.selected_card and game.selected_piece:
            piece_row, piece_column = game.selected_piece
            approved_moves = game.approved_moves(piece_row, piece_column, game.selected_card, color)
        rows = []
        for row_index in range(5):
            board_row = []
            for column_index in range(5):
                cell = game.board[row_index][column_index]
                skin = init_game_skins(cell)
                is_legal_move = (row_index, column_index) in approved_moves
                button = {
                    "text": skin,
                    "callback": self.moves_cells_logic,
                    "args": (row_index, column_index),
                    "disable_security": True,
                }
                if is_legal_move:
                    button["style"] = "success"
                board_row.append(button)
            rows.append(board_row)
        return rows

    def full_board(self, game):
        kb = [self.hands_btns(game, True)]
        kb.extend(self.create_boardr(game))
        kb.append(self.hands_btns(game, False))
        return kb

    def render_msg_img(self, game):
        image = Image.new("RGBA", maket_size, bg_color)
        white_king_bytes = dl_img(self.king_white_img)
        if white_king_bytes:
            king_white_image = Image.open(BytesIO(white_king_bytes)).convert("RGBA").resize(emj_size)
            image.paste(king_white_image, human_pos, king_white_image)

        black_king_bytes = dl_img(self.king_nig_img)
        if black_king_bytes:
            king_black_image = Image.open(BytesIO(black_king_bytes)).convert("RGBA").resize(emj_size)
            image.paste(king_black_image, nig_pos, king_black_image)

        for box, card_name in zip(player_one_card_boxes, game.hands[True]):
            create_movment_card(image, box, card_name, True)

        for box, card_name in zip(player_two_card_boxes, game.hands[False]):
            create_movment_card(image, box, card_name, False)

        create_movment_card(image, spare_card_box, game.spare_card, False)

        output = BytesIO()
        image.convert("RGB").save(output, format="PNG")
        output.seek(0)
        output.name = "onitama.png"
        return output

    async def r_kb(self, call, game):
        await call.edit(
            text=self.select_player_move(game),
            reply_markup=self.full_board(game), 
            disable_security=True
        )

    async def kb_upd(self, call, game):
        if game.finished:
            await call.edit(
                text=self.select_player_move(game),
                photo=self.win_img,
                disable_security=True,
            )
        else:
            await call.edit(
                text=self.select_player_move(game),
                reply_markup=self.full_board(game),
                photo=self.render_msg_img(game),
                disable_security=True,
            )
# requires: aiohttp
# meta developer: @H_SunMods
# meta banner: https://r2.fakecrime.bio/uploads/965a3206-4609-4dff-beb0-6831f8b90e12.jpg
# current ver
__version__ = (0, 1, 1)

import json
import socket
import asyncio
import secrets
import logging
import re
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from aiohttp import ClientSession, ClientTimeout, web
from herokutl.types import Message
from .. import loader, utils
from ..inline.types import InlineCall

html_raw = "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/refs/heads/main/Assets/NoChess/raw_assets/index.html"
css_raw = "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/refs/heads/main/Assets/NoChess/raw_assets/style.css"
js_raw = "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/refs/heads/main/Assets/NoChess/raw_assets/javascript.js"
asset_root_raw = "https://raw.githubusercontent.com/SunnexGB/Heroku-Modules/main/Assets/NoChess"
botfather_photo_url = "https://r2.fakecrime.bio/uploads/d3e16245-15a2-43f1-b176-493b4d9f1f21.jpg"

@loader.tds
class NoChess(loader.Module):
    """NoChess - web module that allows u to launch a web page either as a functional HTML page or as a Telegram Mini-App. This is an add-on for Chess module by @nullmod"""

    strings = {
        "name": "NoChess",
        "starting": "( ﾉ･ｪ･ )ﾉ <b>Starting NoChess...</b>",
        "online": "(*˘︶˘*) <b>NoChess is running</b>",
        "already_running": "ʕᵕᴥᵕʔ <b>NoChess is already running</b>",
        "stopped": "･ﾟ･(｡>д<｡)･ﾟ･ NoChess stopped",
        "not_running": "(✿╹◡╹) NoChess is not running",
        "tunnel_error": "Serveo tunnel error: <code>{}</code>",
        "asset_read_error": "Failed to load web assets: <code>{}</code>",
        "open_button": "Open mini-app",
        "stop_button": "Stop",
        "about_text": "<b>Important read:</b>\nSometimes the server won't lift cause there's enough processes running, for example on HikkaHost, for this I just rebooted the server\nNext is that <code>cma</code> setups the app by a template and it's rly crooked, so you'll have to set some web app config settings yourself\nAnd also:\n    1. First launch will start straight with a site link, not as a web app\n    2. Use <code>nochess</code>, and then <code>cma</code> to setup the web app\n    3. After that restart the process by typing <code>nochess -kill</code> and <code>nochess</code> again\nYeah it's hacky as hell, but I was so over doing stuff that I started dumping some routine like working with files on ai, which I didn't like so I decided to quick-release the module before it's too late\nWell and maybe soon I'll make an update, right now it's some pre-alpha version, that's why the version name is like this, later I'll change it to 1.0.0, if people actually dig the module as an idea",
        "cma_start": "( ﾉ･ｪ･ )ﾉ <b>Creating mini app in BotFather...</b>",
        "cma_need_url": "Set mini app web URL first or run <code>.nochess</code> to get it.",
        "cma_done": "(*˘︶˘*) <b>Done.</b>",
        "cma_error": "Error: <code>{}</code>",
        "RuntimeError": "inline bot username not found",
        "not_supported_platform": "(┬┬＿┬┬) Unfortunately, it is impossible to install this module on this platform.\n\n(〜^∇^)〜 This is not an error, please do not contact support."
    }

    strings_ru = {
        "_cls_doc": "NoChess - Веб модуль который позволяет запускать веб-пейдж,как HTML страницу с функционалом,так же в виде Telegram Mini-App. Является дополнением к модулю Chess от @nullmod",
        "starting": "( ﾉ･ｪ･ )ﾉ <b>Запуск NoChess...</b>",
        "online": "(*˘︶˘*) <b>NoChess запущен</b>",
        "already_running": "ʕᵕᴥᵕʔ <b>NoChess уже запущен</b>",
        "stopped": "･ﾟ･(｡>д<｡)･ﾟ･ NoChess остановлен",
        "not_running": "(✿╹◡╹) NoChess не запущен",
        "tunnel_error": "Ошибка туннеля Serveo: <code>{}</code>",
        "asset_read_error": "Не удалось загрузить веб-ассеты: <code>{}</code>",
        "open_button": "Открыть мини-приложение",
        "stop_button": "Остановить",
        "about_text": "<b>Важно к прочтению:</b>\nИногда сервер не может подниматься из за того что запущено достаточно процессов, например на HikkaHost,для этого я просто перезагружал сервер.\nДалее это то что <code>cma</code> сетапает приложение по шаблону и оч криво, поэтому вам придется выставлять некоторые настройки конфигурации веб приложения самим.\nА еще:\n    1. Первый запуск будет запускаться сразу ссылкой на сайт, а не как веб приложение.\n    2. Используйте <code>nochess</code>, а потом <code>cma</code> чтобы настроить веб приложение.\n    3. После чего перезапустите процесс написав <code>nochess -kill</code> и повторно <code>nochess</code>.\nДа это костыли, но мне уже настолько было в падлу что то делать что я уже стал спихивать рутину по типу работы с файлами на ии, что мне не понравилось и я решил быстро релизать модуль пока не стало поздно.\nНу и может быть в скором времени я уже сделаю апдейт, на данный момент это какая то пре-альфа версия, поэтому и название версии такое, в дальнейшем изменю на 1.0.0, если модуль вообще понравиться людям как идея.",
        "cma_start": "( ﾉ･ｪ･ )ﾉ <b>Создаю эпку через BotFather...</b>",
        "cma_need_url": "Сначала укажи URL мини-эпки или запусти <code>.nochess</code>, чтобы получить его",
        "cma_done": "(*˘︶˘*) <b>Готово</b>",
        "cma_error": "Ошибка: <code>{}</code>",
        "RuntimeError": "юз инлайн бота не найден",
        "not_supported_platform": "(┬┬＿┬┬) К сожалению, на эту платформу невозможно установить этот модуль.\n\n(〜^∇^)〜 Это не ошибка, пожалуйста, не обращайтесь в поддержку."
    }

    strings_de = {
        "_cls_doc": "NoChess - Webmodul zum Starten einer Webseite als HTML oder Telegram Mini-App. Erweiterung für Chess von @nullmod",
        "starting": "( ﾉ･ｪ･ )ﾉ <b>Starte NoChess...</b>",
        "online": "(*˘︶˘*) <b>NoChess läuft</b>",
        "already_running": "ʕᵕᴥᵕʔ <b>NoChess läuft bereits</b>",
        "stopped": "･ﾟ･(｡>д<｡)･ﾟ･ NoChess gestoppt",
        "not_running": "(✿╹◡╹) NoChess läuft nicht",
        "tunnel_error": "Serveo-Tunnel-Fehler: <code>{}</code>",
        "asset_read_error": "Fehler beim Laden der Web-Assets: <code>{}</code>",
        "open_button": "Mini-App öffnen",
        "stop_button": "Stopp",
        "about_text": "<b>Wichtig zu lesen:</b>\nManchmal startet der Server nicht, weil zu viele Prozesse laufen. <code>cma</code> richtet die App über eine Vorlage ein, musst einige Web-App-Einstellungen selbst setzen.\nUnd außerdem:\n    1. Erster Start beginnt direkt mit einem Seitenlink, nicht als Web-App\n    2. Verwende <code>nochess</code> und dann <code>cma</code> zum Einrichten\n    3. Danach Prozess neustarten mit <code>nochess -kill</code> und nochmal <code>nochess</code>\nPre-Alpha, später 1.0.0 falls die Leute die Idee mögen.",
        "cma_start": "( ﾉ･ｪ･ )ﾉ <b>Erstelle Mini-App im BotFather...</b>",
        "cma_need_url": "Setze zuerst die Mini-App-Web-URL oder führe <code>.nochess</code> aus.",
        "cma_done": "(*˘︶˘*) <b>Fertig.</b>",
        "cma_error": "Fehler: <code>{}</code>",
        "RuntimeError": "Inline-Bot-Benutzername nicht gefunden",
        "not_supported_platform": "(┬┬＿┬┬) Leider unmöglich, dieses Modul auf dieser Plattform zu installieren.\n\n(〜^∇^)〜 Kein Fehler, Support nicht kontaktieren."
    }

    strings_ua = {
        "_cls_doc": "NoChess - Веб модуль для запуску веб-сторінки як HTML або Telegram Mini-App. Доповнення до Chess від @nullmod",
        "starting": "( ﾉ･ｪ･ )ﾉ <b>Запуск NoChess...</b>",
        "online": "(*˘︶˘*) <b>NoChess запущено</b>",
        "already_running": "ʕᵕᴥᵕʔ <b>NoChess вже запущено</b>",
        "stopped": "･ﾟ･(｡>д<｡)･ﾟ･ NoChess зупинено",
        "not_running": "(✿╹◡╹) NoChess не запущено",
        "tunnel_error": "Помилка тунелю Serveo: <code>{}</code>",
        "asset_read_error": "Не вдалося завантажити веб-ассети: <code>{}</code>",
        "open_button": "Відкрити міні-застосунок",
        "stop_button": "Зупинити",
        "about_text": "<b>Важливо прочитати:</b>\nІноді сервер не запускається через забагато процесів. <code>cma</code> налаштовує за шаблоном — налаштуйте веб-застосунок самостійно.\nА ще:\n    1. Перший запуск — одразу посилання на сайт, не веб-застосунок\n    2. Використовуйте <code>nochess</code>, потім <code>cma</code> для налаштування\n    3. Перезапустіть процес: <code>nochess -kill</code>, потім <code>nochess</code>\nПре-альфа, пізніше 1.0.0 якщо ідея сподобається.",
        "cma_start": "( ﾉ･ｪ･ )ﾉ <b>Створюю міні-застосунок через BotFather...</b>",
        "cma_need_url": "Спочатку вкажи URL або запусти <code>.nochess</code>",
        "cma_done": "(*˘︶˘*) <b>Готово.</b>",
        "cma_error": "Помилка: <code>{}</code>",
        "RuntimeError": "юзернейм інлайн-бота не знайдено",
        "not_supported_platform": "(┬┬＿┬┬) На жаль, неможливо встановити цей модуль на цю платформу.\n\n(〜^∇^)〜 Це не помилка, не звертайтесь у підтримку."
    }

    strings_jp = {
        "_cls_doc": "NoChess - HTMLまたはTelegram Mini-Appとしてページを起動するモジュール。Chess（@nullmod）のアドオン",
        "starting": "( ﾉ･ｪ･ )ﾉ <b>NoChessを起動中...</b>",
        "online": "(*˘︶˘*) <b>NoChessは実行中です</b>",
        "already_running": "ʕᵕᴥᵕʔ <b>NoChessはすでに実行中です</b>",
        "stopped": "･ﾟ･(｡>д<｡)･ﾟ･ NoChessを停止しました",
        "not_running": "(✿╹◡╹) NoChessは実行されていません",
        "tunnel_error": "Serveoトンネルエラー: <code>{}</code>",
        "asset_read_error": "Webアセットの読み込みに失敗: <code>{}</code>",
        "open_button": "ミニアプリを開く",
        "stop_button": "停止",
        "about_text": "<b>重要なお知らせ:</b>\nプロセスが多すぎてサーバーが起動しないことがあります。<code>cma</code>はテンプレートでアプリをセットアップしますが歪なので自分で設定してください。\nさらに:\n    1. 最初の起動はWebアプリではなくサイトリンクで開始\n    2. <code>nochess</code>を使い、<code>cma</code>で設定\n    3. <code>nochess -kill</code>してから再度<code>nochess</code>\nプレアルファ版、後で1.0.0に変更予定。",
        "cma_start": "( ﾉ･ｪ･ )ﾉ <b>BotFatherでミニアプリを作成中...</b>",
        "cma_need_url": "最初にミニアプリのURLを設定するか、<code>.nochess</code>を実行してください",
        "cma_done": "(*˘︶˘*) <b>完了。</b>",
        "cma_error": "エラー: <code>{}</code>",
        "RuntimeError": "インラインボットのユーザー名が見つかりません",
        "not_supported_platform": "(┬┬＿┬┬) このプラットフォームにはインストールできません。\n\n(〜^∇^)〜 エラーではありません。サポートに連絡しないでください。"
    }

    strings_neofit = {
        "_cls_doc": "NoChess — web module fer launchin' a page as HTML or Telegram Mini-App. Add-on fer Chess by @nullmod",
        "starting": "( ﾉ･ｪ･ )ﾉ <b>Spinnin' up NoChess...</b>",
        "online": "(*˘︶˘*) <b>NoChess is live, fam</b>",
        "already_running": "ʕᵕᴥᵕʔ <b>NoChess already cookin'</b>",
        "stopped": "･ﾟ･(｡>д<｡)･ﾟ･ NoChess iced",
        "not_running": "(✿╹◡╹) NoChess ain't up",
        "tunnel_error": "Serveo tunnel bricked: <code>{}</code>",
        "asset_read_error": "Couldn't snag web assets: <code>{}</code>",
        "open_button": "Pop the mini-app",
        "stop_button": "Cut it",
        "about_text": "<b>RTFM:</b>\nBox won't lift sometimes 'cause too many procs — just reboot. <code>cma</code> uses a jank template so tweak config yerself.\nAlso:\n    1. First run = site link, not web app\n    2. Hit <code>nochess</code> then <code>cma</code> to rig it\n    3. Bounce the proc with <code>nochess -kill</code> + <code>nochess</code>\nPre-alpha slop, gonna bump to 1.0.0 if peeps vibe.",
        "cma_start": "( ﾉ･ｪ･ )ﾉ <b>Forgin' mini app via BotFather...</b>",
        "cma_need_url": "Drop a mini-app URL first or run <code>.nochess</code>",
        "cma_done": "(*˘︶˘*) <b>Ship it.</b>",
        "cma_error": "L + ratio: <code>{}</code>",
        "RuntimeError": "inline bot handle MIA",
        "not_supported_platform": "(┬┬＿┬┬) No shot installin' here.\n\n(〜^∇^)〜 Not a bug, don't ping support."
    }

    strings_tiktok = {
        "_cls_doc": "NoChess — веб-модуль запускает страничку как HTML или мини-апп в телеге. Аддон к Chess от @nullmod",
        "starting": "( ﾉ･ｪ･ )ﾉ <b>Газуем NoChess...</b>",
        "online": "(*˘︶˘*) <b>NoChess на стиле</b>",
        "already_running": "ʕᵕᴥᵕʔ <b>NoChess уже тащит</b>",
        "stopped": "･ﾟ･(｡>д<｡)･ﾟ･ NoChess слился",
        "not_running": "(✿╹◡╹) NoChess не в теме",
        "tunnel_error": "Serveo тунель крашнулся: <code>{}</code>",
        "asset_read_error": "Не смог забрать ассеты: <code>{}</code>",
        "open_button": "Открыть мини-апп",
        "stop_button": "Стопэ",
        "about_text": "<b>Читни сюда:</b>\nБывает серв не поднимается — процов дофига, ребутаю. <code>cma</code> сетапит криво, конфиг руками.\nИ ещё:\n    1. Первый запуск — сразу ссылка на сайт, не апп\n    2. Юзай <code>nochess</code>, потом <code>cma</code>\n    3. Дропни через <code>nochess -kill</code> и снова <code>nochess</code>\nПре-альфа дичь, потом 1.0.0 если залетит.",
        "cma_start": "( ﾉ･ｪ･ )ﾉ <b>Делаю мини-апп через BotFather...</b>",
        "cma_need_url": "Сначала кинь URL или жмякни <code>.nochess</code>",
        "cma_done": "(*˘︶˘*) <b>Запилил.</b>",
        "cma_error": "Ой фейл: <code>{}</code>",
        "RuntimeError": "юз бота не нашли",
        "not_supported_platform": "(┬┬＿┬┬) Сорян, на эту платформу модуль не встанет.\n\n(〜^∇^)〜 Не ошибка, в саппорт не пиши."
    }

    strings_leet = {
        "_cls_doc": "NoChess — w3b m0dul3 t0 l4unch p4g3 4s HTML 0r T3l3gr4m M1n1-4pp. 4dd-0n f0r Ch355 by @nullm0d",
        "starting": "( ﾉ･ｪ･ )ﾉ <b>B00t1ng N0Ch355...</b>",
        "online": "(*˘︶˘*) <b>N0Ch355 15 1n th3 m4tr1x</b>",
        "already_running": "ʕᵕᴥᵕʔ <b>N0Ch355 4lr34dy 0n</b>",
        "stopped": "･ﾟ･(｡>д<｡)･ﾟ･ N0Ch355 t3rm1n4t3d",
        "not_running": "(✿╹◡╹) N0Ch355 0ffl1n3",
        "tunnel_error": "S3rv30 tunn3l f41l: <code>{}</code>",
        "asset_read_error": "F41l3d t0 f3tch w3b 4553t5: <code>{}</code>",
        "open_button": "0p3n m1n1-4pp",
        "stop_button": "K1ll",
        "about_text": "<b>R34D TH15:</b>\nB0x w0n't l1ft cuz 2 m4ny pr0c5 — r3b00t. <c0d3>cm4</c0d3> j4nk t3mpl4t3, c0nf1g m4nu4lly.\n4l50:\n    1. F1r5t run = 51t3 l1nk, n0t w3b 4pp\n    2. U53 <c0d3>n0ch355</c0d3> + <c0d3>cm4</c0d3>\n    3. B0unc3 w1th <c0d3>n0ch355 -k1ll</c0d3> + <c0d3>n0ch355</c0d3>\nPr3-4lph4, bump1n t0 1.0.0 1f p33p5 v1b3.",
        "cma_start": "( ﾉ･ｪ･ )ﾉ <b>C0njur1n9 m1n1 4pp v14 B0tF4th3r...</b>",
        "cma_need_url": "Dr0p 4 URL f1r5t 0r run <c0d3>.n0ch355</c0d3>",
        "cma_done": "(*˘︶˘*) <b>5h1pp3d.</b>",
        "cma_error": "F41l: <code>{}</code>",
        "RuntimeError": "1nl1n3 b0t h4ndl3 n0t f0und",
        "not_supported_platform": "(┬┬＿┬┬) N0 5h0t 1n5t4ll1n' h3r3.\n\n(〜^∇^)〜 N0t 4 bu9, d0n't p1n9 5upp0rt."
    }

    strings_uwu = {
        "_cls_doc": "NoChess — web moduwe tuwu waunch a page as HTML owr Tewegwam Minyi-App. Add-on fowr Chess by @nuwwmod~",
        "starting": "( ﾉ･ｪ･ )ﾉ <b>Spinning up NoChess-chan...</b>",
        "online": "(*˘︶˘*) <b>NoChess is wunning, nyaa~</b>",
        "already_running": "ʕᵕᴥᵕʔ <b>NoChess awweady wunning, hehe</b>",
        "stopped": "･ﾟ･(｡>д<｡)･ﾟ･ NoChess went bye-bye",
        "not_running": "(✿╹◡╹) NoChess is sweepy...",
        "tunnel_error": "Serveo tunnew-bun oopsie: <code>{}</code>",
        "asset_read_error": "Couwdn't fetch the pwetty assets: <code>{}</code>",
        "open_button": "Open minyi-app~",
        "stop_button": "Stahp pwease",
        "about_text": "<b>Pwease wead cawefuwwy:</b>\nSewvew won't wake up cuz too many pwocesses. <code>cma</code> setups fwom wonky tempwate, tweak config yuwsewf.\nAwso:\n    1. Fiwst waunch = site wink, not web app\n    2. Use <code>nochess</code>, den <code>cma</code>\n    3. Westawt wiff <code>nochess -kill</code> + <code>nochess</code>\nPwe-awpha, watew 1.0.0 if peopwe wike~. ",
        "cma_start": "( ﾉ･ｪ･ )ﾉ <b>Making minyi-app in BotFather-chan...</b>",
        "cma_need_url": "Set URL fiwst owr wun <code>.nochess</code>, pwease~",
        "cma_done": "(*˘︶˘*) <b>Aww done, nya!</b>",
        "cma_error": "Oopsie woopsie: <code>{}</code>",
        "RuntimeError": "inyine bot usewnyame nyot found",
        "not_supported_platform": "(┬┬＿┬┬) Unfowtunyatewy, can't instaww hewe.\n\n(〜^∇^)〜 Nyot an ewwow, don't contact suppowt."
    }

    async def client_ready(self):
        platform = utils.get_named_platform()
        if platform in ("HikkaHost"):
            raise loader.LoadError(self.strings("not_supported_platform"))
    
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
        self._serveo_proc = None
        self._assets_lock = asyncio.Lock()
        self._assets_html = None
        self._assets_css = None
        self._assets_js = None

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
        async with self._assets_lock:
            if self._assets_html is not None:
                return self._assets_html, self._assets_css, self._assets_js
            html, css, js = await asyncio.gather(
                self.read_remote_asset(html_raw),
                self.read_remote_asset(css_raw),
                self.read_remote_asset(js_raw),
            )
            self._assets_html = html
            self._assets_css = css
            self._assets_js = js
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

    async def stop_server(self):
        was_running = bool(self.runner)
        await self._kill_serveo()
        if self.runner:
            await self.runner.cleanup()
            self.runner = None
        self.tunnel_url = None
        return was_running

    @staticmethod
    def _strip_ansi(s):
        return re.sub(r'\x1b\[[0-?]*[ -/]*[@-~]', '', s)

    async def _start_serveo(self, port):
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

    @loader.command(
        ru_doc="[-kill] Вызвать веб интерфейс для просмотра партии",
        de_doc="[-kill] Webinterface zum Anzeigen der Partie aufrufen",
        ua_doc="[-kill] Викликати веб інтерфейс для перегляду партії",
        jp_doc="[-kill] チェスゲームを表示するウェブインターフェースを呼び出す",
        neofit_doc="[-kill] Yeet the web ui 2 render a game",
        tiktok_doc="[-kill] Открыть веб-вьюху шахмат, no 🧢",
        leet_doc="[-kill] C4ll w3b 1nt3rf4c3 f0r ch355 v13w",
        uwu_doc="[-kiww] Caww web intewface fow chess viewie~",
    )
    async def nochess(self, message: Message):
        """[-kill] Call web interface to view chess game"""
        try:
            return await self.nochess_args(message)
        except Exception as error:
            await self.stop_server()
            return await utils.answer(
                message,
                self.strings["tunnel_error"].format(utils.escape_html(str(error))),
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
            self.tunnel_url = await self._start_serveo(port)
        except Exception as error:
            await self.stop_server()
            return await utils.answer(
                message,
                self.strings["tunnel_error"].format(utils.escape_html(str(error))),
            )
        if is_tg_direct:
            access_url = mini_url
        else:
            base = (self.tunnel_url or "").rstrip("/")
            access_url = f"{base}/?token={self.access_token}" if base and self.access_token else base
        await self.send_form(message, access_url)

    @loader.command(
        ru_doc="Создаёт и настраивает мини-приложение через BotFather",
        de_doc="Erstellt und konfiguriert Mini-App via BotFather",
        ua_doc="Створює і налаштовує міні-застосунок через BotFather",
        jp_doc="BotFather経由でミニアプリを作成・設定します",
        neofit_doc="Sp00n-feed BotFather 2 forge ya mini app",
        tiktok_doc="Делает мини-апп через BotFather, изи",
        leet_doc="Cr34t3 & c0nf19 m1n1-4pp v14 B0tF4th3r",
        uwu_doc="Cweates & configuwes mini-app via BotFathew~",
    )
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

    @loader.command(
        ru_doc="ВАЖНО К ПРОЧТЕНИЮ",
        de_doc="WICHTIG ZU LESEN",
        ua_doc="ВАЖЛИВО ДО ПРОЧИТАННЯ",
        jp_doc="重要なお知らせ",
        neofit_doc="RTFM BRO",
        tiktok_doc="ЧИТНИ СЮДА",
        leet_doc="R34D TH15",
        uwu_doc="WEAD ME!!",
    )
    async def about(self, message: Message):
        """IMPORTANT READING"""
        await utils.answer(message, self.strings["about_text"])
    async def on_unload(self):
        await self.stop_server()

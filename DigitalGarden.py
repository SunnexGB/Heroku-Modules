# meta developer: @H_SunMods
# requires: aiohttp
# meta pic: https://r2.fakecrime.bio/uploads/5a53da6e-111c-4174-a468-e71b922075d8.jpg
# meta banner: https://r2.fakecrime.bio/uploads/5a53da6e-111c-4174-a468-e71b922075d8.jpg
# meta fhsdesc: Obsidian, Notes, Web, H_SunMods, Sunnex, SunnexGB
# ver
__version__ = ("B", "E", "T", "A")
from herokutl.types import Message
from .. import loader, utils
import aiohttp
import base64
import json
import re

@loader.tds
class DigitalGarden(loader.Module):
    """Module for publick your notes to web"""

    strings = {
        "name": "DigitalGarden",
        "no_config": "<b>Config not set.</b> Use <code>{prefix}cfg DigitalGarden</code> and enter <code>repo_name</code>, <code>username</code> and <code>github_token</code>",
        "no_args": "<b>Usage:</b> <code>{prefix}dg Name [tag1,tag2]</code>",
        "no_reply": "<b>Reply to message or <code>.txt</code> or <code>.md</code></b>",
        "published": "<b>Note <code>{name}</code> published! Waiting end deploy.</b>",
        "updated": "<b>Note <code>{name}</code> updated! Waiting end deploy.</b>",
        "tags_updated": "<b>For note <code>{name}</code> tags be updated.</b>",
        "not_found": "<b>Note <code>{name}</code> not found in repository.</b>",
        "unsupported_file": "<b>Only <code>.txt</code> and <code>.md</code> are supported</b>",
        "push_error": "<b>Failed to push.</b>",
        "upd_note": "Update note",
        "upd_settings": "Update settings",
        "guide": '<b>module setup guide => </b><a href="https://sunnexgb.github.io/Heroku-documentations-md/guide-for-digital-garden-module/"><b>here</b></a>',
        # num num configs:
        "_cfg_doc_repo_name_cfg": "The name of the GitHub repository",
        "_cfg_doc_username_cfg": "Your GitHub username",
        "_cfg_doc_github_token_cfg": 'A GitHub token with contents permissions. You can see how to generate it <a href="https://docs.forestry.md/advanced/fine-grained-access-token/"> here!</a>',
        "_cfg_doc_theme_cfg": 'Theme a your website\n <b>themes list:</b> <a href="https://raw.githubusercontent.com/obsidianmd/obsidian-releases/master/community-css-themes.json"> here!</a>',
        "_cfg_doc_sitename_cfg": "The name of your site. This will be displayed as the site header.",
        "_cfg_doc_logo_cfg": "Raw path to an image in your vault to use as a logo instead of the sitename. Leave blank to show sitename text.",
        "_cfg_doc_main_lang_cfg": "Main page language",
        "_cfg_doc_fav_icon_cfg": "Icon for your site",
        "_cfg_doc_full_resolution_cfg": "By default, the images on your site are compressed to make your site load faster. If you instead want to use the full resolution images, enable this setting.",
        "_cfg_doc_custom_filters_cfg": "Define regex filters to replace note content before publishing.\nFormat: <code>regex pattern, replacement, regex flags</code>\nExample: filter <code>:smile:,🦊, g</code> will replace text with real emojis",
    }

    strings_ru = {
        "_cls_doc": "Модуль для публикации ваших заметок в веб",
        "no_config": "<b>Конфиг не настроен.</b> Используй <code>{prefix}cfg DigitalGarden</code> и вставь <code>repo_name</code>, <code>username</code> и <code>github_token</code>",
        "no_args": "<b>Ты не указал аргументов:</b> <code>{prefix}dg Название [тег1,тег2]</code>",
        "no_reply": "<b>Ответь на сообщение или на файл <code>.txt</code> или <code>.md</code></b>",
        "published": "<b>Заметка <code>{name}</code> опубликована! Ожидайте окончания деплоя.</b>",
        "updated": "<b>Заметка <code>{name}</code> обновлена! Ожидайте окончания деплоя.</b>",
        "tags_updated": "<b>Для заметки <code>{name}</code> были обновлены теги.</b>",
        "not_found": "<b>Заметка <code>{name}</code> не найдена в репозитории.</b>",
        "unsupported_file": "<b>Поддерживаются только <code>.txt</code> и <code>.md</code></b>",
        "push_error": "<b>Не удалось запушить</b>",
        "upd_note": "Обновление заметки",
        "upd_settings": "Обновление настроек",
        "guide": '<b>гайд по настройке модуля => </b><a href="https://sunnexgb.github.io/Heroku-documentations-md/guide-for-digital-garden-module/"><b>тут</b></a>',
        # конфиги типа:
        "_cfg_doc_repo_name_cfg": "Название гитхаб репозитория",
        "_cfg_doc_username_cfg": "Ваш гитхаб юзернейм",
        "_cfg_doc_github_token_cfg": 'Гитхаб токен. Инструкция по тому как создать токен можно узанть <a href="https://docs.forestry.md/advanced/fine-grained-access-token/"> тут!</a>',
        "_cfg_doc_theme_cfg": 'Тема для вашего веб-сайта\n <b>Список тем:</b> <a href="https://raw.githubusercontent.com/obsidianmd/obsidian-releases/master/community-css-themes.json"> тут!</a>',
        "_cfg_doc_sitename_cfg": "Имя сайта которое будет отображаться в заголовке сайта",
        "_cfg_doc_logo_cfg": "Абсолютный путь к лого, которое будет использоваться в качестве логотипа вместо названия сайта. Оставьте поле пустым, чтобы отобразить название сайта.",
        "_cfg_doc_main_lang_cfg": "ну язык сайта в целом бесполезная хуйня",
        "_cfg_doc_fav_icon_cfg": "Иконка для вашего сайта",
        "_cfg_doc_full_resolution_cfg": "По умолчанию изображения на вашем сайте сжимаются, чтобы ускорить деплой. Если вы хотите использовать изображения в оригинале, включите этот параметр.",
        "_cfg_doc_custom_filters_cfg": "Регекс фильтры для заменты текста перед публикацией.\nСинтаксис: <code>регекс, на что заменить, регекс флаги</code>\nПример: <code>:smile:,🦊, g</code> заменит текст на настоящие смайлики",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "repo_name",
                None,
                lambda: self.strings("_cfg_doc_repo_name_cfg"),
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "username",
                None,
                lambda: self.strings("_cfg_doc_username_cfg"),
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "github_token",
                None,
                lambda: self.strings("_cfg_doc_github_token_cfg"),
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "theme",
                "AnubisNekhet/AnuPpuccin",
                lambda: self.strings("_cfg_doc_theme_cfg"),
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "sitename",
                "Digital Garden",
                lambda: self.strings("_cfg_doc_sitename_cfg"),
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "logo",
                None,
                lambda: self.strings("_cfg_doc_logo_cfg"),
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "main_lang",
                "en",
                lambda: self.strings("_cfg_doc_main_lang_cfg"),
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "fav_icon",
                None,
                lambda: self.strings("_cfg_doc_fav_icon_cfg"),
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "full_resolution",
                True,
                lambda: self.strings("_cfg_doc_full_resolution_cfg"),
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "custom_filters",
                ['<tg-emoji\\s+emoji-id=\"[^\"]*\">([^<]+)</tg-emoji>,$1,g'],
                lambda: self.strings("_cfg_doc_custom_filters_cfg"),
                validator=loader.validators.Series(
                validator=loader.validators.String(),
                ),
            ),
        )
        # идкя спизжена у спотифаймода
        self.github_api = "https://api.github.com"
        self.notes_path = "src/site/notes"
        self.settings_path = ".env"

    async def gh_get_file(self, path):
        url = f"{self.github_api}/repos/{self.config['username']}/{self.config['repo_name']}/contents/{path}"
        headers = {
            "Authorization": f"token {self.config['github_token']}",
            "Accept": "application/vnd.github.v3+json",
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                return None

    async def gh_push(self, path, content, commit_message):
        existing = await self.gh_get_file(path)
        sha = existing.get("sha") if existing else None
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        url = f"{self.github_api}/repos/{self.config['username']}/{self.config['repo_name']}/contents/{path}"
        headers = {
            "Authorization": f"token {self.config['github_token']}",
            "Accept": "application/vnd.github.v3+json",
        }
        payload = {"message": commit_message, "content": encoded}
        if sha:
            payload["sha"] = sha
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers, json=payload) as response:
                return response.status in (200, 201), existing is not None

    async def dg_settings(self):
        existing = await self.gh_get_file(self.settings_path)
        if not existing:
            return
        raw_content = base64.b64decode(existing["content"].replace("\n", "")).decode("utf-8")
        theme_settings = {
            "THEME": f"https://raw.githubusercontent.com/{self.config['theme']}/HEAD/theme.css",
            "SITE_NAME_HEADER": self.config["sitename"],
            "SITE_MAIN_LANGUAGE": self.config["main_lang"],
            "USE_FULL_RESOLUTION_IMAGES": str(self.config["full_resolution"]).lower(),
        }
        lines = raw_content.splitlines()
        result_lines = []
        for line in lines:
            if "=" in line and not line.startswith("#"):
                key = line.split("=", 1)[0]
                if key in theme_settings:
                    result_lines.append(f"{key}={theme_settings[key]}")
                    continue
            result_lines.append(line)
        await self.gh_push(
            self.settings_path,
            "\n".join(result_lines),
            self.strings["upd_settings"],
        )

    def html_to_md(self, text):
        def replace_code_block(match):
            lang = match.group(1) or ""
            code = (
                match.group(2)
                .replace("&lt;", "<")
                .replace("&gt;", ">")
                .replace("&amp;", "&")
                .replace("&quot;", '"')
                .replace("&#39;", "'")
            )
            return f"```{lang}\n{code}\n```"

        def convert_spoiler(match):
            lines = match.group(1).strip().split("\n")
            return "> [!spoiler]- Нажмите, чтобы посмотреть текст\n" + "\n".join(f"> {line}" for line in lines)
        text = re.sub(r'(?s)<pre><code(?:\s+class="language-([^"]*)")?>(.*?)</code></pre>', replace_code_block, text)
        text = re.sub(r'(?s)<tg-spoiler>(.*?)</tg-spoiler>', convert_spoiler, text)
        text = re.sub(r'\[\[([^\]|\\]+)\]\]', lambda m: f'[[{m.group(1)}\\|{m.group(1)}]]', text)
        text = (
            text
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&amp;", "&")
            .replace("&quot;", '"')
            .replace("&#39;", "'")
        )
        return text

    def dg_custom_filters(self, text):
        for filter_entry in self.config["custom_filters"]:
            parts = filter_entry.split(",")
            if len(parts) < 2:
                continue
            pattern = parts[0]
            replacement = re.sub(r'\$(\d+)', r'\\\1', parts[1])
            flags_str = parts[2] if len(parts) > 2 else ""
            re_flags = re.IGNORECASE if "i" in flags_str else 0
            try:
                text = re.sub(pattern, replacement, text, flags=re_flags)
            except re.error:
                pass
        return text

    def create_note(self, note_name, extra_tags=None):
        frontmatter = {"dg-publish": True, "permalink": f"/{note_name}/", "dg-note-properties": {}}
        if extra_tags:
            for tag, value in extra_tags.items():
                frontmatter[tag] = value
        return f"---\n{json.dumps(frontmatter, ensure_ascii=False)}\n---\n\n"

    def tag_keys(self, content):
        if not content.startswith("---"):
            return {}, content
        end_index = content.find("---", 3)
        if end_index == -1:
            return {}, content
        frontmatter_block = content[3:end_index].strip()
        body = content[end_index + 3:].strip()
        try:
            data = json.loads(frontmatter_block)
            tags = {k: v for k, v in data.items() if k not in ("dg-publish", "permalink", "dg-note-properties")}
        except (json.JSONDecodeError, ValueError):
            tags = {}
            for line in frontmatter_block.split("\n"):
                if ":" in line:
                    key, _, raw_value = line.partition(":")
                    key = key.strip()
                    if key != "dg-publish":
                        tags[key] = raw_value.strip().lower() == "true"
        return tags, body

    def get_dg_tags(self, tags_arg):
        return [tag.strip() for tag in tags_arg.split(",") if tag.strip()]

    @loader.command(ru_doc="Опубликовать вашу заметку в веб .dg Name")
    async def dg(self, message: Message):
        """Publish your note to web .dg Name"""
        if (self.config["repo_name"] is None or self.config["username"] is None or self.config["github_token"] is None):
            await utils.answer(message, self.strings["no_config"].format(prefix=self.get_prefix()))
            return
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings["no_args"].format(prefix=self.get_prefix()))
            return
        note_name = args[0]
        extra_tags = {}
        if len(args) > 1:
            for tag in self.get_dg_tags(args[1]):
                extra_tags[tag] = True
        reply = await message.get_reply_message()
        if not reply:
            await utils.answer(message, self.strings["no_reply"])
            return
        if reply.document:
            note_name = ""
            for attribute in reply.document.attributes:
                if hasattr(attribute, "note_name"):
                    note_name = attribute.note_name
                    break
            if not (note_name.endswith(".txt") or note_name.endswith(".md")):
                await utils.answer(message, self.strings["unsupported_file"])
                return
            file_bytes = await reply.download_media(bytes)
            md_content = file_bytes.decode("utf-8")
        else:
            raw_html = reply.text or ""
            raw_html = self.dg_custom_filters(raw_html)
            md_content = self.html_to_md(raw_html)
        full_content = self.create_note(note_name, extra_tags) + md_content
        file_path = f"{self.notes_path}/{note_name}.md"
        success, was_existing = await self.gh_push(
            file_path, full_content, self.strings["upd_note"]
        )
        if success:
            await self.dg_settings()
            string_key = "updated" if was_existing else "published"
            await self.inline.form(
            message=message,
            text=self.strings[string_key].format(name=note_name),
            reply_markup=[
                {
                    "text": "Check your note",
                    "url": f"https://{self.config['username']}.github.io/{self.config['repo_name']}/{note_name}/",
                }
            ],
        )
        else:
            await utils.answer(message, self.strings["push_error"])

    @loader.command(ru_doc="Управление статусом dg-тегов")
    async def dgc(self, message: Message):
        """Managing status dg-tags"""
        if (self.config["repo_name"] is None or self.config["username"] is None or self.config["github_token"] is None):
            await utils.answer(message, self.strings["no_config"].format(prefix=self.get_prefix()))
            return
        args = utils.get_args(message)
        if len(args) < 2:
            await utils.answer(message, self.strings["no_args"].format(prefix=self.get_prefix()))
            return
        note_name = args[0]
        tags_to_disable = self.get_dg_tags(args[1])
        file_path = f"{self.notes_path}/{note_name}.md"
        existing = await self.gh_get_file(file_path)
        if not existing:
            await utils.answer(message, self.strings["not_found"].format(name=note_name))
            return
        raw_content = base64.b64decode(existing["content"].replace("\n", "")).decode("utf-8")
        current_tags, body = self.tag_keys(raw_content)
        for tag in tags_to_disable:
            if tag != "dg-publish":
                current_tags[tag] = False
        full_content = self.create_note(note_name, current_tags) + body
        success, _ = await self.gh_push(
            file_path, full_content, self.strings["upd_note"]
        )
        if success:
            await self.inline.form(
                message=message,
                text=self.strings["tags_updated"].format(name=note_name),
                reply_markup=[
            {
                "text": "Check your note",
                "url": f"https://{self.config['username']}.github.io/{self.config['repo_name']}/{note_name}/",
            }
        ],
    )
        else:
            await utils.answer(message, self.strings["push_error"])

    @loader.command(ru_doc="Гайд для работы с модулем")
    async def guide(self, message: Message):
        """Getting started Guide for module"""
        await utils.answer(message, self.strings["guide"])
# meta pic: https://r2.fakecrime.bio/uploads/60d09d47-5f96-40d0-95cf-d8af02de56a0.jpg
# meta banner: https://r2.fakecrime.bio/uploads/60d09d47-5f96-40d0-95cf-d8af02de56a0.jpg
# meta developer: @H_SunMods
# current version
__version__ = (1, 0, 0)

import asyncio
import os
from .. import loader
from .._internal import restart


@loader.tds
class BranchManager(loader.Module):
    """Module for managment your userbot verions."""

    strings = {
        "name": "BranchManager",
        "panel_msg": """<b>Current repository:</b> <code>{repo_name}</code>
<b>Current branch:</b> <code>{branch}</code>
<b>Link:</b> <code>{link}</code>""",
        "warning_msg": """<b><tg-emoji emoji-id=5213205860498549992>⚠️</tg-emoji></b><b>Warning</b>
This module allows you to switch branch ur userbot. 
Incorrect branch selection <u>may lead to breakage and other risks</u>.
Clicking the button below, you confirm that you <u>accept all risks and understond the purpose for which you are using this module</u>.
""",
        "choose_repo": "Choose a repository to switch",
        "choose_branch": "Choose a branch for <code>{repo_name}</code>",
        "repo_added": "<code>{repo_name}</code> added",
        "repo_not_found": "Repository not found",
        "switch_success": """You have successfully switched to <code>{branch}</code> branch 
on <code>{repo_name}</code> repository""",
        "add_repo_button": "Add branch", 
        "add_repo_input": "Paste the repository link in .git format",
        "repo_list_button": "List branches",
        "close_button": "Close",
        "back_button": "Back",
        "understand_button": "I understond",
    }

    strings_ru = {
        "_cls_doc": "Модуль для управления версиями вашего юзер бота",
        "panel_msg": """<b>Нынешний репозиторий:</b> <code>{repo_name}</code>
<b>Нынешняя ветка:</b> <code>{branch}</code>
<b>Ссылка:</b> <code>{link}</code>""",
        "warning_msg": """<b><tg-emoji emoji-id=5213205860498549992>⚠️</tg-emoji></b><b>Предупреждение</b>
Этот модуль позволяет переключать ветку вашего юзербота. 
Неверный выбор ветки <u>может привести к поломке и другим рискам</u>.
Нажимая на кнопку ниже, вы подтверждаете, что <u>принимаете все риски и понимаете в каких целях вы используете данный модуль</u>.
""",
        "choose_repo": "Выберите репозиторий для перехода на него",
        "choose_branch": "Выберите ветку для <code>{repo_name}</code>",
        "repo_added": "<code>{repo_name}</code> добавлен",
        "repo_not_found": "Репозиторий не найден",
        "switch_success": """Вы успешно перешли на ветку <code>{branch}</code> 
репозитория <code>{repo_name}</code>""",
        "add_repo_button": "Добавить ветку",
        "add_repo_input": "Вставьте ссылку на репозиторий в формате .git",
        "repo_list_button": "Список веток",
        "close_button": "Закрыть",
        "back_button": "Назад",
        "understand_button": "Я понимаю",
    }

    def __init__(self):
        self.default_branch = "master"
        # я осознал что конфиг который я писал в скелете,не имеет смыла,но мне лень переписывать
        self.config = loader.ModuleConfig(
            loader.ConfigCategory(
                "settings",
                loader.ConfigValue(
                    "default_repo",
                    "Codrago/Heroku",
                    "Репозиторий по умолчанию",
                ),
                loader.ConfigValue(
                    "default_link",
                    "https://github.com/coddrago/Heroku.git",
                    "Ссылка на репозиторий по умолчанию",
                    validator=loader.validators.Link(),
                ),
                loader.ConfigValue(
                    "default_branches",
                    ["master", "args", "beta", "dev", "kuri"],
                    "Список веток репозитория по умолчанию",
                ),
                doc="Конфигурация для работы с репозиториями",
            ),
        )

    async def client_ready(self, client, db):
        if not self.get("repositories"):
            self.set(
                "repositories",
                {
                    self.config["default_repo"]: {
                        "link": self.config["default_link"],
                        "branches": self.config["default_branches"],
                        "current_branch": self.default_branch,
                    }
                },
            )

        if not self.get("current_repo"):
            self.set(
                "current_repo", 
                self.config["default_repo"]
            )

    async def git_handler(self, command):
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "echo"},
        )
        stdout, stderr = await process.communicate()
        return stdout.decode().strip(), stderr.decode().strip()

    def owner_and_repo(self, repo_link):
        return "/".join(
            repo_link.rstrip("/").removesuffix(".git").split("/")[-2:]
        )

    async def sw_repo(self, repo_link):
        await self.git_handler("git stash")
        await self.git_handler(f"git remote set-url origin {repo_link}")
        await self.git_handler("git fetch")

    async def fetch_branches(self, call, query = ""):
        repo_link = query.strip()
        if not repo_link:
            await call.edit(
                text=self.strings["repo_not_found"],
                reply_markup=await self.main_panel(),
            )
            return
        repo_name = self.owner_and_repo(repo_link)
        output, _ = await self.git_handler(f"git ls-remote --heads {repo_link}")
        branches = [
            line.split("refs/heads/")[-1]
            for line in output.splitlines()
            if "refs/heads/" in line
        ]

        if not branches:
            await call.edit(
                text=self.strings["repo_not_found"],
                reply_markup=await self.main_panel(),
            )
            return

        repositories = self.get(
            "repositories", 
            {}
        )
        repositories[repo_name] = {
            "link": repo_link,
            "branches": branches,
            "current_branch": branches[0] if branches else self.default_branch,
        }
        self.set(
            "repositories", 
            repositories
        )
        await call.edit(
            text=self.strings["repo_added"].format(repo_name=repo_name),
            reply_markup=await self.main_panel(),
        )

    async def get_repo_list(self, key = None):
        repositories = self.get(
            "repositories", 
            {}
        )
        current_repo = self.get(
            "current_repo", 
            self.config["default_repo"]
        )
        repo_data = repositories.get(
            current_repo, 
            {}
        )

        data = {
            "rn": current_repo,
            "b": repo_data.get("branches", self.config["default_branches"]),
            "rl": repo_data.get("link", self.config["default_link"]),
        }

        if key in data:
            return data[key]
        return f"{data['rn']},{data['b']},{data['rl']}"

    async def get_repos_db(self):
        repositories = self.get(
            "repositories", 
            {}
        )
        current_repo = self.get(
            "current_repo", 
            self.config["default_repo"]
        )
        repo_data = repositories.get(current_repo, {})
        return (
            current_repo,
            repo_data.get(
                "current_branch", 
                self.default_branch
            ),
            repo_data.get(
                "link", 
                self.config["default_link"]
            ),
        )

    async def main_panel(self):
        return [
            [
                {
                    "text": self.strings["add_repo_button"], "input": self.strings["add_repo_input"], "handler": self.fetch_branches,
                }
            ],
            [
                {
                    "text": self.strings["repo_list_button"], "callback": self.branch_list
                }
            ],
            [
                {
                    "text": self.strings["close_button"], "action": "close"
                }
            ],
        ]

    async def sw_cfg(self, call):
        self.set(
            "user_see_msg", 
            True
        )
        await call.delete()

    async def branch_list(self, call):
        repositories = self.get("repositories", {})
        btns = [
            [
                {
                    "text": repo_name, "callback": self.sw_branch, "args": (repo_name,)
                }
            ]
            for repo_name in repositories
        ]
        btns.append(
            [
                {
                    "text": self.strings["back_button"], "callback": self.upd_main_info
                }
            ]
        )

        await call.edit(
            text=self.strings["choose_repo"],
            reply_markup=btns,
        )

    async def sw_branch(self, call, repo_name):
        repositories = self.get(
            "repositories", 
            {}
        )
        branches = repositories.get(
            repo_name, 
            {}
        ).get("branches", [])
        btns = [
            [
                {
                    "text": branch,
                    "callback": self.sw_new_repo,
                    "args": (repo_name, branch),
                }
            ]
            for branch in branches
        ]
        btns.append(
            [
                {
                    "text": self.strings["back_button"], "callback": self.branch_list
                }
            ]
        )

        await call.edit(
            text=self.strings["choose_branch"].format(repo_name=repo_name),
            reply_markup=btns,
        )

    async def sw_new_repo(self, call, repo_name, branch):
        repositories = self.get(
            "repositories", 
            {}
        )
        repo_data = repositories.get(repo_name)

        if repo_data is None:
            await call.edit(
                text=self.strings["repo_not_found"]
            )
            return
        
        await self.sw_repo(repo_data["link"])
        await self.git_handler("git fetch")
        await self.git_handler(f"git checkout {branch}")
        await self.git_handler("git pull")

        repo_data["current_branch"] = branch
        repositories[repo_name] = repo_data
        self.set("repositories", repositories)
        self.set("current_repo", repo_name)

        await call.edit(
            text=self.strings["switch_success"].format(branch=branch, repo_name=repo_name)
        )
        restart()

    async def upd_main_info(self, call):
        repo_name, branch, link = await self.get_repos_db()
        await call.edit(
            text=self.strings["panel_msg"].format(
                repo_name=repo_name, 
                branch=branch, 
                link=link
            ),
            reply_markup=await self.main_panel(),
        )

    @loader.command(ru_doc="- Открыть панель управлеия версиями", alias="bm")
    async def branchmanagercmd(self, message):
        """- Open version control panel"""
        repo_name, branch, link = await self.get_repos_db()
        
        if not self.get(
            "user_see_msg", 
            False
        ):
            await self.inline.form(
                self.strings["warning_msg"],
                message=message,
                reply_markup=[
                    [
                        {
                            "text": self.strings["understand_button"], "callback": self.sw_cfg,
                        }
                    ]
                ],
            )
            return

        await self.inline.form(
            self.strings["panel_msg"].format(
                repo_name=repo_name, 
                branch=branch, 
                link=link
            ),
            message=message,
            reply_markup=await self.main_panel(),
        )
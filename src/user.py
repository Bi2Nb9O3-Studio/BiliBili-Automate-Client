import requests


class User:
    def __init__(self, mid: int | None = -1) -> None:
    #     self.mid = mid
    #     self.refresh_token = ''
    #     self.name = ''
    #     self.last_cookies_update = -1
    #     self.session = utils.getNewSession()
    #     self.logined = 0
    #     self.logger = cli.setup_logger("User")
    #     self.set_to_default = set_to_default or global_vars.default_user == Ellipsis

    # def login(self, auth: BaseLogin):
    #     auth.build(self.session)
    #     task = utils.Task('UserLogin', auth, kwargs={'user': self})
    #     taskuuid = task.uuid
    #     global_vars.tasks[taskuuid] = task
    #     global_vars.tasks[taskuuid].start()
    #     self.logined = 1

    # def updateMID(self, mid: int, no_output: bool = False):
    #     if self.mid == -1:
    #         self.mid = mid
    #         global_vars.users[mid] = self
    #         global_vars.users[-1].remove(self)
    #         if not no_output:
    #             self.logger.info(f"New User MID set to {mid}")
    #     elif mid != self.mid:
    #         self.mid = mid
    #         if not no_output:
    #             self.logger.info(f"User MID updated to {mid}")

    #     else:
    #         if not no_output:
    #             self.logger.info(f"User MID is {mid}")

    # def check_user(self, no_output: bool = False):
    #     # https: // api.bilibili.com/x/web-interface/nav
    #     resp = self.session.get(
    #         "https://api.bilibili.com/x/web-interface/nav").json()
    #     self.updateMID(resp['data']['mid'], no_output=no_output)
    #     self.name = resp['data']['uname']
    #     return resp

    # def __str__(self) -> str:
    #     if self.logined == 2:
    #         self.check_user(True)
    #         return f"User {self.name}({self.mid})"
    #     elif self.logined == 1:
    #         return f"User {self.mid} (Logining)"

    #     return f"User {self.mid}(Not Logined or New)"

    # def save_cookies(self):
    #     try:
    #         path = utils.ensure_path("./data/user_cache")
    #         file = utils.ensure_file(path+f"/{self.mid}.json")
    #         content = {
    #             "cookies": self.session.cookies.get_dict(),
    #             "refresh_token": self.refresh_token,
    #             "last_cookies_update": self.last_cookies_update
    #         }
    #         json.dump(content,
    #                   open(file, "w", encoding="utf-8"))
    #     except Exception as e:
    #         self.logger.error(repr(e))

    # def need_refresh_cookies(self):
    #     resp = self.session.get(
    #         "https://passport.bilibili.com/x/passport-login/web/cookie/info")
    #     return resp.json()

    # def refresh_cookies(self):
    #     self.logger.info(f"Refreshing cookies for account {self.mid}")
    #     need_refresh = self.need_refresh_cookies()
    #     if need_refresh['code'] != 0:
    #         self.logger.error(f"Account {self.mid} didn't login in.")
    #         return
    #     if need_refresh['data']['refresh']:
    #         time_stamp = need_refresh['data']['timestamp']
    #         correspond_path = utils.getCorrespondPath(time_stamp)
    #         resp = self.session.get(
    #             f"https://www.bilibili.com/correspond/1/{correspond_path}")
    #         soup = bs4.BeautifulSoup(resp.text, 'html.parser')
    #         result = soup.find("div", {"id": "1-name"})
    #         if isinstance(result, NoneType):
    #             self.logger.error(
    #                 f"Can't auto refresh cookies for account {self.mid}.Pleases login again.")
    #             return
    #         refresh_csrf = result.text
    #         resp = self.session.post("https://passport.bilibili.com/x/passport-login/web/cookie/refresh", {"csrf": self.session.cookies.get(
    #             "bili_jct"), "refresh_csrf": refresh_csrf, "source": "main_web", "refresh_token": self.refresh_token})
    #         if resp.json()['code'] != 0:
    #             self.logger.error(
    #                 f"Error during refreshing cookies. Code={resp.json()['code']}. Response={resp.text}, Request={resp.request}")
    #             return
    #         else:
    #             self.logger.success(f"Account {self.mid} cookies refreshed.")
    #             old_token = self.refresh_token
    #             self.refresh_token = resp.json()['data']['refresh_token']

    #         # comfirm update
    #         resp = self.session.post(
    #             "https://passport.bilibili.com/x/passport-login/web/confirm/refresh", {"csrf": self.session.cookies.get("bili_jct"), "refresh_token": old_token})
    #         if resp.json()['code'] != 0:
    #             self.logger.error(
    #                 f"Error during confirming refresh. Code={resp.json()['code']}. Response={resp.text}, Request={resp.request}")
    #             return

    #         self.logger.success(
    #             f"Account {self.mid} cookies refresh:comfired.")
    #         self.save_cookies()
    #     else:
    #         self.logger.info("No need to refresh cookies.")
    #         self.logger.info(need_refresh)
        self.mid = mid
        self.refresh_token = ''
        self.name = ''
        self.last_cookies_update = -1
        self.session: requests.Session = None
        self.logined = 0
        # self.logger = setup_logger("User")
        # self.set_to_default = set_to_default or global_vars.default_user == Ellipsis

users={}
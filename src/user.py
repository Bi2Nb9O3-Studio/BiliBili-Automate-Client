from ctypes import util
import json
import logging
import os
import pdb
import pickle
import queue
import time
from tkinter import N
from tracemalloc import stop
from types import NoneType
import bs4
import requests

# import cli
import utils
import cli
import global_vars


class BaseLogin():
    def __init__(self) -> None:
        self.logger = cli.setup_logger("Auth")

    def build(self, session: requests.Session):
        self.session = session
        return self

    def __call__(self, statusQueue: queue.LifoQueue, commandQueue: queue.LifoQueue, user, task: utils.Task):
        ...

    def checkUser(self):
        # https: // api.bilibili.com/x/web-interface/nav
        return self.session.get("https://api.bilibili.com/x/web-interface/nav").json()


class User:
    def __init__(self, mid: int | None = -1, set_to_default: bool = False) -> None:
        self.mid = mid
        self.refresh_token = ''
        self.name = ''
        self.last_cookies_update = -1
        self.session = utils.getNewSession()
        self.logined = 0
        self.logger = cli.setup_logger("User")
        self.set_to_default = set_to_default or global_vars.default_user == Ellipsis

    def login(self, auth: BaseLogin):
        auth.build(self.session)
        task = utils.Task('UserLogin', auth, kwargs={'user': self})
        taskuuid = task.uuid
        global_vars.tasks[taskuuid] = task
        global_vars.tasks[taskuuid].start()
        self.logined = 1

    def updateMID(self, mid: int, no_output: bool = False):
        if self.mid == -1:
            self.mid = mid
            global_vars.users[mid] = self
            global_vars.users[-1].remove(self)
            if not no_output:
                self.logger.info(f"New User MID set to {mid}")
        elif mid != self.mid:
            self.mid = mid
            if not no_output:
                self.logger.info(f"User MID updated to {mid}")

        else:
            if not no_output:
                self.logger.info(f"User MID is {mid}")

    def check_user(self, no_output: bool = False):
        # https: // api.bilibili.com/x/web-interface/nav
        resp = self.session.get(
            "https://api.bilibili.com/x/web-interface/nav").json()
        self.updateMID(resp['data']['mid'], no_output=no_output)
        self.name = resp['data']['uname']
        return resp

    def __str__(self) -> str:
        if self.logined == 2:
            self.check_user(True)
            return f"User {self.name}({self.mid})"
        elif self.logined == 1:
            return f"User {self.mid} (Logining)"

        return f"User {self.mid}(Not Logined or New)"

    def save_cookies(self):
        try:
            path = utils.ensure_path("./data/user_cache")
            file = utils.ensure_file(path+f"/{self.mid}.json")
            content = {
                "cookies": self.session.cookies.get_dict(),
                "refresh_token": self.refresh_token,
                "last_cookies_update": self.last_cookies_update
            }
            json.dump(content,
                      open(file, "w", encoding="utf-8"))
        except Exception as e:
            self.logger.error(repr(e))

    def need_refresh_cookies(self):
        resp = self.session.get(
            "https://passport.bilibili.com/x/passport-login/web/cookie/info")
        return resp.json()

    def refresh_cookies(self):
        self.logger.info(f"Refreshing cookies for account {self.mid}")
        need_refresh = self.need_refresh_cookies()
        if need_refresh['code'] != 0:
            self.logger.error(f"Account {self.mid} didn't login in.")
            return
        if need_refresh['data']['refresh']:
            time_stamp = need_refresh['data']['timestamp']
            correspond_path = utils.getCorrespondPath(time_stamp)
            resp = self.session.get(
                f"https://www.bilibili.com/correspond/1/{correspond_path}")
            soup = bs4.BeautifulSoup(resp.text, 'html.parser')
            result = soup.find("div", {"id": "1-name"})
            if isinstance(result, NoneType):
                self.logger.error(
                    f"Can't auto refresh cookies for account {self.mid}.Pleases login again.")
                return
            refresh_csrf = result.text
            resp=self.session.post("https://passport.bilibili.com/x/passport-login/web/cookie/refresh", {"csrf": self.session.cookies.get(
                "bili_jct"), "refresh_csrf": refresh_csrf, "source": "main_web", "refresh_token": self.refresh_token})
            if resp.json()['code']!=0:
                self.logger.error(f"Error during refreshing cookies. Code={resp.json()['code']}. Response={resp.text}, Request={resp.request}")
                return
            else:
                self.logger.success(f"Account {self.mid} cookies refreshed.")
                old_token=self.refresh_token
                self.refresh_token=resp.json()['data']['refresh_token']
            
            #comfirm update
            resp=self.session.post(
                "https://passport.bilibili.com/x/passport-login/web/confirm/refresh", {"csrf": self.session.cookies.get("bili_jct"), "refresh_token": old_token})
            if resp.json()['code']!=0:
                self.logger.error(f"Error during confirming refresh. Code={resp.json()['code']}. Response={resp.text}, Request={resp.request}")
                return

            self.logger.success(f"Account {self.mid} cookies refresh:comfired.")
            self.save_cookies()
        else:
            self.logger.info("No need to refresh cookies.")
            self.logger.info(need_refresh)


class ByQRCode(BaseLogin):
    def __init__(self):
        super().__init__()
        self.status = 0

    @classmethod
    def generate_command(action: str = 'stop'):
        return {
            'action': action
        }

    def __call__(self, statusQueue: queue.LifoQueue, commandQueue: queue.LifoQueue, task: utils.Task, user: User) -> bool:
        # pdb.set_trace()
        self.logger.info("Sign up by QR Code")
        n = 0
        n += 1
        self.logger.info(n)
        qrdic = self.get_qr_code()
        self.qrcode_key = qrdic['data']['qrcode_key']
        utils.QRShower(
            qrdic["data"]["url"], self.logger).show()
        status = -2
        command = None
        while True:
            if commandQueue.qsize() > 0:
                command = pickle.loads(commandQueue.get())
            if command != None:
                if command['action'] == 'stop':
                    self.logger.warn("Stop login(QR) because of command")
                    command = None
                    break
            has_scaned = self.check_has_scaned()
            ostatus = status
            # self.logger.info(has_scaned)
            if has_scaned['data']['code'] == 86038:
                status = -1
                self.logger.error("QR Code expired.")
                global_vars.tasks.pop(task.uuid)
                return 0
            elif has_scaned['data']['code'] == 86090:
                status = 0
            elif has_scaned['data']['code'] == 0:
                self.logger.success("Login success")
                status = 1
                self.status = 1
                user.logined = 2
                user.updateMID(self.checkUser()['data']['mid'])
                user.refresh_token = has_scaned['data']['refresh_token']
                user.save_cookies()
                user.last_cookies_update = time.time()
                if user.set_to_default:
                    global_vars.default_user = user.mid
                global_vars.tasks.pop(task.uuid)
                return
            if ostatus != status:
                statusQueue.put(pickle.dumps(status))
                switcher = {
                    0: "QR Code has been scanned",
                    1: "Login success",
                    -2: "Waiting for scan"
                }
                self.logger.info(switcher.get(status))
            time.sleep(0.75)

    def get_qr_code(self):
        '''
        Get QR Code for Bilibili Login
        https://github.com/SocialSisterYi/bilibili-API-collect/blob/master/docs/login/login_action/QR.md
        '''
        resp = self.session.get(
            "https://passport.bilibili.com/x/passport-login/web/qrcode/generate")
        self.logger.info("QR Code get: "+(resp.text))
        return resp.json()

    def check_has_scaned(self):
        resp = self.session.get(
            "https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key="+self.qrcode_key).json()
        return resp


def load_users():
    if not os.path.exists("./data/user_cache"):
        return
    for i in os.listdir("./data/user_cache"):
        ipath = f"./data/user_cache/{i}"
        new_user = User()
        global_vars.users[-1].append(new_user)
        with open(ipath, "r", encoding="utf-8") as f:
            j = json.loads(f.read())
            new_user.session.cookies.update(j['cookies'])
            new_user.check_user()
            new_user.last_cookies_update = j['last_cookies_update']
            new_user.refresh_token = j['refresh_token']
            new_user.logined = 2
            global_vars.users[new_user.mid] = new_user
            if new_user.set_to_default:
                global_vars.default_user = new_user.mid

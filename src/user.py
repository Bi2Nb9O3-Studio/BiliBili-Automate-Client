from ctypes import util
import logging
import pickle
import queue
import time
from tkinter import N
from tracemalloc import stop
import requests

import cli
import global_vars
import utils


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
    def __init__(self, mid: int | None = -1) -> None:
        self.mid = mid
        self.name = ''
        self.session = utils.getNewSession()
        self.logined = 0
        self.logger = cli.setup_logger("User")

    def login(self, auth: BaseLogin):
        auth.build(self.session)
        task = utils.Task('UserLogin', auth, kwargs={'user': self})
        taskuuid = task.uuid
        global_vars.tasks[taskuuid] = task
        global_vars.tasks[taskuuid].start()
        self.logined = 1

    def updateMID(self, mid: int):
        if self.mid == -1:
            self.mid = mid
            global_vars.users[mid] = self
            global_vars.users[-1].remove(self)
            self.logger.info(f"New User MID set to {mid}")
        elif mid != self.mid:
            self.mid = mid
            self.logger.info(f"User MID updated to {mid}")

        else:
            self.logger.info(f"User MID is {mid}")

    def checkUser(self):
        # https: // api.bilibili.com/x/web-interface/nav
        resp = self.session.get(
            "https://api.bilibili.com/x/web-interface/nav").json()
        self.mid = resp['data']['mid']
        self.name = resp['data']['uname']
        return resp

    def __str__(self) -> str:
        if self.logined == 2:
            self.checkUser()
            return f"User {self.name}({self.mid})"
        elif self.logined == 1:
            return f"User {self.mid} (Logining)"

        return f"User {self.mid}(Not Logined or New)"


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
        self.logger.info("Sign up by QR Code")
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
                global_vars.tasks.pop(task.uuid)
                user.updateMID(self.checkUser()['data']['mid'])
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

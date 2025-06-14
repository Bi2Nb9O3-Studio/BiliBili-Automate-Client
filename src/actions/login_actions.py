from logging import Logger
from queue import LifoQueue

from user import User
from .action import BaseAction


class QRCodeLinkGetAction(BaseAction):
    def __init__(self):
        super().__init__()
        self.name = "Get by QR Code"
        self.description = "Get QR Code for login."

        self.namespace = "default"
        self.path = "login.qrcode.getcode"
        self.location = (self.namespace, self.path)
    def function(self, runtime_args: tuple[Logger, User, LifoQueue, LifoQueue], *args, **kwargs):
        logger, user, statusQueue, commandQueue = runtime_args
        resp=user.session.get(
            "https://passport.bilibili.com/x/passport-login/web/qrcode/generate")
        if resp.json()['code']!= 0:
            # logger.error(
            #     f"Error during getting QR Code. Code={resp.json()['code']}. Response={resp.text}, Request={resp.request}")
            raise RuntimeError(f"Error during getting QR Code. Code={resp.json()['code']}. Response={resp.text}, Request={resp.request}")
        logger.debug(f"QR Code generated successfully: {resp.json()}")
        statusQueue.put({
            'status': 'success',
            'message': 'QR Code generated successfully.',
            'data': resp.json()
        })
        return resp.json()
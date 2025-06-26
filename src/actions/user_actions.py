import json
from logging import Logger
from queue import LifoQueue

from user import User
from utils import ensure_file, ensure_path
from .action import BaseAction


class QRCodeLinkGetAction(BaseAction):
    name = "Get by QR Code"
    description = "Get QR Code for login."

    namespace = "default"
    path = "user.login.qrcode.get"
    location = (namespace, path)
    def function(runtime_args: tuple[Logger, User], *args, **kwargs):
        """
        生成用于登录的 B 站二维码。

        :param runtime_args: 包含日志记录器、用户对象、状态队列和命令队列的元组。
        :param args: 可变位置参数，当前未使用。
        :param kwargs: 可变关键字参数，当前未使用。
        :return: 包含二维码信息的 JSON 响应数据。
        """
        # 解包运行时参数
        logger, user = runtime_args
        # 发送 GET 请求以生成登录二维码
        resp = user.session.get(
            "https://passport.bilibili.com/x/passport-login/web/qrcode/generate")
        # 检查响应状态码是否为 0，不为 0 表示请求出错
        if resp.json()['code'] != 0:
            # 取消注释以下行可将错误信息记录到日志
            # logger.error(
            #     f"Error during getting QR Code. Code={resp.json()['code']}. Response={resp.text}, Request={resp.request}")
            # 若请求出错，抛出运行时错误
            raise RuntimeError(f"Error during getting QR Code. Code={resp.json()['code']}. Response={resp.text}, Request={resp.request}")
        # 若请求成功，记录调试信息
        logger.debug(f"QR Code generated successfully: {resp.json()}")
        # 返回包含二维码信息的 JSON 响应数据
        return resp.json()

class QRCodeCheckIfScannedAction(BaseAction):
    name = "Check QR Code"
    description = "Check if the QR Code has been scanned."

    namespace = "default"
    path = "user.login.qrcode.check"
    location = (namespace, path)
    def function(runtime_args: tuple[Logger, User], *args, **kwargs):
        """
        检查二维码是否已被扫描。

        :param runtime_args: 包含日志记录器和用户对象的元组。
        :param args: 可变位置参数，当前未使用。
        :param kwargs: 可变关键字参数，当前未使用。
        :return: 包含二维码状态的 JSON 响应数据。
        """
        logger, user = runtime_args
        qrcode_key = kwargs.get("qrcode_key")
        if not qrcode_key:
            raise ValueError("qrcode_key is required to check QR Code status.")
        resp = user.session.get(
            "https://passport.bilibili.com/x/passport-login/web/qrcode/poll?qrcode_key=" + qrcode_key)
        if resp.json()['code'] != 0:
            raise RuntimeError(f"Error during checking QR Code. Code={resp.json()['code']}. Response={resp.text}, Request={resp.request}")
        logger.debug(f"QR Code checked successfully: {resp.json()}")
        return resp.json()

class SaveCookiesAction(BaseAction):
    name = "Save Cookies"
    description = "Save cookies to the user cache."

    namespace = "default"
    path = "user.cookies.save"
    location = (namespace, path)
    def function(runtime_args: tuple[Logger, User], *args, **kwargs):
        """
        保存用户的 cookies 到缓存。

        :param runtime_args: 包含日志记录器和用户对象的元组。
        :param args: 可变位置参数，当前未使用。
        :param kwargs: 可变关键字参数，当前未使用。
        """
        logger, user = runtime_args
        path=ensure_path("./users")
        file=ensure_file(path + f"/{user.mid}.json")
        content = {
            "cookies": user.session.cookies.get_dict(),
            "refresh_token": user.refresh_token,
            "last_cookies_update": user.last_cookies_update
        }
        json.dump(content, open(file, "w", encoding="utf-8"))
        
        logger.info(f"Cookies for user {user.mid} saved successfully.")
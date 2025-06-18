from logging import Logger
from queue import LifoQueue

from user import User
from .action import BaseAction


class QRCodeLinkGetAction(BaseAction):
    # super().__init__()
    name = "Get by QR Code"
    description = "Get QR Code for login."

    namespace = "default"
    path = "login.qrcode.getcode"
    location = (namespace, path)
    def function(self, runtime_args: tuple[Logger, User, LifoQueue, LifoQueue], *args, **kwargs):
        """
        生成用于登录的 B 站二维码。

        :param runtime_args: 包含日志记录器、用户对象、状态队列和命令队列的元组。
        :param args: 可变位置参数，当前未使用。
        :param kwargs: 可变关键字参数，当前未使用。
        :return: 包含二维码信息的 JSON 响应数据。
        """
        # 解包运行时参数
        logger, user, statusQueue, commandQueue = runtime_args
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
        # 将成功状态信息放入状态队列
        statusQueue.put({
            'status': 'success',
            'message': 'QR Code generated successfully.',
            'data': resp.json()
        })
        # 返回包含二维码信息的 JSON 响应数据
        return resp.json()
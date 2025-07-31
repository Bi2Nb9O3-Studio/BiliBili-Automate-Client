from logging import Logger
import os
import pickle
from queue import Queue
import time
from typing import Dict, Tuple
import actions
import jobs
import jobs.job
from user import User,users
import user
from utils import ensure_path


@jobs.job_register.register("default","user.login.qrcode",{
    "stop": {"action":"stop"}
})
def user_login_qrcode(queues: Dict[str, Queue], runtime_args: Tuple[Logger, User]):
    """
    生成用于登录的 B 站二维码。

    :param runtime_args: 包含日志记录器、用户对象、状态队列和命令队列的元组。
    :param args: 可变位置参数，当前未使用。
    :param kwargs: 可变关键字参数，当前未使用。
    :return: 包含二维码信息的 JSON 响应数据。
    """
    logger, user = runtime_args

    logger.info("Starting QR Code login process.")
    qrdata=actions.actions_register.get_action("default", "user.login.qrcode.get").function(runtime_args=runtime_args)
    if qrdata['code'] != 0:
            logger.error(f"Error during getting QR Code. Code={qrdata['code']}. Response={qrdata['message']}")
            queues['statusQueue'].put({
                "code": -1,
                "message": f"Error during getting QR Code. Code={qrdata['code']}. Response={qrdata['message']}"
            })
            return -1
    qrkey= qrdata['data']['qrcode_key']
    actions.actions_register.get_action("default", "user.login.qrcode.generate_code").function(
        runtime_args=runtime_args, url=qrdata["data"]["url"])
    queues['statusQueue'].put({
        "code": 0,
        "message": "Starting waiting for QR Code scan.",
        "data": qrdata
    })
    while True:
        if queues['commandQueue'].qsize() > 0:
            command = queues['commandQueue'].get()
            if command['action'] == 'stop':
                logger.warning("Stopping QR Code login due to command.")
                return
        has_scanned = actions.actions_register.get_action("default", "user.login.qrcode.check").function(
            runtime_args=runtime_args, qrcode_key=qrkey)
        if has_scanned['data']['code'] == 86038:
            logger.error("QR Code expired.")
            queues['statusQueue'].put({
                "code": -1,
                "message": "QR Code expired."
            })
            return -1
        elif has_scanned['data']['code'] == 86090:
            logger.debug("QR Code not scanned yet.")
        elif has_scanned['data']['code'] == 0:
            logger.success("Login success")
            user.logined = 2
            actions.actions_register.get_action("default", "user.info.update").function(
                runtime_args=runtime_args)
            user.refresh_token = has_scanned['data']['refresh_token']
            actions.actions_register.get_action("default", "user.cookies.save").function(
                runtime_args=runtime_args)
            user.last_cookies_update = time.time()
            queues['statusQueue'].put({
                "code": 1,
                "message": "Login success",
                "data": {
                    "mid": user.mid,
                    "uname": user.name
                }
            })
            users[user.mid] = user
            return


@jobs.job_register.register("default", "user.load", {
    "stop": {"action": "stop"}
})
def user_load(queues: Dict[str, Queue], runtime_args: Tuple[Logger, User]):
    userpath=ensure_path("./users")
    for i in os.listdir(userpath):
        if os.path.isfile(os.path.join(userpath,i)) and i.endswith(".json"):
            newuser=user.User(int(i.split(".")[0]))
            actions.actions_register.get_action("default","user.load").function(runtime_args=(runtime_args[0],newuser))
            users[newuser.mid] = newuser
            actions.actions_register.get_action("default", "user.info.update").function(runtime_args=(runtime_args[0], newuser))

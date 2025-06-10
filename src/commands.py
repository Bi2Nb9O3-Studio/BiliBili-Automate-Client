
import time
from typing import Any, Tuple

import cli
import global_vars
import user


class Command():
    '''
    :param name: The name of the command
    :param description: The description of the command
    :param function: The function that the command will run
    :param require_args: Whether the command requires arguments
    '''

    def __init__(self, name: str, function: callable, require_args: bool = False, description: str = 'No description.') -> None:
        self.name = name
        self.description = description
        self.function = function
        self.require_args = require_args
        self.logger = cli.setup_logger("Command")

    def __call__(self, *args, **kwargs):
        kwargs['logger'] = self.logger
        self.function(*args, **kwargs)

    def __str__(self) -> str:
        return f"Command: {self.name}\nDescription: {self.description}"

    def needArgs(self):
        return self.require_args


class ErrorCommand(Command):
    def __init__(self, name: str, description: str, error_msg: str = "Invalid Command") -> None:
        super().__init__(name, self.error, require_args=False, description=description)
        self.error_msg = error_msg

    def error(self, logger, buff):
        logger.error(self.error_msg)


def list_users(logger, buff):
    logger.info("User list:")
    if global_vars.users.__len__() == 1:
        logger.info("No users.")
        return False
    for k in global_vars.users:
        if k == -1:
            continue
        logger.info(global_vars.users[k])
    return False


def exit(logger, buff):
    logger.info("Client closed")
    time.sleep(0.5)
    global_vars.app.exit()


def login_by_qr(logger, buff):
    new_user = user.User(-1, True)
    new_user.login(user.ByQRCode())
    global_vars.users[-1].append(new_user)


commands = ...


def decode_requirements(requirements: list) -> Tuple[list, dict]:
    args = []
    kwargs = {}
    for req in requirements:
        if req.startswith("-arg:"):
            req.strip("-arg:")
            args.append(req)
        elif req.startswith("-kwarg:"):
            req.strip("-kwarg:")
            key, value = req.split("=", 1)
            kwargs[key] = value
    return args, kwargs

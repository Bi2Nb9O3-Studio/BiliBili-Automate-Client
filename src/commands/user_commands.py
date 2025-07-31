import logging

from commands.command import BaseCommand
import task
import user


class UserCommands(BaseCommand):
    name: str = "User Commands"
    description: str = "Commands related to user actions such as login, logout, and session management."
    aliases: list[str] = ["usr"]
    hidden: bool = False
    command: str = "user"
    
    completion = {
        "login": {
            "qrcode": None
        }
    }
    def handler(command_line: str, logger: logging.Logger):
        cmds=command_line.split(" ")[1:]
        if not cmds:
            logger.error("No command provided. Use 'user help' to see available commands.")
            return
        match cmds[0]:
            case "login":
                if len(cmds) < 2:
                    task.task_executor.execute(
                        "default", "user.login.qrcode", "UserLoginQRCode", user.User())
                    return
                match cmds[1]:
                    case "qrcode":
                        task.task_executor.execute(
                            "default", "user.login.qrcode", logger, user.User())
            case "help":
                logger.info("Available user commands: login, logout, info, help")
import logging
import os
import sys
import time
import prompt_toolkit
import prompt_toolkit.key_binding
import prompt_toolkit.widgets

import actions
import cli
import commands
import log
import task
from utils import ensure_path
from jobs import *


class Client:
    def __init__(self):
        self.areas = {}
        self.logFile = f"./logs/{time.strftime('%Y-%m-%d_%H-%M-%S')}.log"
        self.generate_layout()
        self.logger = self.setup_logger("Main")
        commands.commands_register.logger = self.setup_logger("Command")
        self.logger.debug("Registered actions: %s", str(actions.actions_register.actions))
        
        def help(_, logger):
            """List all registered commands.

            Args:
                _ (str): Command line input, not used in this function.
                logger (logging.Logger): Logger instance for logging.
            """
            logger.info(commands.commands_register.list_commands())
        commands.commands_register.simple_register(
            help, "help", "List Commands", "List all registered commands.",["?", "h"], hidden=False
        )

        commands.commands_register.logger_generator = self.setup_logger
        task.task_executor.logger = self.setup_logger("TaskExecutor")
        task.task_executor.logger_generator = self.setup_logger

        task.task_executor.execute(
            "default", "cli.update.sidebar", self.setup_logger("SidebarUpdate"), None,areas=self.areas)
        task.task_executor.execute(
            "default", "user.load", self.setup_logger("UserLoad"), None)
        self.logger.info("BiBiClient started.")

    def generate_layout(self):
        self.logArea = cli.LoggingArea()
        self.areas['log'] = self.logArea.getArea()
        self.areas['input'] = prompt_toolkit.widgets.TextArea(
            height=prompt_toolkit.layout.Dimension(weight=3),
            prompt=">>> ",
            focus_on_click=True,
            multiline=False
        )
        self.areas['livelist'] = prompt_toolkit.widgets.TextArea(
            height=prompt_toolkit.layout.Dimension(weight=1),
            focus_on_click=True,
            read_only=True
        )
        self.areas['userlist'] = prompt_toolkit.widgets.TextArea(
            height=prompt_toolkit.layout.Dimension(weight=1),
            focus_on_click=True,
            read_only=True
        )
        self.areas['tasklist'] = prompt_toolkit.widgets.TextArea(
            height=prompt_toolkit.layout.Dimension(weight=1),
            focus_on_click=True,
            read_only=True
        )
        self.layout = prompt_toolkit.layout.Layout(
            prompt_toolkit.layout.containers.HSplit([
                prompt_toolkit.layout.containers.Window(
                    height=1, char=" BiBiClient By Bi2Nb9O3  "),
                prompt_toolkit.layout.containers.VSplit([
                    prompt_toolkit.layout.containers.HSplit([
                        self.areas['log'],
                        self.areas['input'],
                    ], width=prompt_toolkit.layout.Dimension(weight=7)),
                    prompt_toolkit.layout.containers.HSplit([
                        self.areas['livelist'],
                        self.areas['userlist'],
                        self.areas['tasklist']
                    ], width=prompt_toolkit.layout.Dimension(weight=3))
                ])
            ])
        )
        self.areas['input'].accept_handler=commands.commands_register.handle_command_line
        self.app = prompt_toolkit.Application(
            layout=self.layout, full_screen=True, mouse_support=True)
        kb = prompt_toolkit.key_binding.KeyBindings()

        @kb.add("c-q")
        def _close(_):
            self.stop()
        self.app.key_bindings = kb
        
        def exit_command(_, logger):
            """Exit the BiBiClient application.

            Args:
                _ (str): Command line input, not used in this function.
                logger (logging.Logger): Logger instance for logging.
            """
            logger.info("Exiting BiBiClient application.")
            self.stop()
        commands.commands_register.simple_register(
            exit_command, "exit", "Exit Client", "Exit the BiBiClient application.",["quit", "q","esc","bye"],hidden=False
        )
        
    def setup_logger(self,name) -> logging.Logger:
        if logging.Logger.manager.loggerDict.get(name):
            return logging.getLogger(name)
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        os.makedirs('./logs/', exist_ok=True)
        fileHandler = logging.FileHandler(self.logFile, encoding="utf-8")
        streamHandler = log.LoggingHandler(self.logArea)
        formatter = logging.Formatter(
            '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
        fileHandler.setFormatter(formatter)
        streamHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)
        logger.addHandler(streamHandler)
        return logger
    def stop(self):
        task.task_executor.stop_all_and_block()
        self.app.exit()
        sys.exit(0)

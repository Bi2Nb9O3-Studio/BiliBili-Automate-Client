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
from utils import ensure_path


class Client:
    def __init__(self):
        self.areas = {}
        self.generate_layout()
        ensure_path("./logs/")
        self.logFile = f"./logs/{time.strftime('%Y-%m-%d_%H-%M-%S')}.log"
        self.logger = self.setup_logger("Main")
        self.logger.info(str(actions.actions_register.actions))
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
            self.app.exit()
        self.app.key_bindings = kb
        
        def stop(_):
            """
            Stop the client application.
            """
            self.stop()
        
        commands.commands_register.simple_register(
            stop, "exit", "Exit Client", "Exit the BiBiClient application."
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
        self.app.exit()
        sys.exit(0)



from ast import Dict

import prompt_toolkit
import prompt_toolkit.buffer
import prompt_toolkit.key_binding
import prompt_toolkit.layout
import prompt_toolkit.widgets
import cli


class Client:
    def __init__(self) -> None:

        # CLI
        self.areas = {}
        self.logArea = cli.LoggingArea()
        self.areas['log'] = self.logArea.getArea()
        self.logger = cli.setup_logger("Client", "./logs/", self.logArea)
        self.areas['input'] = prompt_toolkit.widgets.TextArea(
            height=prompt_toolkit.layout.Dimension(weight=3),
            prompt=">>> ",
            focus_on_click=True,
            multiline=False
        )

        def accept(buff: prompt_toolkit.buffer.Buffer):
            if buff.text.strip() == "":
                return True
            self.logArea.logText(f"Input: {buff.text}")
            return False
        self.areas['input'].accept_handler = accept
        self.layout = prompt_toolkit.layout.Layout(prompt_toolkit.layout.containers.HSplit([
            prompt_toolkit.layout.containers.Window(
                height=1, char=" BiBiClient  ", style="class:line"),
            self.areas['log'],
            self.areas['input']
        ]))
        self.app = prompt_toolkit.Application(
            layout=self.layout, full_screen=True, mouse_support=True)
        kb = prompt_toolkit.key_binding.KeyBindings()

        @kb.add("s-escape")
        def _close():
            self.app.exit()
            self.logger.info("Client closed")
        self.app.key_bindings = kb
        self.logger.info("Client initialized")

        self.tasks = []

    def run(self, async_run=False):
        if async_run:
            return self.app.run_async()
        self.app.run()

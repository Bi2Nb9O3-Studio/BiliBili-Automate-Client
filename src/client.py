import time
import prompt_toolkit
import prompt_toolkit.buffer
import prompt_toolkit.key_binding
import prompt_toolkit.layout
import prompt_toolkit.widgets
import cli
import global_vars
import user
import utils


class Client:
    def __init__(self) -> None:

        # CLI
        self.areas = {}
        global_vars.logFile = f"./logs/{int(time.time())}.log"
        global_vars.logArea = cli.LoggingArea()
        global_vars.areas['log'] = global_vars.logArea.getArea()
        self.logger = cli.setup_logger("Client")
        self.commandLogger = cli.setup_logger("CommandHandler")
        global_vars.areas['input'] = prompt_toolkit.widgets.TextArea(
            height=prompt_toolkit.layout.Dimension(weight=3),
            prompt=">>> ",
            focus_on_click=True,
            multiline=False
        )
        global_vars.areas['tabList'] = prompt_toolkit.widgets.TextArea(
            height=prompt_toolkit.layout.Dimension(weight=7),
            focus_on_click=True,
            read_only=True
        )

        def accept(buff: prompt_toolkit.buffer.Buffer):
            if buff.text.strip() == "":
                return True
            commands = buff.text.split(' ')
            self.commandLogger.info(f"User Input: {buff.text}")
            if commands[0] == 'user':
                if commands.__len__() == 1:
                    self.commandLogger.info("User list:")
                    if global_vars.users.__len__() == 1:
                        self.commandLogger.info("No users.")
                        return False
                    for k in global_vars.users:
                        if k == -1:
                            continue
                        self.commandLogger.info(global_vars.users[k])
                    return False
                if commands[1] == 'login':
                    if commands.__len__() == 2:
                        self.commandLogger.error(
                            "Please specify the login method.")
                        return False
                    if commands[2] == 'qr':
                        new_user = user.User(-1)
                        new_user.login(user.ByQRCode())
                        global_vars.users[-1].append(new_user)
                        return False
            elif commands[0] == 'execute':
                exec(buff.text[8:])
            elif commands[0] == 'exit':
                self.logger.info("Client closed")
                time.sleep(0.5)
                global_vars.app.exit()
                return False
            return False
        global_vars.areas['input'].accept_handler = accept
        global_vars.layout = prompt_toolkit.layout.Layout(
            prompt_toolkit.layout.containers.HSplit([
                prompt_toolkit.layout.containers.Window(
                    height=1, char=" BiBiClient By Bi2Nb9O3  "),
                prompt_toolkit.layout.containers.VSplit([
                    prompt_toolkit.layout.containers.HSplit([
                        global_vars.areas['log'],
                        global_vars.areas['input'],
                    ], width=prompt_toolkit.layout.Dimension(weight=7)),
                    prompt_toolkit.layout.containers.HSplit([
                        global_vars.areas['tabList']
                    ], width=prompt_toolkit.layout.Dimension(weight=3))
                ])
            ])

        )
        global_vars.app = prompt_toolkit.Application(
            layout=global_vars.layout, full_screen=True, mouse_support=True)
        kb = prompt_toolkit.key_binding.KeyBindings()

        @kb.add("c-q")
        def _close(_):
            self.logger.info("Client closed")
            time.sleep(0.5)
            global_vars.app.exit()
        global_vars.app.key_bindings = kb
        self.logger.info("Client initialized")
        self.logger.info("Press Ctrl+Q to close the client.")

    def run(self):
        global_vars.app.run()

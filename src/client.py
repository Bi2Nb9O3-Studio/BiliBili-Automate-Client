import time
import prompt_toolkit
import prompt_toolkit.buffer
import prompt_toolkit.key_binding
import prompt_toolkit.layout
import prompt_toolkit.widgets
import cli
import commands
import global_vars
from live import LiveRoom
import user


class Client:
    def __init__(self) -> None:

        # CLI
        self.areas = {}
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
        global_vars.areas['livelist'] = prompt_toolkit.widgets.TextArea(
            height=prompt_toolkit.layout.Dimension(weight=1),
            focus_on_click=True,
            read_only=True
        )
        global_vars.areas['userlist'] = prompt_toolkit.widgets.TextArea(
            height=prompt_toolkit.layout.Dimension(weight=1),
            focus_on_click=True,
            read_only=True
        )
        global_vars.areas['tasklist'] = prompt_toolkit.widgets.TextArea(
            height=prompt_toolkit.layout.Dimension(weight=1),
            focus_on_click=True,
            read_only=True
        )
        commands.commands = {
            "user": {
                0: commands.Command("List Users", commands.list_users, description="List all users.", require_args=False),
                "login": {
                    0: commands.ErrorCommand("Login Error", "Please specify the login method.", "Please specify the login method."),
                    "qr": commands.Command("Login with QR", commands.login_by_qr, description="Login with QR code.", require_args=False),
                }
            },
            'exit': commands.Command("Exit", commands.exit, description="Exit the client.", require_args=False)
        }

        def accept(buff: prompt_toolkit.buffer.Buffer):
            if buff.text.strip() == "":
                return True
            cmd = buff.text.split(' ')
            self.commandLogger.info(f"User Input: {buff.text}")
            if buff.text.startswith("execute"):
                exec(buff.text[8:])
            elif cmd[0] == 'test':
                global_vars.test = LiveRoom(
                    global_vars.users[global_vars.default_user], 30210595)

            elif cmd[0] == 'test1':
                global_vars.test.record_task_obj.setCommand({
                    'action': 'stop_record'
                })
            elif cmd[0] == 'test2':
                global_vars.test.start_record()
            elif cmd[0] == 'test3':
                global_vars.users[global_vars.default_user].refresh_cookies()
            else:
                pos = 0
                prev = commands.commands
                for word in cmd:
                    cur = prev.get(word, -1)
                    if cur == -1:
                        self.commandLogger.error(
                            f"Invalid Command: {' '.join(cmd[:pos+1])} <- HERE {'...' if pos!=len(cmd)-1 else ''}")
                        break
                    elif isinstance(cur, dict):
                        prev = cur
                        if pos == len(cmd)-1:
                            cur = cur.get(0, -1)
                            if cur == -1:
                                self.commandLogger.error(
                                    f"Invalid Command: {' '.join(cmd[:pos+1])} <== HERE {'...' if pos!=len(cmd)-1 else ''}")
                                break
                            else:
                                cur(buff=buff)
                    else:
                        if cur.needArgs() and pos+2 < len(cmd):
                            if cmd[pos+1] == '-r' or cmd[pos+1] == '--requirements':
                                args, kwargs = commands.decode_requirements(
                                    cmd[pos+2:])
                                cur(buff=buff, **args, **kwargs)
                        else:
                            cur(buff=buff)
                        break
                    pos += 1
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
                        global_vars.areas['livelist'],
                        global_vars.areas['userlist'],
                        global_vars.areas['tasklist']
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
        user.load_users()

    def run(self):
        global_vars.app.run()

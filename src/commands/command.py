import logging
import colorama
import prompt_toolkit
import prompt_toolkit.buffer


class BaseCommand:
    name: str
    description: str
    aliases: list[str] = []
    hidden: bool = False
    command: str = ""

    def __init__(self):
        ...

    def handler(command_line: str, logger: logging.Logger):
        raise NotImplementedError(
            "Command handler must be implemented in subclasses.")


class CommandRegister:
    def __init__(self):
        self.commands = {}
        self.logger:logging.Logger
    def register(self, command: BaseCommand):
        if command.command in self.commands:
            raise ValueError(
                f"Command {command.name} already registered with command line {command.command}")
        self.commands[command.command] = command

    def handle_command_line(self, buff: prompt_toolkit.buffer.Buffer):
        command_line = buff.text.strip()
        self.logger.info(f"User Command Input: {command_line}")
        # command_line = command_line[1:] # Get the first word as command
        for command, command_obj in self.commands.items():
            if command_line.startswith(command):
                if isinstance(command_obj, dict):
                    command_obj['handler'](command_line, self.logger)
                    return
                else:
                    command_obj.handler(command_line, self.logger)
                    return
        self.logger.error(f"Command '{command_line}' not found.")

    def __iter__(self):
        return iter(self.commands.values())

    def simple_register(self, handler, command, name, description="", aliases=[], hidden=False):
        """
        A simple way to register a command with a function.
        """
        self.commands[command] = {
            'handler': handler,
            'command': command,
            'name': name,
            'description': description,
            'aliases': aliases,
            'hidden': hidden
        }
        for alias in aliases:
            self.simple_register(
                handler, alias, name, "Alias for " + command, aliases=[], hidden=True)

    def list_commands(self):
        """
        List all registered commands.
        """
        s = "Commands:\n\n"

        for command, command_obj in self.commands.items():
            if isinstance(command_obj, dict):
                if command_obj['hidden']:
                    continue
                s += f"{' '.join([command_obj['command']]+command_obj['aliases'])} - {command_obj['name']}: {command_obj['description']}\n"
            else:
                if hasattr(command_obj, 'hidden') and command_obj.hidden:
                    continue
                s += f"{' '.join([command_obj.command]+command_obj.aliases)} - {command_obj.name}: {command_obj.description}\n"

        return s

import prompt_toolkit
import prompt_toolkit.buffer


class BaseCommand:
    def __init__(self):
        self.name: str
        self.description: str
        
        self.command: str = ""
    
    def handler(self, command_line:str):
        raise NotImplementedError("Command handler must be implemented in subclasses.")


class CommandRegister:
    def __init__(self):
        self.commands = {}

    def register(self, command: BaseCommand):
        if command.command in self.commands:
            raise ValueError(f"Command {command.name} already registered with command line {command.command}")
        self.commands[command.command] = command

    def handle_command_line(self, buff: prompt_toolkit.buffer.Buffer):
        command_line = buff.text.strip()
        # command_line = command_line[1:] # Get the first word as command
        for command, command_obj in self.commands.items():
            if command_line.startswith(command):
                if isinstance(command_obj,dict):
                    command_obj['handler'](command_line)
                else:
                    command_obj.handler(command_line)
    def __iter__(self):
        return iter(self.commands.values())
    
    def simple_register(self, handler, command, name, description=""):
        """
        A simple way to register a command with a function.
        """
        self.commands[command] = {
            'handler': handler,
            'command': command,
            'name': name,
            'description': description
        }
        
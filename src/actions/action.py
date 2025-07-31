from logging import Logger

from user import User


class BaseAction:
    name: str
    description: str
    namespace: str = ""
    path: str = ""
    location: tuple[str, str] = (namespace, path)
    def function(runtime_args:tuple[Logger,User], *args, **kwargs):
        raise NotImplementedError("Action function must be implemented in subclasses.")


class ActionRegister:
    def __init__(self):
        self.actions = {}

    def register(self, action: BaseAction):
        self.actions[action.location[0]] = self.actions.get(action.location[0], {})
        if action.location[1] in self.actions[action.location[0]]:
            raise ValueError(f"Action {action.name} already registered at {action.location}")
        self.actions[action.location[0]][action.location[1]] = action

    def get_action(self, namespace:str, path) -> BaseAction:
        return self.actions.get(namespace, {}).get(path, None)

    def __iter__(self):
        return iter(self.actions.values())

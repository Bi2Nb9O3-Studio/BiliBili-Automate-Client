import logging

import prompt_toolkit.completion
from commands.command import BaseCommand
import jobs
import task
import user

class AutoCompletionFromDynamicSource(prompt_toolkit.completion.Completer):
    def __init__(self, source):
        self.source = source

    def get_completions(self, document, complete_event):
        if callable(self.source):
            items = self.source()
        else:
            items = self.source
        for item in items:
            yield prompt_toolkit.completion.Completion(str(item), start_position=-len(document.text))

class TaskCommand(BaseCommand):
    name: str = "Task Commands"
    description: str = "Commands related to task actions such as start, stop, and status."
    aliases: list[str] = ["tsk"]
    hidden: bool = False
    command: str = "task"
    completion = {
        "start" : AutoCompletionFromDynamicSource(jobs.job_register.get_as_completion),
        "kill" : AutoCompletionFromDynamicSource(task.task_executor.get_tasks_as_set)
    }

    def handler(command_line: str, logger: logging.Logger):
        cmds = command_line.split(" ")[1:]
        if not cmds:
            logger.error(
                "No command provided. Use 'task help' to see available commands.")
            return
        match cmds[0]:
            case "start":
                if len(cmds) < 2:
                    logger.error("No job specified to start.")
                    return
                if len(cmds) < 3:
                    logger.error("No name specified for the task.")
                    return
                if len(cmds) < 4:
                    logger.error("No user specified for the task.")
                    return
                user_mid= cmds[3]
                user_obj = user.users.get(int(user_mid),None)
                task_name = cmds[2]
                job_name = cmds[1]
                task.task_executor.execute(
                    job_name.split(":")[0],job_name.split(":")[1], task_name, user_obj)
            case "kill":
                if len(cmds) < 2:
                    logger.error("No task specified to kill.")
                    return
                bypass="--bypass" in cmds
                task_uuid = cmds[1]
                if task_uuid in task.task_executor.tasks:
                    logger.info(f"Task {task_uuid} has been sent to stop.")
                    task.task_executor.tasks[task_uuid].stop(bypass=bypass)
                else:
                    logger.error(f"Task {task_uuid} not found.")
            case "help":
                logger.info(
                    "Available task commands: start kill help")

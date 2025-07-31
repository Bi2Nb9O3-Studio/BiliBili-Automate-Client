from logging import Logger
import pickle
from queue import Queue
import time
from typing import Dict, Tuple

import prompt_toolkit

import jobs
from prompt_toolkit.widgets import TextArea
import task
from user import User
import user


@jobs.job_register.register("default", "cli.update.sidebar", {"stop": {"action": "stop"}})
def cli_update_sidebar(areas: Dict[str,TextArea],queues: Dict[str,Queue],runtime_args:Tuple[Logger,User]):
    _ , _ = runtime_args
    queues['statusQueue'].put("started")
    while True:
        areas['userlist'].buffer.read_only = prompt_toolkit.filters.to_filter(
            False)
        # areas['userlist'].buffer.clear()
        areas['userlist'].buffer.text="Users:\n"+"\n".join([str(i) for i in user.users.values()])
        areas['userlist'].buffer.read_only = prompt_toolkit.filters.to_filter(
            True)
        
        areas['tasklist'].buffer.read_only = prompt_toolkit.filters.to_filter(
            False)
        # areas['tasklist'].buffer.clear()
        areas['tasklist'].buffer.text="Tasks:\n"+"\n".join([str(i)+":"+i.job_name for i in task.task_executor.tasks.values()])
        areas['tasklist'].buffer.read_only = prompt_toolkit.filters.to_filter(
            True)
        
        for t in list(task.task_executor.tasks.values()).copy():
            if not t.threading.is_alive():
                task.task_executor.tasks.pop(t.uuid)
                task.task_executor.tasks_set.discard(t.uuid)
        
        if queues['commandQueue'].qsize() > 0:
            command = queues['commandQueue'].get()
            if command['action'] == 'stop':
                print("stop")
                return
            print(f"Command received: {command}")
        time.sleep(0.2)

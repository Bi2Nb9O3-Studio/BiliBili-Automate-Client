from logging import Logger
import pickle
import queue
import threading
from typing import Dict
from uuid import uuid4

class TaskCommand:
    def __init__(self, name: str, payload: Dict = None):
        self.name = name
        self.payload = payload or {}

class Task:
    def __init__(self,uuid,job_obj,logger,user, args, kwargs={}):
        self.uuid=uuid
        self.statusQueue = queue.LifoQueue(5)
        self.commandQueue = queue.LifoQueue(5)
        self.logger = logger
        self.user = user

        self.job_name = job_obj['func'].__name__
        self.job=job_obj['func']
        self.job_commands= job_obj['commands']

        self.args = args
        self.kwargs = kwargs
        self.threading = None  # Placeholder for threading.Thread object
    def run(self,):
        if self.threading is not None and self.threading.is_alive():
            raise RuntimeError("Task is already running.")
        kwargs= self.kwargs.copy()
        kwargs['queues']= {
            'statusQueue': self.statusQueue,
            'commandQueue': self.commandQueue
        }
        kwargs['runtime_args'] = (self.logger, self.user)
        self.threading = threading.Thread(
            target=self.job,
            args=self.args,
            kwargs=kwargs,
            name=self.job_name
        )
        self.threading.start()
        self.logger.info(f"Task({self.uuid}) {self.threading.name}({self.threading.ident}) started.")
    
    def send(self, command):
        self.commandQueue.put(pickle.dumps(command))
        self.logger.info(f"Command {command} has been sent to task {self.uuid}.")
    
    def get_status(self):
        if self.statusQueue.empty():
            return None
        return pickle.loads(self.statusQueue.get())
    
    def stop(self):
        if self.threading is not None and self.threading.is_alive():
            comm=TaskCommand("stop") if not self.job_commands.__contains__("stop") else self.job_commands["stop"]
            self.send(comm)
            self.threading.join()
            self.logger.info(f"Task({self.uuid}) {self.threading.name}({self.threading.ident}) stopped.")
        else:
            self.logger.warning(f"Task({self.uuid}) is not running, cannot stop.")
    
class TaskExecutor:
    def __init__(self, logger:Logger) -> None:
        self.tasks = {}
        self.logger = logger

    def execute(self, job_namespace: str, job_name: str, logger, user, *args, **kwargs):
        if job_name not in self.tasks:
            raise ValueError(f"Job '{job_name}' is not registered.")
        uuid = uuid4().hex
        task = Task(uuid, self.tasks[job_namespace][job_name], logger, user, *args, **kwargs)
        self.tasks[uuid] = task
        self.logger.info(f"Task {uuid} for job {job_name} in namespace {job_namespace} created.")
        task.run()
        return uuid
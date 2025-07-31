from logging import Logger
import pickle
import queue
import threading
import traceback
from typing import Dict
from uuid import uuid4

import jobs


class TaskCommand:
    def __init__(self, name: str, payload: Dict = None):
        self.name = name
        self.payload = payload or {}


class Task:
    def __init__(self, uuid, job_obj,job_path, logger, user, args, kwargs={}):
        self.uuid = uuid
        self.statusQueue = queue.LifoQueue(5)
        self.commandQueue = queue.LifoQueue(5)
        self.logger = logger
        self.user = user

        self.job_name = job_path
        self.job = job_obj['func']
        self.job_commands: Dict[str, TaskCommand] = job_obj['commands']

        self.args = args
        self.kwargs = kwargs
        self.threading = None  # Placeholder for threading.Thread object

    def run(self,):
        if self.threading is not None and self.threading.is_alive():
            raise RuntimeError("Task is already running.")
        kwargs = self.kwargs.copy()
        kwargs['queues'] = {
            'statusQueue': self.statusQueue,
            'commandQueue': self.commandQueue
        }
        kwargs['runtime_args'] = (self.logger, self.user)

        def job():
            try:
                self.job(*self.args, **kwargs)
            except Exception as e:
                self.logger.error(f"Error in job {self.job_name}: {e}")
                self.logger.error("\n"+traceback.format_exc())
                self.statusQueue.put(pickle.dumps({
                    "code": -1,
                    "message": f"Error in job {self.job_name}: {e}"
                }))
        self.threading = threading.Thread(
            target=job,
            name=self.job_name+f"<{self.uuid[:8]}>",
        )
        self.threading.start()
        self.logger.info(
            f"{str(str(self))} {self.threading.name}({self.threading.ident}) started.")

    def send(self, command):
        self.commandQueue.put(command)
        self.logger.info(
            f"Command {command} has been sent to task {self.uuid}.")

    def get_status(self):
        if self.statusQueue.empty():
            return None
        return self.statusQueue.get()

    def stop(self):
        if self.threading is not None and self.threading.is_alive():
            comm = TaskCommand("stop") if not self.job_commands.__contains__(
                "stop") else self.job_commands["stop"]
            self.send(comm)
            self.threading.join()
            self.logger.info(
                f"Task({self.uuid}) {self.threading.name}({self.threading.ident}) stopped.")
        else:
            self.logger.warning(
                f"Task({self.uuid}) is not running, cannot stop.")
    
    def __str__(self):
        return f"Task<{self.uuid}>"


class TaskExecutor:
    def __init__(self, logger: Logger) -> None:
        self.tasks:Dict[str, Task] = {}
        self.logger = logger
        self.logger_generator = None

    def execute(self, job_namespace: str, job_name: str, logger_name, user, *args, **kwargs):
        if job_name not in jobs.job_register.jobs.get(job_namespace, {}):
            raise ValueError(f"Job '{job_name}' is not registered.")
        uuid = uuid4().hex
        logger= self.logger_generator(f"Task<{uuid[:8]}>:"+logger_name) if self.logger_generator else self.logger

        task = Task(uuid, jobs.job_register.jobs[job_namespace][job_name],job_name,
                    logger, user, args=args, kwargs=kwargs)
        self.tasks[uuid] = task
        self.logger.info(
            f"{str(task)} for {job_namespace}:{job_name} created.")
        task.run()
        return uuid
    
    def stop_all_and_block(self):
        for task in self.tasks.values():
            task.stop()
        for task in self.tasks.values():
            task.threading.join()




task_executor = TaskExecutor(None)

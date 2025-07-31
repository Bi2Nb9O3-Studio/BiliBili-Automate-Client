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
    def __init__(self, uuid, is_core_task, core_task_reason, job_obj,job_path, logger, user, args, kwargs={}):
        self.uuid = uuid
        self.statusQueue = queue.LifoQueue(5)
        self.commandQueue = queue.LifoQueue(5)
        self.logger = logger
        self.user = user
        self.is_core_task = is_core_task
        self.core_task_reason = core_task_reason

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

    def stop(self,bypass=False):
        if self.is_core_task and not bypass:
            self.logger.warning(
                f"Cannot stop core task {self.uuid} ({self.job_name}) without bypass, due to reason: {self.core_task_reason}")
            return
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
        self.tasks_set = set()
        self.logger = logger
        self.logger_generator = None

    def execute(self, job_namespace: str, job_name: str, logger_name, user,is_core_task=False, core_task_reason=None, *args, **kwargs):
        if job_name not in jobs.job_register.jobs.get(job_namespace, {}):
            self.logger_generator(f"Task<{job_namespace}:{job_name}>") if self.logger_generator else self.logger.error(f"Job not found: {job_namespace}:{job_name}")
        uuid = uuid4().hex
        logger= self.logger_generator(f"Task<{uuid[:8]}>:"+logger_name) if self.logger_generator else self.logger

        task = Task(uuid, is_core_task, core_task_reason, jobs.job_register.jobs[job_namespace][job_name],job_name,
                    logger, user, args=args, kwargs=kwargs)
        self.tasks[uuid] = task
        self.tasks_set.add(task.uuid)
        self.logger.info(
            f"{str(task)} for {job_namespace}:{job_name} created.")
        task.run()
        return uuid

    def get_tasks_as_set(self):
        
        return self.tasks_set
    
    def stop_all_and_block(self):
        for task in self.tasks.values():
            task.stop(bypass=True)
        for task in self.tasks.values():
            task.threading.join()




task_executor = TaskExecutor(None)

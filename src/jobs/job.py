
from typing import Callable


class JobRegister:
    def __init__(self):
        self.jobs = {}

    def register_job(self, namespace: str, job_name: str, commands: dict,job_func: callable):
        self.jobs[namespace] = self.jobs.get(namespace, {})
        if self.jobs[namespace].get(job_name):
            raise ValueError(f"Job '{job_name}' already exists in namespace '{namespace}'.")
        self.jobs[namespace][job_name] = {"func":job_func, "commands": commands}
    
    def register(self, namespace: str, job_path: str = None, commands: dict = {}):
        # print(f"Registering job in namespace '{namespace}' with path '{job_path}' and commands {commands}")
        def decorator(func: Callable):
            self.register_job(namespace, job_path, commands, func)
            return func
        return decorator
    
    def get_as_completion(self):
        o={}
        for namespace, jobs in self.jobs.items():
            for job in jobs:
                o[f"{namespace}:{job}"] = None
        return o

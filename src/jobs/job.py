
from typing import Callable


class JobRegister:
    def __init__(self):
        self.jobs = {}

    def register_job(self, namespace: str, job_name: str, job_func: callable):
        self.jobs[namespace] = self.jobs.get(namespace, {})
        if self.jobs[namespace].get(job_name):
            raise ValueError(f"Job '{job_name}' already exists in namespace '{namespace}'.")
        self.jobs[namespace][job_name] = job_func
    
    def register(self, namespace: str, job_name: str = None):
        def decorator(func: Callable):
            name = job_name or func.__name__
            self.register_job(namespace, name, func)
            return func
        return decorator


job_register = JobRegister()
import pkgutil
from .job import JobRegister


job_register = JobRegister()

pkg_list = pkgutil.walk_packages(__path__, __name__ + ".")

for _, module_name, ispkg in pkg_list:
    module = __import__(module_name, fromlist=['*'])

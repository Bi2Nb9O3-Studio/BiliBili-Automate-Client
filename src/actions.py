import utils
class Action():
    def __init__(self,namespace,path,function):
        self.namespace = namespace
        self.path = path
        self.function = function
    def run(self,parentTask:utils.Task):
        return self.function(parentTask)

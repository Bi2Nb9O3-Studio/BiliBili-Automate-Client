import time
import prompt_toolkit


logFile = f"./logs/{int(time.time())}.log"
logArea = None
app: prompt_toolkit.Application = None
layout = None

lives = {}
areas = {}
tasks = {}
users = {-1: []}

default_user = ...
test = None

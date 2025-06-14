#walker

import pkgutil
# import os.path as path
from .action import ActionRegister, BaseAction

# 创建 ActionRegister 实例
actions_register = ActionRegister()

pkg_list = pkgutil.walk_packages(__path__, __name__ + ".")

for _, module_name, ispkg in pkg_list:
    module = __import__(module_name, fromlist=['*'])
    # 遍历模块的属性
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        # 检查属性是否为 BaseAction 实例
        if isinstance(attr, BaseAction):
            try:
                actions_register.register(attr)
            except ValueError as e:
                print(e)
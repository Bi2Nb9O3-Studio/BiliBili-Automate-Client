import pkgutil

from .command import CommandRegister, BaseCommand

# 创建 CommandRegister 实例
commands_register = CommandRegister()

pkg_list = pkgutil.walk_packages(__path__, __name__ + ".")

for _, module_name, ispkg in pkg_list:
    module = __import__(module_name, fromlist=['*'])
    # 遍历模块的属性
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        try:
            if isinstance(attr, BaseCommand):
                commands_register.register(attr)
        except ValueError as e:
            print(e)

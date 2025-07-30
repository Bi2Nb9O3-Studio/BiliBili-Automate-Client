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
        # 检查属性是否为 BaseAction 实例
        try:
            if BaseCommand in attr.__bases__:
                commands_register.register(attr)
        except AttributeError:
            # 如果 attr 不是类或没有 __bases__ 属性，则跳过
            continue

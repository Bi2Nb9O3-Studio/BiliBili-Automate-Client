# Definition Formations

## Action

Action的定义必须位于`/src/actions`(生产环境中`/actions`)目录下任意非`__init__.py`、`action.py`内。格式如下：

```python
class ActionName(BaseAction):
    name = "ActionName"
    description = "ActionDescription"
    namespace = "namespace"
    path = "path.to.your.action"
    location = (namespace, path)
    def function(runtime_args: tuple[Logger, User], *args, **kwargs):
        # Your action logic here
        pass
```

注：

- `function`参数中必须有`runtime_args`字段，该变量会接收一个日志器和用户对象。
- 类属性中必须包含`name`,`description`,`namespace`,`path`和`location`字段
- 必须继承`BaseAction`类

## Command

### Class式注册

Command的定义必须位于`/src/commands`(生产环境中`/commands`)目录下任意非`__init__.py`、`command.py`内。格式如下：

```python
class CommandName(BaseCommand):
    name: str = "commandName"
    description: str = "commandDescription"
    aliases: list[str] = ['alias1', 'alias2']
    hidden: bool = False #是否在help中隐藏
    command: str = "command" #调用时的命令字段
    def handler(command_line: str, logger: logging.Logger):
        # Your command logic here
        ...
```

注：

- 类必须继承`BaseCommand`
- 类属性中必须包含`name`,`description`,`aliases`,`hidden`,`command`字段
- `handler`方法必须接收两个参数，第一个`command_line`是命令行字符串，第二个`logger`是日志器对象。

### 字典式注册

调用`commands.commands_register.simple_register()`注册命令，格式如下：

```python
commands.commands_register.simple_register(
            commandFunction, "command", "commandName", "commandDescritipon",["alias1","alias2"],hidden=False #or True
        )
```

## Job

### 修饰器注册

Job的定义必须位于`/src/jobs`(生产环境中`/jobs`)目录下任意非`__init__.py`、`job.py`内。格式如下：

```python
@jobs.job_register("namespace","path.to.your.job",{"command":AnyObjectYouWant})
def any_method_name_you_want(queues:Dict[str,Queue],runtime_args:Tuple[Logger,User]):
    ...
```

注：

- 此处command为Job以Task运行时能够接收的指令，而非用户输入的command
- `queues`参数是一个字典，格式如下：

    ```python
    {
        'statusQueue': LifoQueue(5),
        'commandQueue': LifoQueue(5)
    }
    ```

- `runtime_args`参数是一个元组，格式为`(Logger,User)`

### 直接注册

```python
jobs.job.job_register.register_job(namespace: str, job_name: str, commands: dict,job_func: callable)
```

注：

- `job_func`的要求同上

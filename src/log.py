
import logging
import cli

# Set new log level
SUCCESS_LEVEL_NUM=25
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")
def success(self, message, *args, **kws):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kws)
logging.Logger.success = success  # type: ignore


class LoggingHandler(logging.Handler):
    def __init__(self, logging_area: cli.LoggingArea):
        super().__init__()
        self.logging_area = logging_area

    def emit(self, record):
        message = self.format(record)
        self.logging_area.logText(f"{message}")
        return

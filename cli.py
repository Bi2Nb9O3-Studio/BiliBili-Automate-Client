from re import match
import colorama
import prompt_toolkit,logging

from prompt_toolkit.application import Application
from typing import Callable
import prompt_toolkit.buffer
import prompt_toolkit.layout
import prompt_toolkit.lexers
import prompt_toolkit.widgets
import prompt_toolkit.widgets
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.document import Document
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import StyleAndTextTuples

#logger
SUCCESS_LEVEL_NUM = 25
logging.addLevelName(SUCCESS_LEVEL_NUM, 'SUCCESS')

# 扩展Logger类以添加新的日志方法


def success(self, message, *args, **kws):
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kws)


logging.Logger.success = success


class ANSIColoredLexer(Lexer):
    def __init__(self) -> None:
        super().__init__()

    def lex_document(self, document: Document) -> Callable[[int], StyleAndTextTuples]:
        lines = document.lines

        def get_line(lineno: int) -> StyleAndTextTuples:
            "Return the tokens for the given line."
            try:
                t = document.lines[lineno - 1]
                if t.find(" [SUCCESS] ") != -1:
                    r = [
                        ("#88ff88", t)
                    ]
                elif t.find(" [WARN] ") != -1 or t.find(" [WARNING] ") != -1:
                    r = [
                        ("#ffff88", t)
                    ]
                elif t.find(" [ERROR] ") != -1:
                    r = [
                        ("#ff8888", t)
                    ]
                else:
                    r = [
                        ("#ffffff", t)
                    ]
                return r  # type: ignore
            except IndexError:
                return []

        return get_line

class LoggingArea():
    def __init__(self):
        self.textArea = prompt_toolkit.widgets.TextArea(
            focus_on_click=True,
            scrollbar=True,
            lexer=ANSIColoredLexer()
        )
        self.__setReadOnly(True)

    def logText(self, msg):
        self.__setReadOnly(False)
        self.textArea.buffer.text += f"{msg}\n"
        self.__setReadOnly(True)

    def __setReadOnly(self, value):
        self.textArea.buffer.read_only = prompt_toolkit.filters.to_filter(
            value)

    def getArea(self):
        return self.textArea

class LoggingHandler(logging.Handler):
    def __init__(self,logging_area:LoggingArea):
        super().__init__()
        self.logging_area=logging_area

    def emit(self, record):
        levelname = record.levelname
        message = self.format(record)
        self.logging_area.logText(f"{message}")

def setup_logger(name:str,path:str,loggingArea:LoggingArea)->logging.Logger:
    logger=logging.getLogger(name)
    logger.setLevel(logging.INFO)
    fileHandler = logging.FileHandler(path, encoding="utf-8")
    streamHandler = LoggingHandler(loggingArea)
    formatter = logging.Formatter(
        '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
    fileHandler.setFormatter(formatter)
    streamHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    logger.addHandler(streamHandler)
    return logger

def setup_logging_area():
    logging_area=LoggingArea()
    return logging_area
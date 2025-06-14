
import prompt_toolkit
import prompt_toolkit.filters
import prompt_toolkit.layout
from prompt_toolkit.lexers import Lexer
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import StyleAndTextTuples
from typing import Callable

import prompt_toolkit.widgets

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
            lexer=ANSIColoredLexer(),
            height=prompt_toolkit.layout.Dimension(weight=7)
        )
        self.__setReadOnly(True)

    def logText(self, msg):
        self.__setReadOnly(False)
        flag = self.textArea.buffer.document.on_last_line
        self.textArea.buffer.text += f"{msg}\n"
        if flag:
            self.textArea.buffer.cursor_position = len(
                self.textArea.buffer.text)
        self.__setReadOnly(True)

    def __setReadOnly(self, value):
        self.textArea.buffer.read_only = prompt_toolkit.filters.to_filter(
            value)

    def getArea(self):
        return self.textArea

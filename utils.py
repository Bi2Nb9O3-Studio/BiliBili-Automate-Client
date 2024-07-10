import asyncio
from concurrent.futures import thread
import io
import logging
import pickle
import queue
import re
import threading
import uuid
from easygui import msgbox
import qrcode
import qrcode.constants
import qrcode.main
import qrcode.image.pil as pil_image
import requests

import cli


class QRShower:
    def __init__(self, url: str, logger: logging.Logger) -> None:
        self.url = url
        self.generate(self.url)
        self.logger = logger

    def generate(self, url) -> 'QRShower':
        """
        Generate QR code for a given URL and save it to a file.

        :param url: The URL to encode in the QR code.

        :return QRShower: The QRShower instance.
        """
        self.qr = qrcode.main.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        self.qr.add_data(url)
        self.qr.make(fit=True)

        return self

    def show(self):
        out = io.StringIO('\n')
        self.qr.print_ascii(out)
        sp = out.getvalue().split('\n')
        for i in sp:
            self.logger.info(i)
        self.logger.warn("Please scan the QR code in 180 seconds!")


def getNewSession():
    session = requests.session()
    session.headers.update({
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    })
    return session


class Task():
    def __init__(self, name, task_function, args=(), kwargs={}) -> None:
        self.statusQueue = queue.LifoQueue(5)
        self.commandQueue = queue.LifoQueue(5)
        self.threading = threading.Thread(
            target=task_function, args=(self.statusQueue, self.commandQueue, self)+args, kwargs=kwargs, name=name)
        self.uuid = uuid.uuid4().int
        self.logger = cli.setup_logger("Task")

    def start(self):
        self.threading.start()
        self.logger.info(
            f"Task({self.uuid}) {self.threading.name}({self.threading.ident}) started.")

    def setCommand(self, command):
        self.commandQueue.put(pickle.dumps(command))

    def getStatus(self):
        return pickle.loads(self.statusQueue.get())

    def __str__(self) -> str:
        return f"{self.threading.name}({self.threading.ident})"

from dataclasses import dataclass
from typing import List
from Crypto.Cipher import PKCS1_OAEP
import binascii
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
import io
import logging
import os
import pickle
import queue
import re
import threading
import uuid
import qrcode
import requests
# import _typeshed

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
            error_correction=qrcode.ERROR_CORRECT_L,
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


class TaskCommand():
    def __init__(self,name):
        self.name=name
@dataclass
class TaskCommandUnion():
    commands: List[TaskCommand]
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

    def setCommand(self, command: TaskCommand):
        self.commandQueue.put(pickle.dumps(command))
        self.logger.info(f"Command {command} has been set.")

    def getStatus(self):
        return pickle.loads(self.statusQueue.get())

    def __str__(self) -> str:
        return f"{self.threading.name}({self.threading.ident})"


def ensure_path(path):
    if not os.path.exists(path=path):
        os.makedirs(path,exist_ok=True)
    return path
def ensure_file(file):
    if not os.path.exists(file):
        f = open(file, "w")
        f.close()
    return file


key = RSA.importKey('''\
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDLgd2OAkcGVtoE3ThUREbio0Eg
Uc/prcajMKXvkCKFCWhJYJcLkcM2DKKcSeFpD/j6Boy538YXnR6VhcuUJOhH2x71
nzPjfdTcqMz7djHum0qSZA0AyCBDABUqCrfNgCiJ00Ra7GmRj+YCK1NJEuewlb40
JNrRuoEUXpabUzGB8QIDAQAB
-----END PUBLIC KEY-----''')


def getCorrespondPath(ts):
    cipher = PKCS1_OAEP.new(key, SHA256)
    encrypted = cipher.encrypt(f'refresh_{ts}'.encode())
    return binascii.b2a_hex(encrypted).decode()

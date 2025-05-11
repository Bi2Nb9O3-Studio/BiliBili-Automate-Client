from ast import Bytes
import binascii
import ctypes
import datetime
import json
import pickle
import queue
import time
import typing
import zlib

import os
from requests import get
import cli
import brotli
import global_vars
import user
import utils


class LiveRoom():
    def __init__(self, user: user.User, id: int = -1) -> None:
        self.id = id
        self.user = user
        self.logger = cli.setup_logger(f"LiveRoom@{self.id}")
        self.sequence = 0
        self.all_quality = []
        self.using_quality = -1
        self.data_path = "./data/live/"+str(self.id)
        self.is_recording_video = 0
        self.is_recording_data = 0
        self.record_task_obj = ...

    def updateID(self, id: int):
        if id == -1:
            self.logger.error("Invaild LiveRoom ID", stack_info=True)
        if self.id == -1:
            self.id = id
            self.logger.info(f"New LiveRoom ID set to {id}")
            self.logger = cli.setup_logger("LiveRoom@{self.id}")
        elif id != self.id:
            self.id = id
            self.logger.info(f"LiveRoom ID updated to {id}")
            self.logger = cli.setup_logger("LiveRoom@{self.id}")
        else:
            self.logger.info(f"LiveRoom ID is {id}")

    def get_token(self):
        respon = self.user.session.get(
            f"https://api.live.bilibili.com/xlive/web-room/v1/index/getDanmuInfo?id={self.id}").json()
        self.token = respon['data']['token']
        self.host_list = respon['data']['host_list']

    def get_play_url(self):
        if self.id > 0:
            resp = self.user.session.get(
                f"https://api.live.bilibili.com/room/v1/Room/playUrl?cid={self.id}"
            ).json()
            if resp['code'] == -400:
                self.logger.error("Invalid Arguments")
                return -1
            elif resp['code'] == 19002003:
                self.logger.error("Room Not Found")
                return -1
            self.all_quality = [(i['qn'], i['desc'])
                                for i in resp['data']['quality_description']]
            self.using_quality = resp['data']['current_qn']
            dict.values
            self.durl = resp['data']['durl'][0]['url']
        else:
            self.logger.error("Invalid LiveRoom ID")
            return -1

    def use_sequence(self):
        self.sequence += 1
        return self.sequence

    def start_record(self):
        start_time = datetime.datetime.fromtimestamp(time.time())
        record_path = utils.ensure_path(
            self.data_path+f"/record/{start_time.strftime('%d-%m-%Y %H-%M-%S')}")
        info = self.get_info()
        if info['code'] == 1:
            self.logger.error("Invalid LiveRoomID")
            return
        elif info['data']['live_status'] != 1:
            self.logger.info(info)
            self.logger.error("Not living.")
            return

        def record_task(statusQueue: queue.LifoQueue, commandQueue: queue.LifoQueue, task: utils.Task):
            self.logger.info("Try to start record task.")
            self.get_play_url()
            self.get_token()
            with open(utils.ensure_file(record_path+"/info.json"), mode="w") as f:
                f.write(json.dumps(info))
            video_file = utils.ensure_file(record_path+f"/video.flv")
            chunk_size = 256
            response = self.user.session.get(self.durl, stream=True)
            with open(video_file, 'wb') as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    response.elapsed
                    file.write(data)
                    file.flush()

                    if statusQueue.full():
                        for _ in range(5):
                            statusQueue.get()
                    statusQueue.put(pickle.dumps({
                        "start_time": start_time,
                        "recording_time": (datetime.datetime.now()-start_time),
                        "video_file": video_file,
                    }))

                    if not commandQueue.empty():
                        command = pickle.loads(commandQueue.get())['action']
                        if command == 'stop_record':
                            self.logger.info("stop recording video.")
                            global_vars.tasks.pop(task.uuid)
                            return

                        # TODO: next step
            self.logger.info("Video record task finished.")
            global_vars.tasks.pop(task.uuid)
            return
        self.record_task_obj = utils.Task(
            f"LiveRoom@{self.id}-VideoRecord", record_task)
        global_vars.tasks[self.record_task_obj.uuid] = self.record_task_obj
        global_vars.tasks[self.record_task_obj.uuid].start()

    def get_sample_status_json_for_video_recording(self):
        return {
            "start_time": datetime.datetime.now(),
            "recording_time": datetime.datetime.now(),
            "video_file": "path_to_file",
        }

    def get_info(self):
        resp = self.user.session.get(
            f"https://api.live.bilibili.com/room/v1/Room/get_info?room_id={self.id}").json()
        return resp


class LiveRoomDataPacket():
    def __init__(self, protocl: int, operation_code: int, payload: dict | str | list, rooom: LiveRoom) -> None:
        self.protocol = protocl
        self.operation_code = operation_code
        self.room = rooom
        self.payload = payload

    def __str__(self) -> str:
        heading_size = 16
        heading_size = heading_size.to_bytes(2, "big")
        protocolver = self.protocol.to_bytes(2, "big")
        operation = self.operation_code.to_bytes(4, "big")
        sequence = self.room.use_sequence().to_bytes(4, "big")

        payload = self.payload if isinstance(
            payload, str) else json.dumps(payload, separators=(',', ':'))

        if self.protocol == 2:
            payload_code = zlib.compress(payload)
        elif self.protocol == 3:
            payload_code = brotli.compress(LiveRoomDataPacket(
                0, 3, eval(payload), self.room).__str__())
        else:
            payload_code = payload.encode('utf-8')
        total_size = 16+len(payload_code)
        total_size = total_size.to_bytes(4, "big")
        result = total_size+heading_size+protocolver+operation+sequence+payload_code
        return result

    @classmethod
    def decode(self, data, mode: typing.Literal["origin", "hexstr"] = "origin"):
        if mode == "hexstr":
            data = binascii.unhexlify(data)
        total_size = int.from_bytes(data[:4], "big")
        heading_size = int.from_bytes(data[4:6], "big")
        protocol = int.from_bytes(data[6:8], "big")
        operation = int.from_bytes(data[8:12], "big")
        sequence = int.from_bytes(data[12:16], "big")
        payload = data[16:]
        if protocol == 2:
            payload = zlib.decompress(payload)
        elif protocol == 3:
            payload = brotli.decompress(payload)
            return self.decode(payload)
        return LiveRoomDataPacket(protocol, operation, payload, None)

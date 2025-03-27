from queue import Queue
from threading import Thread
import time
import numpy as np
import cv2

from video_jawn.camera_utils.camera_feed import CameraFeed


class Singleton(type):
    """A metaclass that creates a single instance of any class that uses it."""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Coordinator(metaclass=Singleton):
    def __init__(self):
        self.camera = None
        self.curr_color = 0
        self.grayscale_intensity = 1
        self.clients = set()
        self.client_filler = None
        self.filling_clients = False
        self.using_buffer = False

    def _fill_clients(self):
        while self.filling_clients:
            if len(self.clients):
                if self.camera is not None:
                    try:
                        qsize, frame = self.camera.get_frame()
                        self.using_buffer = qsize > 2
                    except:
                        continue
                    if frame is None:
                        continue
                    gray_frame = (
                        (
                            cv2.cvtColor(
                                cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY),
                                cv2.COLOR_GRAY2BGR,
                            ).astype(np.float32)
                            * self.grayscale_intensity
                        )
                        .clip(0, 255)
                        .astype(np.uint8)
                    )
                    selected_color_frame = frame.copy()
                    for i in range(3):
                        if i != self.curr_color:
                            selected_color_frame[:, :, i] = 0

                    image = np.hstack([frame, gray_frame, selected_color_frame])
                    for client in self.clients:
                        client.queue.put(image)

    @property
    def camera_active(self):
        return self.camera is not None

    def start_camera(self, camera_id: int, scale: float):
        self.camera = CameraFeed(camera_id, scale)
        self.camera.start()
        self.client_filler = Thread(target=self._fill_clients)
        self.filling_clients = True
        self.client_filler.start()

    def kill_camera(self):
        self.filling_clients = False
        if self.client_filler is not None:
            self.client_filler.join()
        self.client_filler = None
        self.camera.terminate()
        self.camera.join()
        self.camera = None


class VideoFeedClient:
    def __init__(self):
        self.queue = Queue()
        Coordinator().clients.add(self)

    def get_frames(self):
        while True:
            try:
                image = self.queue.get_nowait()
            except:
                time.sleep(1 / 30)
                continue
            ret, buffer = cv2.imencode(".jpg", image)
            if not ret:
                continue

            frame_bytes = buffer.tobytes()
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
            )

    def terminate(self):
        Coordinator().clients.remove(self)

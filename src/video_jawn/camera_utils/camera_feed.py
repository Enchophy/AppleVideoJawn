from queue import Queue, Empty
from threading import Thread
import logging
import cv2

VIDEO_FRAME_BUFFER_SIZE_SECONDS = 30


class CameraFeed(Thread):
    def __init__(self, camera_id: int = 0):
        self._rst()
        self.break_on_next = False
        self.camera_id = camera_id
        super().__init__()

    def _rst(self):
        self.video_frame_buffer = Queue()
        self.fps = None
        self.witdth = None
        self.height = None
        self._videoCapture = None
        self.videoScale = 1

    def run(self):
        self._videoCapture = cv2.VideoCapture(0)
        self.fps = self._videoCapture.get(cv2.CAP_PROP_FPS)
        self.video_frame_buffer = Queue(1 + VIDEO_FRAME_BUFFER_SIZE_SECONDS * self.fps)
        self.witdth = int(self._videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self._videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        if self._videoCapture.isOpened():
            rval, frame = self._videoCapture.read()
        else:
            self._rst()
            raise RuntimeError("Video feed or device init invalid")

        while rval:
            rval, frame = self._videoCapture.read()
            print(self.video_frame_buffer.qsize())
            if self.video_frame_buffer.full():
                try:
                    self.video_frame_buffer.get_nowait()
                    logging.getLogger("VideoFeed").warning("Video frame buffer full")
                except Empty:
                    logging.getLogger("VideoFeed").exception(
                        "Video frame buffer full to empty"
                    )

            self.video_frame_buffer.put_nowait(frame.copy())

            if self.break_on_next == True:
                break

        self._videoCapture.release()

    def change_scale(self, scalar: int):
        self.videoScale = scalar

    def get_frame(self):
        ## TODO : add a lock to the video frame buffer to ensure that qsize and get_nowait have consistency while adding frames
        try:
            qsize = self.video_frame_buffer.qsize()
            frame = self.video_frame_buffer.get_nowait()
            frame = cv2.resize(frame, None, fx=self.videoScale, fy=self.videoScale, interpolation=cv2.INTER_LINEAR)
            return qsize, frame
        except Empty:
            return (
                0,
                None,
            )  # expected behavior when frames read faster than fps, disregard.

    def terminate(self):
        self.break_on_next = True

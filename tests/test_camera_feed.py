from video_jawn.camera_utils.camera_feed import CameraFeed
import time

def test_capture_terminates():
    cf = CameraFeed()
    cf.start()
    time.sleep(1)
    cf.terminate()
    cf.join(timeout=3)
    assert not cf.is_alive()

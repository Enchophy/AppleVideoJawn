import cv2


def list_cameras(max_index=5):
    rt = dict()
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            # retrieve properties (might be 0.0 if the camera doesn't provide them yet)
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = cap.get(cv2.CAP_PROP_FPS)
            rt[i] = (fps, width, height)
            cap.release()
    return rt

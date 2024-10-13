import cv2
from subocr import DataProducer
import sys

def is_video_valid(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return False
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()
    if frame_count == 0 and fps == 0:
        return False
    return True

class DecodedFrame:
    def __init__(self, timestamp_us, video_start_us, video_end_us, frame):
        self.timestamp_us = timestamp_us
        self.video_start_us = video_start_us
        self.video_end_us:int | None = video_end_us
        self.frame = frame


class VideoFrameReader(DataProducer):
    def __init__(self, video_path):
        self.video_path = video_path
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            print(f"Failed to open video file {video_path}")
            exit(1)
        self.current_frame_count = 0
        self.video_start_us = None
        self.video_end_us = None
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # print(self.frame_count)
        if self.frame_count is None or self.frame_count <= 0:
            print("Failed to read video info")
            exit(1)

    def __del__(self):
        self.cap.release()
        
    def produce(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        timestamp_us = self.cap.get(cv2.CAP_PROP_POS_MSEC) * 1000
        if self.video_start_us is None:
            self.video_start_us = timestamp_us
        if self.video_end_us is None:
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            if fps is not None and fps > 0:
                self.video_end_us = self.video_start_us + self.frame_count * 1_000_000 / fps

        self.current_frame_count += 1
        if self.video_end_us is not None:
            return DecodedFrame(timestamp_us, self.video_start_us, self.video_end_us, frame)
        else:
            done_us = timestamp_us - self.video_start_us
            end_us = self.video_start_us + done_us / self.current_frame_count * self.frame_count
            return DecodedFrame(timestamp_us, self.video_start_us, end_us, frame)



class VideoFrameReorderer(DataProducer):
    def __init__(self, previous_producer:DataProducer, reorder_buffer_size:int):
        self.previous_producer = previous_producer
        self.reorder_buffer_size = reorder_buffer_size
        self.reorder_buffer = []
    def produce(self):
        while len(self.reorder_buffer) < self.reorder_buffer_size:
            data = self.previous_producer.produce()
            self.reorder_buffer.append(data)
        self.reorder_buffer.sort(key=lambda x: x.timestamp_us if x is not None else sys.maxsize, reverse=True)
        return self.reorder_buffer.pop()

class VideoFrameFPSController(DataProducer):
    def __init__(self, previous_producer:DataProducer, fps:int):
        self.previous_producer = previous_producer
        if fps <= 0:
            self.fps = -1
        else:
            self.fps = fps
        self.frame_interval_us = 1_000_000 / fps
        self.current_wanted_us = 0
    def produce(self):
        while True:
            data:DecodedFrame = self.previous_producer.produce()
            if data is None:
                return None
            if self.fps <= 0:
                return data
            if data.timestamp_us >= self.current_wanted_us:
                self.current_wanted_us += self.frame_interval_us
                return data
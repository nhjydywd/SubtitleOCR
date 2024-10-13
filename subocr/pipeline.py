from enum import Enum
from typing import List, Callable
import threading
import time

from subocr import *



class SubocrPipeline:
    def __init__(self, path_video:str, fps:int, anchors:List[SubtitleAnchor], config, cmd_args) -> None:
        self._path_video = path_video
        self._fps = fps
        self._anchors = anchors
        self._cmd_args = cmd_args
        self._caption_merger = CaptionMerger(anchors)
        recognizer = SubtitleRecognizer(path_video, fps, anchors, config, cmd_args)
        self._producer = AsyncDataProducer(recognizer, 10)
        
        self._is_alive = AtomicValue(False)
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._run)



    def start(self):
        self._is_alive.set(True)
        self._producer.start()
        self._thread.start()

    def stop(self):
        self._is_alive.set(False)
        self._thread.join()
        self._producer.stop(lambda x: None)

    # 可供查阅的信息
    class Statistics:
        def __init__(self) -> None:
            self.is_initialized:bool = False
            self.is_finished:bool = False
            self.done_us:int = 0
            self.total_us:int = 0
            self.speed_up:float = 0
            self.captions:List[Caption] = []

    def query(self)->Statistics:
        with self._lock:
            result = SubocrPipeline.Statistics()
            result.is_finished = not self._thread.is_alive()
            result.done_us = self._statistic.done_us
            result.total_us = self._statistic.total_us
            result.speed_up = self._statistic.speed_up
            result.captions = self._caption_merger.captions.copy()
        return result
    
    _statistic = Statistics()
    def _run(self):
        start_time = time.time()
        while self._is_alive.get():
            frame:RecognizedFrame = self._producer.produce()
            if frame is None:
                break
            with self._lock:
                self._caption_merger.incoming_frame(frame)
                done_us = frame.detected_frame.decoded_frame.timestamp_us - frame.detected_frame.decoded_frame.video_start_us
                self._statistic.done_us = done_us
                self._statistic.total_us = frame.detected_frame.decoded_frame.video_end_us - frame.detected_frame.decoded_frame.video_start_us
                sec_elapsed = time.time() - start_time
                if sec_elapsed > 0:
                    self._statistic.speed_up = done_us / (sec_elapsed * 1_000_000)
                else:
                    self._statistic.speed_up = 0
                self._statistic.is_initialized = True


        with self._lock:
            self._caption_merger.finish()
    
    def export_srt(self, path:str):
        with self._lock:
            s = ""
            idx = 1
            for caption in self._caption_merger.captions:
                str_start = _us_to_str_time(caption.start_us)
                str_end = _us_to_str_time(caption.end_us)
                for text in caption.caption:
                    text = text.replace("\n", " ")
                    s += f"{idx}\n{str_start} --> {str_end}\n{text}\n\n"
                    idx += 1
            with open(path, "w", encoding="utf-8") as f:
                f.write(s)

def _us_to_str_time(us)->str:
    total_seconds = int(us // 1_000_000)
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    ms = int((us % 1_000_000) // 1_000)
    return "{:02d}:{:02d}:{:02d},{:03d}".format(hours, minutes, seconds, ms)
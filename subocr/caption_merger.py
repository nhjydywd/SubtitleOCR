from subocr import *
from typing import List
from distance import levenshtein

class Caption:
    def __init__(self, start_us:int, end_us:int, caption:List[str]) -> None:
        self.start_us = start_us
        self.end_us = end_us
        self.caption = caption

class CaptionMerger:
    # 对于每一条字幕，最远向前搜索（尝试延展）的时间
    MAX_SEARCH_TIME_US = 600_000
    # 对于每一条字幕，被判定为有效的最低时间
    MIN_VALID_TIME_US = 500_000

    def __init__(self, anchors:List[SubtitleAnchor]) -> None:
        self.anchors:List[SubtitleAnchor] = anchors
        self.buffered_frames:List[RecognizedFrame] = []
        self.current_caption_frame_count = 0
        self.captions:List[Caption] = []
    
    def incoming_frame(self, frame:RecognizedFrame):
        if len(self.buffered_frames) > 0:
            if frame.detected_frame.decoded_frame.timestamp_us < self.buffered_frames[-1].detected_frame.decoded_frame.timestamp_us:
                print("Error: incoming frame is not in order")
                exit(1)
        self.buffered_frames.append(frame)
        # 是否与当前字幕match?
        if self.current_caption_frame_count > 0:
            if self._is_new_frame_match(frame):
                self.current_caption_frame_count = len(self.buffered_frames)
                return
        # 不match，是否处于当前字幕的搜索空间内?
        if self.current_caption_frame_count > 0:
            new_frame_us = frame.detected_frame.decoded_frame.timestamp_us
            last_frame_us = self.buffered_frames[self.current_caption_frame_count - 1].detected_frame.decoded_frame.timestamp_us
            if new_frame_us - last_frame_us <= self.MAX_SEARCH_TIME_US:
                return
        # 既不match，也超出当前字幕的搜索空间，则结束当前字幕
        if self.current_caption_frame_count > 0:
            self._collect_current_caption()
        # 并定位新的当前字幕
        self._locate_new_caption_in_buffer()
    
    def finish(self):
        # 将所有缓冲区数据生成字幕（如果有）
        while len(self.buffered_frames) > 0:
            self._collect_current_caption()
            self._locate_new_caption_in_buffer()

    MATCH_THRESH_MAX_LEN_DIFF = 5
    MATCH_THRESH_STRLEN_PER_EDIT_DISTANCE = 4 # 句子长度每达到这个长度，容忍的编辑距离就多1
    MATCH_THRESH_MAX_EDIT_DISTANCE = 3 # 容忍的编辑距离的最大值
    def _is_new_frame_match(self, frame:RecognizedFrame)->bool:
        str_new_frame = self._get_frame_primary_str(frame)
        # 对于字幕缓冲区中的每一种str，给予一次匹配机会
        considered_str = set()
        for i in range(0, self.current_caption_frame_count):
            s = self._get_frame_primary_str(self.buffered_frames[i])
            if s in considered_str:
                continue
            considered_str.add(s)
            # 条件1：两句长度差异如果太大，则不匹配
            if abs(len(s) - len(str_new_frame)) > self.MATCH_THRESH_MAX_LEN_DIFF:
                continue

            # 条件2：两句编辑距离如果在阈值内，则匹配
            tolerance = max(len(s), len(str_new_frame)) // self.MATCH_THRESH_STRLEN_PER_EDIT_DISTANCE
            tolerance = min(tolerance, self.MATCH_THRESH_MAX_EDIT_DISTANCE)
            edit_distance = levenshtein(s, str_new_frame)
            if edit_distance <= tolerance:
                return True
        return False


    def _get_frame_primary_str(self, frame:RecognizedFrame)->str:
        s = None
        for i in range(0, len(self.anchors)):
            if not self.anchors[i].is_primary:
                continue
            if s is None:
                s = frame.texts[i]
            else:
                s += "\n" + frame.texts[i]
        
        return s if s is not None else ""
    
    def _collect_current_caption(self):
        if self.current_caption_frame_count <= 0:
            return
        start_us = self.buffered_frames[0].detected_frame.decoded_frame.timestamp_us
        end_us = self.buffered_frames[self.current_caption_frame_count - 1].detected_frame.decoded_frame.timestamp_us
        if end_us - start_us >= self.MIN_VALID_TIME_US:
            # 每个anchor的caption由投票决定
            caption = []
            for i in range(0, len(self.anchors)):
                anchor = self.anchors[i]
                vote = {}
                for j in range(0, self.current_caption_frame_count):
                    text = self.buffered_frames[j].texts[i]
                    if text not in vote:
                        vote[text] = 0
                    vote[text] += 1
                max_vote_count = 0
                max_vote_text = ""
                for text, count in vote.items():
                    if count > max_vote_count:
                        max_vote_count = count
                        max_vote_text = text
                caption.append(max_vote_text)

            self.captions.append(Caption(start_us, end_us, caption))
        self.buffered_frames = self.buffered_frames[self.current_caption_frame_count:]
        self.current_caption_frame_count = 0

    def _locate_new_caption_in_buffer(self):
        while len(self.buffered_frames) > 0:
            s = self._get_frame_primary_str(self.buffered_frames[0])
            if len(s) == 0:
                self.buffered_frames = self.buffered_frames[1:]
                continue
            # 找到了新的字幕，进行延展
            self.current_caption_frame_count = 1
            for i in range(1, len(self.buffered_frames)):
                new_frame_us = self.buffered_frames[i].detected_frame.decoded_frame.timestamp_us
                last_frame_us = self.buffered_frames[self.current_caption_frame_count - 1].detected_frame.decoded_frame.timestamp_us
                if new_frame_us - last_frame_us > self.MAX_SEARCH_TIME_US:
                    break
                if self._is_new_frame_match(self.buffered_frames[i]):
                    self.current_caption_frame_count = i + 1
            break
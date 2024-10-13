from subocr import *

from paddleocr.tools.infer.predict_rec import TextRecognizer

from enum import Enum
from typing import List
import os

class RecognizedFrame:
    def __init__(self, detected_frame, texts):
        self.detected_frame:DetectedFrame = detected_frame
        self.texts = texts

class SubtitleLanguage(Enum):
    ZH = "zh"
    EN = "en"
    JA = "ja"
    KO = "ko"

class SubtitleAnchor:
    def __init__(self, center_x:int, center_y:int, height:int, lang:SubtitleLanguage, is_primary:bool) -> None:
        self.center_x = center_x
        self.center_y = center_y
        self.height = height
        self.lang = lang
        self.is_primary = is_primary

class SubtitleRecognizer(DataProducer):
    def __init__(self, path_video:str, fps:int, anchors:List[SubtitleAnchor], config:dict, cmd_args) -> None:
        self.path_video = path_video
        self.fps = fps
        self.anchors = anchors
        
        self.ppocr_recognizers = {}
        langs = set([anchor.lang for anchor in anchors])
        for lang in langs:
            code = lang.value
            # cmd args for paddleocr recognizer
            algorithm = config['models']['rec'][code]['algorithm']
            cmd_args.rec_algorithm = algorithm
            cmd_args.use_onnx = False
            cmd_args.benchmark = False
            cmd_args.warmup = False
            dir_model = config['models']['base_dir']
            name_model = config['models']['rec'][code]['model_path']
            cmd_args.rec_model_dir = os.path.join(dir_model, name_model)
            dir_keys = config['models']['rec']['keys_dir']
            path_keys = config['models']['rec'][code]['keys']
            cmd_args.rec_char_dict_path = os.path.join(dir_model, dir_keys, path_keys)
            self.ppocr_recognizers[code] = TextRecognizer(cmd_args)

        subtitle_detector = SubtitleDetector(path_video, fps, config, cmd_args)
        self.frame_producer = AsyncDataProducer(subtitle_detector, 10)
        self.frame_producer.start()

    def __del__(self):
        if hasattr(self, 'frame_producer'):
            self.frame_producer.stop(lambda x: None)
    
    def produce(self):
        detected_frame:DetectedFrame = self.frame_producer.produce()
        if detected_frame is None:
            return None
        texts = []
        for anchor in self.anchors:
            text = ""
            bbox = extract_bbox_for_anchor(anchor, detected_frame)
            if bbox is not None:
                left = bbox[0] - bbox[2] / 2
                right = bbox[0] + bbox[2] / 2
                top = bbox[1] - bbox[3] / 2
                bottom = bbox[1] + bbox[3] / 2
                image = detected_frame.decoded_frame.frame[int(top):int(bottom), int(left):int(right), :]
                recognizer = self.ppocr_recognizers[anchor.lang.value]
                rec_res, elapsed = recognizer([image])
                text, score = rec_res[0]
            texts.append(text)
        return RecognizedFrame(detected_frame, texts)
    

def extract_bbox_for_anchor(anchor:SubtitleAnchor, detected_frame:DetectedFrame):
    result_bbox = None
    def update_result_bbox(bbox):
        if result_bbox is None:
            return bbox
        else:
            left = min(result_bbox[0]-result_bbox[2]/2, bbox[0]-bbox[2]/2)
            right = max(result_bbox[0]+result_bbox[2]/2, bbox[0]+bbox[2]/2)
            top = min(result_bbox[1]-result_bbox[3]/2, bbox[1]-bbox[3]/2)
            bottom = max(result_bbox[1]+result_bbox[3]/2, bbox[1]+bbox[3]/2)
            return (left+right)/2, (top+bottom)/2, right-left, bottom-top
    ANCHOR_TOP = anchor.center_y - anchor.height / 2
    ANCHOR_BOTTOM = anchor.center_y + anchor.height / 2
    Y_EXPAND_RANGE_FACTOR = 0.1 # 提取的BBox在y方向上扩张的范围（以anchor为基础）
    MIN_TOP = anchor.center_y - anchor.height * (0.5 + Y_EXPAND_RANGE_FACTOR)
    MAX_BOTTOM = anchor.center_y + anchor.height * (0.5 + Y_EXPAND_RANGE_FACTOR)

    # 按y轴上IoU匹配情况分类
    THRESH_IOU = 0.6
    THRESH_WEAK_IOU = 0.4
    y_bboxes = []
    weak_y_bboxes = []
    for bbox in detected_frame.bboxes:
        top = bbox[1] - bbox[3] / 2
        bottom = bbox[1] + bbox[3] / 2
        inter = min(bottom, ANCHOR_BOTTOM) - max(top, ANCHOR_TOP)
        if inter <= 0:
            continue
        union = max(bottom, ANCHOR_BOTTOM) - min(top, ANCHOR_TOP)
        iou = inter / union
        if iou >= THRESH_IOU:
            y_bboxes.append(bbox)
        elif iou >= THRESH_WEAK_IOU:
            weak_y_bboxes.append(bbox)


    # 情况1.1：y轴上的IoU强匹配，且center_x接近
    # 此情况下，将原目标框x方向围绕centerX做一个镜像补充，且y方向适当调整
    idx_bbox = -1
    min_x_diff = 1e9
    THRESH_X_DIFF_FACTOR = 0.3 # 允许有相当于（宽度或高度中最大者）的30%的偏移
    for i, bbox in enumerate(y_bboxes):
        bbox = y_bboxes[i]
        width = bbox[2]
        height = bbox[3]
        thresh_x_diff = max(width, height) * THRESH_X_DIFF_FACTOR
        x_diff = abs(bbox[0] - anchor.center_x)
        if x_diff < min_x_diff and x_diff <= thresh_x_diff:
            min_x_diff = x_diff
            idx_bbox = i
    if idx_bbox >= 0:
        bbox = y_bboxes[idx_bbox]
        width = bbox[2]
        height = bbox[3]
        left = bbox[0] - width / 2
        right = bbox[0] + width / 2
        top = bbox[1] - height / 2
        top = min(ANCHOR_TOP, max(MIN_TOP, top))
        bottom = bbox[1] + height / 2
        bottom = max(ANCHOR_BOTTOM, min(MAX_BOTTOM, bottom))
        if (right - anchor.center_x) > (anchor.center_x - left):
            left = anchor.center_x - (right - anchor.center_x) # 左侧填充
        else:
            right = anchor.center_x + (anchor.center_x - left) # 右侧填充
        center_x = (left + right) / 2
        center_y = (top + bottom) / 2
        width = right - left
        height = bottom - top
        result_bbox = update_result_bbox((center_x, center_y, width, height))
        # 清除所有center_x落在提取框范围内的BBox
        new_y_bboxes = []
        for bbox in y_bboxes:
            if bbox[0] >= left and bbox[0] <= right:
                continue
            new_y_bboxes.append(bbox)
        y_bboxes = new_y_bboxes
    
    # 情况1.2：y轴上的IoU强匹配，虽然centerX不接近，但多个BBox围绕centerX形成对称
    # 多个BBox合并后centerX误差小于（宽度*factor），才视作对称的情况
    THRESH_SYM_CENTER_X_DIFF_FACTOR = 0.15   
    while len(y_bboxes) > 1:
        left = 1e9
        right = -1e9
        top = 1e9
        bottom = -1e9
        for bbox in y_bboxes:
            left = min(left, bbox[0] - bbox[2] / 2)
            right = max(right, bbox[0] + bbox[2] / 2)
            top = min(top, bbox[1] - bbox[3] / 2)
            bottom = max(bottom, bbox[1] + bbox[3] / 2)
        width = right - left
        center_x = (left + right) / 2
        thresh_x_diff = width * THRESH_SYM_CENTER_X_DIFF_FACTOR
        if abs(center_x - anchor.center_x) <= thresh_x_diff:
            # 以对称BBox更新结果，结束
            top = min(ANCHOR_TOP, max(MIN_TOP, top))
            bottom = max(ANCHOR_BOTTOM, min(MAX_BOTTOM, bottom))
            if (right - anchor.center_x) > (anchor.center_x - left):
                left = anchor.center_x - (right - anchor.center_x) # 左侧填充
            else:
                right = anchor.center_x + (anchor.center_x - left) # 右侧填充
            center_x = (left + right) / 2
            center_y = (top + bottom) / 2
            width = right - left
            height = bottom - top
            result_bbox = update_result_bbox((center_x, center_y, width, height))
            break
        # 剔除离anchor centerX最远的box，继续
        max_dist = -1e9
        idx_bbox = -1
        for i, bbox in enumerate(y_bboxes):
            dist = abs(bbox[0] - anchor.center_x)
            if dist > max_dist:
                max_dist = dist
                idx_bbox = i
        y_bboxes.pop(idx_bbox)
    
    # 情况2：y轴上的IoU弱匹配，但centerX强匹配
    # 允许有相当于（宽度或高度中最大者）的20%的偏移
    THRESH_STRONG_X_DIFF_FACTOR = 0.2
    idx_bbox = -1
    min_x_diff = 1e9
    for i, bbox in enumerate(weak_y_bboxes):
        bbox = weak_y_bboxes[i]
        width = bbox[2]
        height = bbox[3]
        thresh_x_diff = max(width, height) * THRESH_STRONG_X_DIFF_FACTOR
        x_diff = abs(bbox[0] - anchor.center_x)
        if x_diff < min_x_diff and x_diff <= thresh_x_diff:
            min_x_diff = x_diff
            idx_bbox = i
    if idx_bbox >= 0:
        bbox = weak_y_bboxes[idx_bbox]
        width = bbox[2]
        height = bbox[3]
        left = bbox[0] - width / 2
        right = bbox[0] + width / 2
        top = bbox[1] - height / 2
        top = min(ANCHOR_TOP, max(MIN_TOP, top))
        bottom = bbox[1] + height / 2
        bottom = max(ANCHOR_BOTTOM, min(MAX_BOTTOM, bottom))
        if (right - anchor.center_x) > (anchor.center_x - left):
            left = anchor.center_x - (right - anchor.center_x) # 左侧填充
        else:
            right = anchor.center_x + (anchor.center_x - left) # 右侧填充
        center_x = (left + right) / 2
        center_y = (top + bottom) / 2
        width = right - left
        height = bottom - top
        result_bbox = update_result_bbox((center_x, center_y, width, height))

    # 检查有效性
    if result_bbox is not None:
        left = result_bbox[0] - result_bbox[2] / 2
        right = result_bbox[0] + result_bbox[2] / 2
        top = result_bbox[1] - result_bbox[3] / 2
        bottom = result_bbox[1] + result_bbox[3] / 2
        if top >= bottom or left >= right:
            result_bbox = None

    return result_bbox

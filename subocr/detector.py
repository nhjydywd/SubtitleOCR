from subocr import *
from paddleocr.tools.infer.predict_det import TextDetector
import os

def ppocr_det_param_inject(cmd_args, config):
        algorithm = config['models']['det']['zh']['algorithm']
        cmd_args.det_algorithm = algorithm
        cmd_args.use_onnx = False
        cmd_args.benchmark = False
        cmd_args.warmup = False
        dir_model = config['models']['base_dir']
        name_model = config['models']['det']['zh']['model_path']
        cmd_args.det_model_dir = os.path.join(dir_model, name_model)

class DetectedFrame:
    def __init__(self, decoded_frame, bboxes):
        self.decoded_frame:DecodedFrame = decoded_frame
        self.bboxes = bboxes

class SubtitleDetector(DataProducer):
    def __init__(self, path_video, fps, config:dict, cmd_args) -> None:
        self.path_video = path_video
        self.fps = fps
        # cmd args for paddleocr detector
        ppocr_det_param_inject(cmd_args, config)
        self.ppocr_detector = TextDetector(cmd_args)

        video_frame_reader = VideoFrameReader(path_video)
        video_frame_reorderer = VideoFrameReorderer(video_frame_reader, 10)
        video_frame_fps_controller = VideoFrameFPSController(video_frame_reorderer, fps)
        self.frame_producer = AsyncDataProducer(video_frame_fps_controller, 10)
        self.frame_producer.start()
    def __del__(self):
        if hasattr(self, 'frame_producer'):
            self.frame_producer.stop(lambda x: None)

    def produce(self):
        decoded_frame:DecodedFrame = self.frame_producer.produce()
        if decoded_frame is None:
            return None
        ppocr_bboxes, elapsed = self.ppocr_detector(decoded_frame.frame)
        bboxes = []
        for box in ppocr_bboxes:
            left, top = box[0]
            right, bottom = box[2]
            center_x = (left + right) / 2
            center_y = (top + bottom) / 2
            width = right - left
            height = bottom - top
            bboxes.append((center_x, center_y, width, height))
        return DetectedFrame(decoded_frame, bboxes)
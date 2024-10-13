import sys
import os
import time
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import cv2
import platform
import json
from subocr import SubtitleDetector
from paddleocr.tools.infer.utility import init_args


parser = init_args()
parser.add_argument("-v", "--video", help="path to video file", required=True)
args = parser.parse_args()
args.use_gpu = True
if platform.system() == 'Darwin':
    args.use_gpu = False

with open("config.json", "r") as f:
    config = json.load(f)
detector = SubtitleDetector(args.video, 10, config, args)



while True:
    start_time = time.time()
    detected_frame = detector.produce()
    if detected_frame is None:
        break
    frame = detected_frame.decoded_frame.frame
    bboxes = detected_frame.bboxes
    for box in bboxes:
        center_x, center_y, width, height = box
        left = int(center_x - width / 2)
        right = int(center_x + width / 2)
        top = int(center_y - height / 2)
        bottom = int(center_y + height / 2)
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
    end_time = time.time()
    print("Time: ", end_time - start_time)
    cv2.imshow("frame", frame)
    cv2.waitKey(1)

    
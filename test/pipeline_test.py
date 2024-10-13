import sys
import os
import time
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import cv2
import platform
import json
from subocr import *
from paddleocr.tools.infer.utility import init_args

parser = init_args()
parser.add_argument("-v", "--video", help="path to video file", required=True)
args = parser.parse_args()
args.use_gpu = True
if platform.system() == 'Darwin':
    args.use_gpu = False

anchors = []
anchors.append(SubtitleAnchor(639, 649, 52, SubtitleLanguage.ZH, True))
anchors.append(SubtitleAnchor(632, 696, 40, SubtitleLanguage.JA, False))

with open("config.json", "r") as f:
    config = json.load(f)
pipeline = SubocrPipeline(args.video, 10, anchors, config, args)
pipeline.start()

captions = []
while True:
    stat:SubocrPipeline.Statistics = pipeline.query()
    if stat.is_finished:
        break
    done_str = us2mmss(stat.done_us)
    total_str = us2mmss(stat.total_us)
    print(f"Done: {done_str}, Total: {total_str}")
    if len(stat.captions) > len(captions):
        captions = stat.captions.copy()
        caption:Caption = captions[-1]
        start_str = us2mmss(caption.start_us)
        end_str = us2mmss(caption.end_us)
        print(f"{start_str} ==> {end_str}:")
        for text in caption.caption:
            print(text)
    time.sleep(0.5)
pipeline.stop()
print("pipeline finished.")
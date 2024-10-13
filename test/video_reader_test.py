import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from subocr import video_reader
import cv2
import argparse
import time


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--video", help="path to video file", required=True)
    parser.add_argument("-f", "--fps", help="fps to control", type=int, default=1)
    args = parser.parse_args()
    video_path = args.video
    video_fps = args.fps
    video_frame_reader = video_reader.VideoFrameReader(video_path)
    video_frame_reorderer = video_reader.VideoFrameReorderer(video_frame_reader, 10)
    video_frame_fps_controller = video_reader.VideoFrameFPSController(video_frame_reorderer, video_fps)
    while True:
        start_time = time.time()
        data = video_frame_fps_controller.produce()
        if data is None:
            print("Video ended.")
            break
        end_time = time.time()
        print("Time: ", end_time - start_time, "\tTimestamp: ", data.timestamp_us / 1_000_000)
        cv2.imshow("frame", data.frame)
        cv2.waitKey(1)
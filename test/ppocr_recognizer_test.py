import os
import argparse
import cv2
from paddleocr.tools.infer.predict_rec import TextRecognizer
from paddleocr.tools.infer.utility import init_args


parser = init_args()
parser.add_argument("-i", "--image", help="path to image file", required=True)
args = parser.parse_args()

args.rec_model_dir = os.path.join("models", "ch_PP-OCRv4_rec_infer")
args.rec_char_dict_path = os.path.join("keys", "ppocr_keys_v1.txt")
args.use_gpu = False
args.use_onnx = False
args.benchmark = False
args.warmup = False


recognizer = TextRecognizer(args)

image_path = args.image
image = cv2.imread(image_path)

rec_res, rec_score = recognizer([image])
print(rec_res)
print(rec_score)
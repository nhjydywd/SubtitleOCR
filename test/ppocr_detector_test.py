import os
import argparse
import cv2
from paddleocr.tools.infer.predict_det import TextDetector
from paddleocr.tools.infer.utility import init_args

parser = init_args()
parser.add_argument("-i", "--image", help="path to image file", required=True)
args = parser.parse_args()

args.det_algorithm = 'DB'
args.use_gpu = False
args.use_onnx = False
args.benchmark = False
args.warmup = False
args.det_model_dir = os.path.join("models", "ch_PP-OCRv4_det_infer")

detector = TextDetector(args)


image_path = args.image
image = cv2.imread(image_path)
boxes, scores = detector(image)
print(boxes)
print(scores)
for box in boxes:
    left, top = box[0]
    right, bottom = box[2]
    pt1 = (int(left), int(top))
    pt2 = (int(right), int(bottom))
    cv2.rectangle(image, pt1, pt2, (0, 0, 255), 2)
cv2.imshow("image", image)
cv2.waitKey(0)








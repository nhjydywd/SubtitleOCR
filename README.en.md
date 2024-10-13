English | [简体中文](README.md)

# SubtitleOCR

Extracting hardcode subtitles in videos using Optical Character Recognition(OCR), and converting to independent '.srt' files.

## Video Tutorial
The video is too big. Please go to [BiliBili](https://www.bilibili.com/video/BV1dJ2rYPEKP/) to watch it.

<img src="docs/tutorial.png" alt="tutorial" style="max-height: 300px;">

## Install & Run
Get source code：
```
git clone https://github.com/nhjydywd/SubtitleOCR
cd SubtitleOCR
```

Install dependencies：
```
pip install -r requirements.txt
```

Download models (can be skipped next time)
```
python ./download_models.py
```
If the download failed, you need to go to [the official site of PaddleOCR](https://paddlepaddle.github.io/PaddleOCR/main/ppocr/model_list.html) to manually download models.

After downloading, the `models` directory should be like:

![models文件夹](docs/models.png)


Finally, launch the GUI:
```
python ./launch_gui.py --lang en
```



## Features
* 🔄 Multilanguage Subtitles：can assign different languages for each row of subtitle.
* 🚀 GPU Support：take advantage of GPU acceleration。
* 🔍 Accurate：subtitle selection based on the anchor (center point) significantly enhances the ability to filter irrelevant text in the picture compared to traditional selection based on rectangular areas.


## Thanks
PaddleOCR：[https://github.com/PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)
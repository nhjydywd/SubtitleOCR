<!-- 简体中文 | [English](README.en.md) -->


# 望言OCR

望言OCR是一款快如闪电的硬字幕提取工具，旨在加速AI时代下的视频硬字幕数据挖掘工作。

您只需一台具有普通M芯片的Mac，或者一台搭载3060级别显卡的Windows电脑，便能达到10倍速以上的硬字幕提取速度。

用户交流QQ群：960402870

<div align="center">
  <img src="docs/AppIcon_256pt.png" style="max-height: 80px;max-width: 80px;">
</div>

## 下载社区版

望言OCR分为专业版和社区版。社区版是望言OCR的功能轻量化免费版本。它具有望言OCR的大部分核心功能，例如高速提取，批量操作，字幕编辑等，能够高效利用您的电脑硬件快速提取硬字幕。

### Windows用户：
[点此处下载Windows版APP](https://github.com/nhjydywd/SubtitleOCR/releases/tag/v3.1.2)

### Mac用户：
[点此处下载mac版APP](https://github.com/nhjydywd/SubtitleOCR/releases/tag/1.2.1)



### 使用教程
可在[哔哩哔哩](https://www.bilibili.com/video/BV1yn62YjE76/?spm_id_from=333.1387.homepage.video_card.click)观看使用教程（Windows/MacOS通用）。

## 下载专业版
#### 如果社区版不能满足您的需求，可尝试望言OCR专业版。专业版针对用户提出的一些痛点问题进行了针对性优化，截至目前功能特性对比如下：
| 功能特性 | 社区版 | 专业版 |
| :------: | :------: | :------:  | 
| 高速提取 | ✅ | ✅  |
| 极速提取<br>(Boost加速功能) | ❌ | ✅<br>(可提高约100%识别速度)   |
| 自研模型 | ❌ | ✅ <br>(可实现中文空格及繁体字识别) |
| 甄别错误识别结果 | ❌ | ✅ <br>(方便纠错) |
| 批量提取 | ✅ | ✅  |
| 历史记录 | ❌ | ✅  |
| 批量替换 | ❌ | ✅  |
| 多格式导出 | ❌ | ✅  |

<br>

#### 关于专业版与社区版的性能区别，您可参考下方的列表：<br>（x后面的数字表示能达到几倍速，例如x10代表10倍速，即10分钟的视频在1分钟内处理完毕）

| 测试平台  | 望言OCR（社区版） | **望言OCR（专业版）** |
| :------: | :------: | :------: |
| M1 Macbook Air   | x10.5 | **x22.1** |
| M2 Macbook Air   | x14.9 | **x29.6** |
| M3 Macbook Pro | x3.5  | x21.7 | **x51.9** |
| NVIDIA RTX 3060（with Intel I5 12400）  | x15.2 | **x32.5** |
| NVIDIA RTX 4070（with AMD R7 5800X）  | x24.1 | **x48.8** |
 
备注：测试视频为一段45分钟的含有中英双语字幕的mp4视频，您实际运行的速度可能受具体视频、CPU性能和GPU型号的影响，但专业版基本上都能快100%左右。

<br>

更多功能，您可下载专业版试用：

Windows：https://pan.baidu.com/s/1muf9eM9BtGFKKtMCQpZ6WQ?pwd=w2ei

Mac：https://apps.apple.com/cn/app/%E6%9C%9B%E8%A8%80ocr/id6738074717?mt=12

对应的视频教程：https://www.bilibili.com/video/BV1FUAHehEns/?vd_source=48fff58090109fe7eb61febbc62c153b









## 修改与定制
v1.2.1版本在技术上支持二次开发。如需二次开发，请见[此处教程](custom.md)。


## 鸣谢
PaddleOCR：[https://github.com/PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)

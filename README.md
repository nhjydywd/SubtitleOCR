<!-- 简体中文 | [English](README.en.md) -->


# 望言OCR

望言OCR是一款快如闪电的硬字幕提取工具，旨在加速AI时代下的视频硬字幕数据挖掘工作。

您只需一台具有普通M芯片的Mac，或者一台搭载3060级别显卡的Windows电脑，便能达到10倍速以上的硬字幕提取速度。

用户交流QQ群：960402870

<div align="center">
  <img src="docs/AppIcon_256pt.png" style="max-height: 80px;max-width: 80px;">
</div>

## 下载开源版本
望言OCR现在是一个商业化项目，自v1.4起的版本是付费的，但仍提供v1.3及其以下的开源/免费版的下载。如果您希望使用开源/免费版，可从此页面下载：
### Mac用户：
[点此处下载mac版APP](https://github.com/nhjydywd/SubtitleOCR/releases/tag/1.2.1)

<div style="text-align: center;">
  <img src="docs/mac_demo.gif" style="max-height: 300px;">
</div>

### Windows用户：
[点此处下载Windows版APP](https://github.com/nhjydywd/SubtitleOCR/releases/tag/1.2.1)


### 使用教程
可在[哔哩哔哩](https://www.bilibili.com/video/BV1yn62YjE76/?spm_id_from=333.1387.homepage.video_card.click)观看使用教程（Windows/MacOS通用）。

## 商业化版本
#### 如果开源/免费版不能满足您的需求，可尝试望言OCR的最新版本。最新版已经更新到了v3.1，功能特性如下：
| 功能特性 | 免费版v1.3 | 商业版v3.1 |
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

#### 关于商业版与免费版的性能区别，您可参考下方的列表：<br>（x后面的数字表示能达到几倍速，例如x10代表10倍速，即10分钟的视频在1分钟内处理完毕）

| 测试平台  | 望言OCR<br>(免费版v1.3) | **望言OCR<br>(商业版v3.1)** |
| :------: | :------: | :------: |
| M1 Macbook Air   | x10.5 | **x22.1** |
| M2 Macbook Air   | x14.9 | **x29.6** |
| M3 Macbook Pro | x3.5  | x21.7 | **x51.9** |
| NVIDIA RTX 3060（with Intel I5 12400）  | x15.2 | **x32.5** |
| NVIDIA RTX 4070（with AMD R7 5800X）  | x24.1 | **x48.8** |
 
备注：测试视频为一段45分钟的含有中英双语字幕的mp4视频，您实际运行的速度可能受具体视频、CPU性能和GPU型号的影响，但商业版基本上都能快100%左右。

<br>

更多功能，您可下载最新版试用：

Mac：https://apps.apple.com/cn/app/%E6%9C%9B%E8%A8%80ocr/id6738074717?mt=12

Windows：https://pan.baidu.com/s/1muf9eM9BtGFKKtMCQpZ6WQ?pwd=w2ei

对应的视频教程：https://www.bilibili.com/video/BV1FUAHehEns/?vd_source=48fff58090109fe7eb61febbc62c153b









## 修改与定制
如需二次开发，请见[此处教程](custom.md)。


## 鸣谢
PaddleOCR：[https://github.com/PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)

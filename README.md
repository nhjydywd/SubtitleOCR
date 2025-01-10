<!-- 简体中文 | [English](README.en.md) -->


# 望言OCR

望言OCR是一款快如闪电的硬字幕提取工具，旨在加速AI时代下的视频硬字幕数据挖掘工作。

您只需一台具有普通M芯片的Mac，或者一台搭载3060级别显卡的Windows电脑，便能达到10倍速以上的硬字幕提取速度。

<div align="center">
  <img src="docs/AppIcon_256pt.png" style="max-height: 80px;max-width: 80px;">
</div>


### Mac用户：
[点此处下载mac版APP](https://github.com/nhjydywd/SubtitleOCR/releases/tag/v1.2.1)

<div style="text-align: center;">
  <img src="docs/mac_demo.gif" style="max-height: 300px;">
</div>

### Windows用户：
[点此处下载Windows版APP](https://github.com/nhjydywd/SubtitleOCR/releases/tag/v1.2.1)

开发者使用的配置：Win11 + I5 12400 + NVIDIA RTX 3060

已确认的最低可运行配置：Win10(22H2) + i5-7200U + NVIDIA MX150（较慢，约1.1倍速）

AMD显卡: 已测试7000系显卡可运行（测试型号：AMD 7900XT）

注意，Windows仍存一些未知原因导致的闪退问题（集中在APP启动阶段）。如果您启动APP后没有闪退，说明您的环境没有问题，可以放心使用。


### 使用教程
可在[哔哩哔哩](https://www.bilibili.com/video/BV1yn62YjE76/?spm_id_from=333.1387.homepage.video_card.click)观看使用教程（Windows/MacOS通用）。

## 性能
开发望言OCR的核心出发点是优化硬字幕提取的速度。通过将硬字幕提取拆分成”解码“、”检测“、”识别“三个完全并行的阶段，并充分利用AI推理引擎，实现了硬字幕提取速度的大幅提升。

下面是一个性能测试的结果，测试视频为一段45分钟的含有中英双语字幕的mp4视频：（x后面的数字表示能达到几倍速）

| 测试平台 | [VSE](https://github.com/YaoFANGUK/video-subtitle-extractor) | [雨伞OCR](https://apps.apple.com/cn/app/%E9%9B%A8%E4%BC%9E%E8%A7%86%E9%A2%91%E5%AD%97%E5%B9%95%E6%8F%90%E5%8F%96-%E9%9F%B3%E9%A2%91-%E5%BD%95%E9%9F%B3-%E8%A7%86%E9%A2%91%E8%BD%AC%E6%96%87%E5%AD%97%E7%A1%AC%E5%AD%97%E5%B9%95%E6%8F%90%E5%8F%96/id1639976304?mt=12) | **望言OCR** |
| :------: | :------: | :------:  | :------: |
| M1 Macbook Air | x1.6 | x2.4  | **x10.5** |
| M2 Macbook Air | x1.8 | x2.9  | **x14.9** |
| M3 Macbook Pro | x2.1 | x3.5  | **x21.7** |
| NVIDIA RTX 3060（with Intel I5 12400） | x3.3 | x4.2  | **x15.2** |
| NVIDIA RTX 4070（with AMD R7 5800X） | x4.7 | x5.9  | **x24.1** |

您实际运行的速度可能受具体视频、CPU性能和GPU型号的影响，但不会有太多偏差。



## QQ群
如遇使用问题，或有功能建议，欢迎加入QQ群：[960402870](https://qm.qq.com/q/Go5r1mWHuw)

## 修改与定制
如需二次开发，请见[此处教程](custom.md)。


## 鸣谢
PaddleOCR：[https://github.com/PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)

import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import *
import argparse
from .gui_locale import Locale
from subocr import *
import cv2
import json
import platform
import os
from typing import List, Tuple
from paddleocr.tools.infer.utility import init_args
from paddleocr.tools.infer.predict_det import TextDetector

class AppModel:
    def __init__(self, config, cmd_args) -> None:
        self.reset_data()
        self.config = config
        self.cmd_args = cmd_args
        ppocr_det_param_inject(cmd_args, config)
        self.ppocr_detector = TextDetector(cmd_args)

    def reset_data(self):
        # 视频信息
        self.path_video:str = None
        self.start_us = None
        self.end_us = None
        self.video_width = None
        self.video_height = None
        # 当前帧数据
        self.current_us = None
        self.current_decoded_frame:DecodedFrame = None
        self.current_frame_pixmap:QPixmap = None
        self.current_bboxes:List[Tuple[int, int, int, int]] = []
        # 字幕锚点信息
        self.anchors:List[SubtitleAnchor] = []
        self.anchor_colors = [
            QColor(255, 0, 0),    # Color.red
            QColor(0, 0, 255),    # Color.blue
            QColor(0, 128, 128),  # Color.teal
            QColor(128, 0, 128),  # Color.purple
            QColor(255, 255, 0),  # Color.yellow
            QColor(255, 165, 0),  # Color.orange
            QColor(0, 128, 0),    # Color.green
            QColor(255, 192, 203),# Color.pink
            QColor(128, 128, 128),# Color.gray
            QColor(165, 42, 42)   # Color.brown
        ]
        # 后台任务信息
        self.pipeline:SubocrPipeline = None
        self.last_statistics:SubocrPipeline.Statistics = None

    def set_video(self, path_video):
        video_reader = VideoFrameReader(path_video)
        # 探测5帧，获取信息
        for _ in range(5):
            frame = video_reader.produce()
            if frame is None or frame.video_start_us is None or frame.video_end_us is None:
                print("Failed to probe video")
                print(f"probed start_us: {frame.video_start_us}, end_us: {frame.video_end_us}")
                self.reset_data()
                exit(1)
        
        self.path_video = path_video
        self.start_us = frame.video_start_us
        self.end_us = frame.video_end_us
        self.video_width = frame.frame.shape[1]
        self.video_height = frame.frame.shape[0]
        
    def seek_and_read_frame(self, us):
        # seek
        video_reader = VideoFrameReader(self.path_video)
        frame_num = video_reader.frame_count * us // (self.end_us - self.start_us)
        video_reader.cap.set(cv2.CAP_PROP_POS_MSEC, us // 1000)
        # video_reader.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        # num = video_reader.cap.get(cv2.CAP_PROP_POS_FRAMES)

        reorderer = VideoFrameReorderer(video_reader, 10)
        frame:DecodedFrame = None
        while True:
            _frame:DecodedFrame = reorderer.produce()
            if _frame is None:
                break
            frame = _frame
            if _frame.timestamp_us >= us:
                break
        if frame is None:
            print("Failed to seek video")
            self.reset_data()
            exit(1)
        self.current_decoded_frame = frame
        self.current_us = frame.timestamp_us
        self._set_pixmap_from_frame(frame)
    def _set_pixmap_from_frame(self, frame:DecodedFrame):
        # det boxes
        bgr_image = frame.frame.copy()
        ppocr_bboxes, _ = self.ppocr_detector(bgr_image)
        for box in ppocr_bboxes:
            left, top = box[0]
            right, bottom = box[2]
            pt1 = (int(left), int(top))
            pt2 = (int(right), int(bottom))
            cv2.rectangle(bgr_image, pt1, pt2, (255, 255, 255), 2)
        # convert to center_x, center_y, width, height
        self.current_bboxes = []
        for box in ppocr_bboxes:
            left, top = box[0]
            right, bottom = box[2]
            center_x = (left + right) / 2
            center_y = (top + bottom) / 2
            width = right - left
            height = bottom - top
            self.current_bboxes.append((center_x, center_y, width, height))
        # sort by center_y
        self.current_bboxes.sort(key=lambda x: x[1])
        # anchors
        for idx, anchor in enumerate(self.anchors):
            anchor:SubtitleAnchor = anchor
            color = self.anchor_colors[idx]
            color = (color.blue(), color.green(), color.red())
            radius = 5
            cv2.circle(bgr_image, (anchor.center_x, anchor.center_y), radius, color, -1)
            top = anchor.center_y - anchor.height // 2
            bottom = anchor.center_y + anchor.height // 2
            cv2.line(bgr_image, (anchor.center_x, top), (anchor.center_x, bottom), color, 2)
            left = anchor.center_x - radius
            right = anchor.center_x + radius
            cv2.line(bgr_image, (left, top), (right, top), color, 2)
            cv2.line(bgr_image, (left, bottom), (right, bottom), color, 2)
            # anchor bbox
            detected_frame = DetectedFrame(frame, self.current_bboxes)
            bbox = extract_bbox_for_anchor(anchor, detected_frame)
            if bbox is not None:
                left = bbox[0] - bbox[2] / 2
                right = bbox[0] + bbox[2] / 2
                top = bbox[1] - bbox[3] / 2
                bottom = bbox[1] + bbox[3] / 2
                pt1 = (int(left), int(top))
                pt2 = (int(right), int(bottom))
                cv2.rectangle(bgr_image, pt1, pt2, color, 2)
        rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
        height, width, channel = rgb_image.shape
        bytes_per_line = 3 * width
        q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        self.current_frame_pixmap = QPixmap.fromImage(q_image)

    def update_frame_pixmap(self, width, rerender=False)->None:
        if self.path_video is None or self.current_frame_pixmap is None:
            # 绘制占位图片
            if self.current_frame_pixmap is not None and self.current_frame_pixmap.width() == width:
                return
            pixmap = QPixmap(width, width//2)
            pixmap.fill(QColor('black'))
            painter = QPainter(pixmap)
            painter.setPen(QColor('white'))
            painter.setFont(QFont('Arial', 20))
            painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, Locale.TEXT_DROP_VIDEO_HERE)
            painter.end()
            self.current_frame_pixmap = pixmap
        else:
            # 使用已解码的帧
            if self.current_frame_pixmap.width() != width or rerender:
                self._set_pixmap_from_frame(self.current_decoded_frame)
                self.current_frame_pixmap = self.current_frame_pixmap.scaledToWidth(width, Qt.TransformationMode.SmoothTransformation)

    def start_extraction(self, pipeline:SubocrPipeline):
        self.pipeline = pipeline
        self.pipeline.start()
    
class MainWindow(QMainWindow):
    def __init__(self, config, cmd_args) -> None:
        self.config = config
        self.cmd_args = cmd_args
        super().__init__()
        self.setWindowTitle(Locale.APP_NAME)
        screen = self.screen().availableGeometry()
        width = int(screen.width() * 2 / 3)
        height = int(min(screen.height() * 2 / 3, width))
        self.setGeometry(
            (screen.width() - width) // 2,
            (screen.height() - height) // 2,
            width,
            height
        )


        # split layout
        self.splitter = QSplitter(self)
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.splitter.setContentsMargins(10,10,10,10)
        self.splitter.splitterMoved.connect(self.update_model_view)
        self.setCentralWidget(self.splitter)
        
        
        # main scroll view 
        self.main_scroll_area = QScrollArea()
        self.main_scroll_area.setStyleSheet("QScrollArea { border: 1px solid gray; }")
        self.splitter.addWidget(self.main_scroll_area)
        self.main_widget = QWidget()
        self.main_scroll_area.setWidget(self.main_widget)
        self.main_scroll_area.setWidgetResizable(True)
        self.main_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)


        # layout
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(10, 10, 10, 10)

        # image view
        self.image_view = QLabel(self.main_widget)
        self.image_view.setContentsMargins(0, 0, 0, 0)
        # self.image_view.setText(Locale.TEXT_DROP_VIDEO_HERE)
        # self.image_view.setStyleSheet("padding: 10px; border: 1px solid black;")
        # self.image_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.image_view)
        layout.addItem(QSpacerItem(0, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        # timestamp layout(current, slider, total)
        self.timestamp_layout = QHBoxLayout()
        layout.addLayout(self.timestamp_layout)
        # current
        self.timestamp_label_current = QLabel("00:00", self.main_widget)
        self.timestamp_layout.addWidget(self.timestamp_label_current)
        # slider
        self.timestamp_slider = QSlider(Qt.Orientation.Horizontal)
        self.timestamp_slider.setRange(0, 100)
        self.timestamp_layout.addWidget(self.timestamp_slider)
        self.timestamp_slider.valueChanged.connect(self.on_slider_value_changed)
        # total
        self.timestamp_label_total = QLabel("00:00", self.main_widget)
        self.timestamp_layout.addWidget(self.timestamp_label_total)


        # control buttons
        self.btn_layout = QHBoxLayout()
        layout.addLayout(self.btn_layout)
        # begin button
        self.btn_begin = QPushButton(Locale.BUTTON_BEGIN, self.main_widget)
        self.btn_begin.setStyleSheet("""
            QPushButton {
            background-color: blue;
            color: white;
            }
            QPushButton:pressed {
            background-color: darkblue;
            color: white;
            }
            QPushButton:disabled {
            background-color: lightblue;
            color: gray;
            }
        """)
        
        self.btn_layout.addWidget(self.btn_begin)
        self.btn_begin.clicked.connect(self.on_btn_begin)
        # add anchor button
        self.btn_add_anchor = QPushButton(Locale.BUTTON_ADD_ANCHOR, self.main_widget)
        self.btn_layout.addWidget(self.btn_add_anchor)
        self.btn_add_anchor.clicked.connect(self.on_btn_add_anchor)
        # generate anchors button
        self.btn_generate_anchors = QPushButton(Locale.BUTTON_GENERATE_ANCHORS, self.main_widget)
        self.btn_layout.addWidget(self.btn_generate_anchors)
        self.btn_generate_anchors.clicked.connect(self.on_btn_generate_anchors)
        # spacer
        self.btn_layout.addItem(QSpacerItem(20, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))
        # FPS label and spin
        self.label_fps = QLabel(Locale.TEXT_FPS, self.main_widget)
        self.btn_layout.addWidget(self.label_fps)
        self.spin_fps = QSpinBox(self.main_widget)
        self.spin_fps.setMinimumWidth(80)
        self.spin_fps.setMinimum(1)
        self.spin_fps.setMaximum(120)
        self.spin_fps.setValue(10)
        # self.spin_fps.setSuffix(Locale.TEXT_FPS)
        self.btn_layout.addWidget(self.spin_fps)
        # spacer
        self.btn_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # anchor list
        self.anchor_layout = QVBoxLayout()
        layout.addLayout(self.anchor_layout)


        # splitter spacer
        layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # caption list
        self.caption_list = QListWidget()
        self.splitter.addWidget(self.caption_list)

        self.splitter.setSizes([width * 2 // 3, width // 3])

        self.model:AppModel = AppModel(config=self.config, cmd_args=self.cmd_args)
        timer = QTimer(self)
        timer.timeout.connect(self.update_model_view)
        timer.start(0)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        files = [url.toLocalFile() for url in event.mimeData().urls()]
        self.on_new_video(files[0])

    def resizeEvent(self, event: QResizeEvent):
        self.update_model_view()

    def on_slider_value_changed(self, value):
        if self.model.start_us is None or self.model.end_us is None:
            return
        us = int(self.model.start_us + (self.model.end_us - self.model.start_us) * value / 100)
        self.model.seek_and_read_frame(us)
        self.update_model_view()
    
    def on_btn_begin(self):
        # check anchor validity
        if len(self.model.anchors) == 0:
            QMessageBox.critical(self, Locale.WARNING_TITLE_NO_ANCHOR, Locale.WARNING_CONTENT_NO_ANCHOR)
            return
        for anchor in self.model.anchors:
            s_anchor = f"{Locale.TEXT_ANCHOR_X}({anchor.center_x}), {Locale.TEXT_ANCHOR_Y}({anchor.center_y}), {Locale.TEXT_ANCHOR_HEIGHT}({anchor.height})"
            if anchor.center_x < 0 or anchor.center_x >= self.model.video_width:
                s = f"'{s_anchor}' {Locale.TEXT_ANCHOR_X} {Locale.WARNING_CONTENT_ANCHOR_ATTR_EXCEED} [0, {self.model.video_width})]"
                QMessageBox.critical(self, Locale.WARNING_TITLE_ANCHOR_ATTR_EXCEED, s)
                return
            if anchor.center_y < 0 or anchor.center_y >= self.model.video_height:
                s = f"'{s_anchor}' {Locale.TEXT_ANCHOR_Y} {Locale.WARNING_CONTENT_ANCHOR_ATTR_EXCEED} [0, {self.model.video_height})]"
                QMessageBox.critical(self, Locale.WARNING_TITLE_ANCHOR_ATTR_EXCEED, s)
                return
        # disable all buttons and spins
        def disable_input(widget:QWidget):
            for child in widget.findChildren(QWidget):
                if isinstance(child, (QPushButton, QSpinBox, QCheckBox, QComboBox)):
                    child.setDisabled(True)
                # 递归处理子控件
                disable_input(child)
        disable_input(self.main_widget)
        # start pipeline
        fps = self.spin_fps.value()
        pipeline = SubocrPipeline(self.model.path_video, fps, self.model.anchors, self.config, self.cmd_args)
        self.model.start_extraction(pipeline)
        # progress information
        progress_layout = QHBoxLayout()
        self.lbl_done = QLabel(us2mmss(0), self.main_widget)
        progress_layout.addWidget(self.lbl_done)
        self.progress_bar = QProgressBar(self.main_widget)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        self.lbl_total = QLabel(us2mmss(0), self.main_widget)
        progress_layout.addWidget(self.lbl_total)
        progress_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))
        self.lbl_speedup = QLabel("x0.0", self.main_widget)
        progress_layout.addWidget(self.lbl_speedup)
        progress_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum))

        widget = QWidget()
        widget.setLayout(progress_layout)
        layout:QVBoxLayout = self.main_widget.layout()
        idx = self.main_widget.layout().indexOf(self.btn_layout)
        self.main_widget.layout().insertWidget(idx + 1, widget)

        
        
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.on_progress_timer)
        self.progress_timer.start(500)

    def on_progress_timer(self):
        statistics = self.model.pipeline.query()
        # done label
        self.lbl_done.setText(us2mmss(statistics.done_us))
        # total label
        self.lbl_total.setText(us2mmss(statistics.total_us))
        # progress bar
        done_pct = int(statistics.done_us * 100 / statistics.total_us)
        self.progress_bar.setValue(done_pct)
        # speedup label
        speedup = statistics.speed_up
        self.lbl_speedup.setText(f"x{speedup:.1f}")
        # caption list
        captions = statistics.captions
        last_captions = self.model.last_statistics.captions if self.model.last_statistics is not None else []
        self.model.last_statistics = statistics
        for i in range(len(last_captions), len(captions)):
            separator_item = QListWidgetItem()
            separator_item.setFlags(Qt.ItemFlag.NoItemFlags)  # 禁用选择和交互
            separator_item.setBackground(QColor(200, 200, 200))  # 设置背景颜色
            separator_item.setSizeHint(QSize(0, 3))  # 设置高度
            self.caption_list.addItem(separator_item)

            caption = captions[i]
            item = QListWidgetItem()
            item.setText(f"{us2mmss(caption.start_us)}  =>  {us2mmss(caption.end_us)}")
            for text in caption.caption:
                item.setText(item.text() + f"\n{text}")
            self.caption_list.addItem(item)
        # check finished
        if statistics.is_finished:
            self.progress_timer.stop()
            self.lbl_done.setText(us2mmss(statistics.total_us))
            self.progress_bar.setValue(100)
            dir_output = "output"
            if not os.path.exists(dir_output):
                os.makedirs(dir_output)
            idx = 0
            while True:
                path = os.path.join(dir_output, f"output_{idx}.srt")
                if not os.path.exists(path):
                    break
                idx += 1
            path = os.path.abspath(path)
            self.model.pipeline.export_srt(path)
            QMessageBox.information(self, Locale.WARNING_TITLE_EXPORT_FINISHED, f"{Locale.WARNING_CONTENT_EXPORT_FINISHED} {path}")
            

        

    # 添加/生成anchor
    def on_btn_add_anchor(self):
        if self.model.video_width is None:
            return
        if len(self.model.anchors) >= len(self.model.anchor_colors):
            QMessageBox.critical(self, Locale.WARNING_TITLE_TOO_MANY_ANCHORS, Locale.WARNING_CONTENT_TOO_MANY_ANCHORS)
            return
        anchor = SubtitleAnchor(self.model.video_width//2, self.model.video_height//2, self.model.video_width//10, SubtitleLanguage.ZH, True)
        self.model.anchors.append(anchor)
        self.update_anchor_widgets()    
    def on_btn_generate_anchors(self):
        if self.model.current_bboxes is None:
            return
        for bbox in self.model.current_bboxes:
            if len(self.model.anchors) >= len(self.model.anchor_colors):
                QMessageBox.critical(self, Locale.WARNING_TITLE_TOO_MANY_ANCHORS, Locale.WARNING_CONTENT_TOO_MANY_ANCHORS)
                break
            center_x, center_y, width, height = bbox
            anchor = SubtitleAnchor(round(center_x), round(center_y), round(height), SubtitleLanguage.ZH, True)
            self.model.anchors.append(anchor)
        self.update_anchor_widgets()

    # 单个anchor的相关操作
    def on_spin_anchor_x(self):
        spin:QSpinBox = self.sender()
        idx = self.get_action_anchor_idx()
        self.model.anchors[idx].center_x = spin.value()
        self.update_model_view(rerender_image=True)
    def on_spin_anchor_y(self):
        spin:QSpinBox = self.sender()
        idx = self.get_action_anchor_idx()
        self.model.anchors[idx].center_y = spin.value()
        self.update_model_view(rerender_image=True)
    def on_spin_anchor_height(self):
        spin:QSpinBox = self.sender()
        idx = self.get_action_anchor_idx()
        self.model.anchors[idx].height = spin.value()
        self.update_model_view(rerender_image=True)
    def on_select_anchor_lang(self):
        combo:QComboBox = self.sender()
        idx = self.get_action_anchor_idx()
        self.model.anchors[idx].lang = list(SubtitleLanguage)[combo.currentIndex()]
    def on_checkbox_anchor_primary(self):
        checkbox:QCheckBox = self.sender()
        idx = self.get_action_anchor_idx()
        self.model.anchors[idx].is_primary = checkbox.isChecked()
    def on_btn_remove_anchor(self):
        idx = self.get_action_anchor_idx()
        self.model.anchors.pop(idx)
        self.update_anchor_widgets()
    def get_action_anchor_idx(self):
        widget = self.sender().parent()
        idx = self.anchor_layout.indexOf(widget)
        return idx

    def update_anchor_widgets(self):
        for i in reversed(range(self.anchor_layout.count())): 
            widget = self.anchor_layout.itemAt(i).widget()
            if widget is not None: 
                widget.deleteLater()
        for idx, anchor in enumerate(self.model.anchors):
            anchor:SubtitleAnchor = anchor
            widget = QWidget()
            layout = QHBoxLayout()
            widget.setLayout(layout)
            widget.setContentsMargins(0,0,0,0)
            # color rect
            color = self.model.anchor_colors[self.model.anchors.index(anchor)]
            rect = QLabel(self)
            rect.setFixedWidth(40)
            rect.setFixedHeight(20)
            rect.setStyleSheet(f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});")
            layout.addWidget(rect)
            layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            # x label and spin
            x_label = QLabel(Locale.TEXT_ANCHOR_X)
            layout.addWidget(x_label)
            x_spin = QSpinBox()
            x_spin.setMinimumWidth(100)
            x_spin.setMinimum(0)
            x_spin.setMaximum(self.model.video_width)
            x_spin.setValue(anchor.center_x)
            x_spin.valueChanged.connect(self.on_spin_anchor_x)
            layout.addWidget(x_spin)
            layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            # y label and spin
            y_label = QLabel(Locale.TEXT_ANCHOR_Y)
            layout.addWidget(y_label)
            y_spin = QSpinBox()
            y_spin.setMinimumWidth(100)
            y_spin.setMinimum(0)
            y_spin.setMaximum(self.model.video_height)
            y_spin.setValue(anchor.center_y)
            y_spin.valueChanged.connect(self.on_spin_anchor_y)
            layout.addWidget(y_spin)
            layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            # height label and input
            height_label = QLabel(Locale.TEXT_ANCHOR_HEIGHT)
            layout.addWidget(height_label)
            height_spin = QSpinBox()
            height_spin.setMinimumWidth(80)
            height_spin.setMinimum(0)
            height_spin.setMaximum(self.model.video_height)
            height_spin.setValue(anchor.height)
            height_spin.valueChanged.connect(self.on_spin_anchor_height)
            layout.addWidget(height_spin)
            layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            # language label and selection
            lang_label = QLabel(Locale.TEXT_LANG_SELECT)
            layout.addWidget(lang_label)
            lang_combo = QComboBox()
            for lang in SubtitleLanguage:
                lang_combo.addItem(lang_2_locale(lang))
            lang_combo.setCurrentText(lang_2_locale(anchor.lang))
            lang_combo.setMinimumSize(60, 20)
            lang_combo.currentIndexChanged.connect(self.on_select_anchor_lang)
            layout.addWidget(lang_combo)
            layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            # primary checkbox
            primary_checkbox = QCheckBox(Locale.TEXT_ANCHOR_IS_PRIMARY)
            primary_checkbox.setChecked(anchor.is_primary)
            primary_checkbox.stateChanged.connect(self.on_checkbox_anchor_primary)
            layout.addWidget(primary_checkbox)
            layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            # delete button
            btn = QPushButton(Locale.BUTTON_REMOVE_ANCHOR, widget)
            btn.setStyleSheet("color: red;")
            btn.clicked.connect(self.on_btn_remove_anchor)
            layout.addWidget(btn)
            layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            self.anchor_layout.addWidget(widget)
        self.update_model_view(rerender_image=True)

    def on_new_video(self, video_path):
        if not is_video_valid(video_path):
            file_name = video_path.split('/')[-1]
            QMessageBox.critical(self, Locale.WARNING_TITLE_INVALID_VIDEO, f"'{file_name}' {Locale.WARNING_CONTENT_INVALID_VIDEO}")
            return
        self.model.set_video(video_path)
        self.timestamp_slider.setValue(0)
        self.on_slider_value_changed(0)
        
        

    def update_model_view(self, rerender_image=False):
        self.main_widget.setFixedWidth(self.main_scroll_area.width())
        # image view
        self.model.update_frame_pixmap(self.image_view.width(), rerender_image)
        pixmap = self.model.current_frame_pixmap
        self.image_view.setFixedHeight(pixmap.height())
        self.image_view.setPixmap(pixmap)
        # timestamp
        current_us = self.model.current_us if self.model.current_us is not None else 0
        total_us = self.model.end_us - self.model.start_us if self.model.end_us is not None else 0
        self.timestamp_label_current.setText(us2mmss(current_us, need_ms=False))
        self.timestamp_label_total.setText(us2mmss(total_us, need_ms=False))

        pass

def lang_2_locale(lang:SubtitleLanguage):
    if lang == SubtitleLanguage.ZH:
        return Locale.TEXT_LANG_ZH
    elif lang == SubtitleLanguage.EN:
        return Locale.TEXT_LANG_EN
    elif lang == SubtitleLanguage.JA:
        return Locale.TEXT_LANG_JA
    elif lang == SubtitleLanguage.KO:
        return Locale.TEXT_LANG_KO
    else:
        print(f"Unsupported language: {lang}")
        exit(1)


def subocr_gui_main():
    parser = init_args()
    parser.add_argument("-l", "--lang", help="language", default="zh")
    parser.add_argument("-c", "--config", help="config file", default="./config.json")
    args = parser.parse_args()
    args.use_gpu = True
    if platform.system() == 'Darwin':
        args.use_gpu = False

    lang = args.lang
    if lang == "zh":
        Locale.load_locale_zh()
    elif lang == "en":
        Locale.load_locale_en()
    else:
        print(f"Unsupported language: '{lang}'")
        exit(1)
    with open(args.config, 'r') as f:
        config = json.load(f)
    app = QApplication(sys.argv)
    window = MainWindow(config=config, cmd_args=args)
    window.show()
    sys.exit(app.exec())


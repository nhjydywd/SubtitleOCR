


class Locale:
    APP_NAME = ""

    WARNING_TITLE_INVALID_VIDEO = ""
    WARNING_CONTENT_INVALID_VIDEO = ""

    WARNING_TITLE_TOO_MANY_ANCHORS = ""
    WARNING_CONTENT_TOO_MANY_ANCHORS = ""

    WARNING_TITLE_NO_ANCHOR = ""
    WARNING_CONTENT_NO_ANCHOR = ""

    WARNING_TITLE_ANCHOR_ATTR_EXCEED = ""
    WARNING_CONTENT_ANCHOR_ATTR_EXCEED = ""

    WARNING_TITLE_EXPORT_FINISHED = ""
    WARNING_CONTENT_EXPORT_FINISHED = ""

    TEXT_DROP_VIDEO_HERE = ""
    TEXT_FPS = ""

    TEXT_ANCHOR_X = ""
    TEXT_ANCHOR_Y = ""
    TEXT_ANCHOR_HEIGHT = ""
    TEXT_ANCHOR_IS_PRIMARY = ""

    TEXT_LANG_SELECT = ""
    TEXT_LANG_ZH = ""
    TEXT_LANG_EN = ""
    TEXT_LANG_JA = ""
    TEXT_LANG_KO = ""

    BUTTON_BEGIN = ""
    BUTTON_ADD_ANCHOR = ""
    BUTTON_GENERATE_ANCHORS = ""
    BUTTON_REMOVE_ANCHOR = ""


    def _reset_locale():
        for attr_name in dir(Locale):
            if not attr_name.startswith('__') and not callable(getattr(Locale, attr_name)):
                setattr(Locale, attr_name, "")

    def _check_integrity():
        for attr_name in dir(Locale):
            if not attr_name.startswith('__') and not callable(getattr(Locale, attr_name)):
                if getattr(Locale, attr_name) == "":
                    print(f"Local missing: '{attr_name}' is not set")
                    exit(1)

    def locale(func):
        def wrapper(*args, **kwargs):
            Locale._reset_locale()
            func(*args, **kwargs)
            Locale._check_integrity()
        return wrapper

    @locale
    def load_locale_zh():
        Locale.APP_NAME = "望言OCR"

        Locale.WARNING_TITLE_INVALID_VIDEO = "错误"
        Locale.WARNING_CONTENT_INVALID_VIDEO = "不是有效的视频文件"

        Locale.WARNING_TITLE_TOO_MANY_ANCHORS = "错误"
        Locale.WARNING_CONTENT_TOO_MANY_ANCHORS = "字幕锚点过多"

        Locale.WARNING_TITLE_NO_ANCHOR = "错误"
        Locale.WARNING_CONTENT_NO_ANCHOR = "必须至少添加一个字幕锚点"

        Locale.WARNING_TITLE_ANCHOR_ATTR_EXCEED = "错误"
        Locale.WARNING_CONTENT_ANCHOR_ATTR_EXCEED = "超出范围: "

        Locale.WARNING_TITLE_EXPORT_FINISHED = "提示"
        Locale.WARNING_CONTENT_EXPORT_FINISHED = "已将srt格式字幕导出到："


        Locale.TEXT_DROP_VIDEO_HERE = "将视频拖拽到此处"
        Locale.TEXT_FPS = "检测FPS"

        Locale.TEXT_ANCHOR_X = "X"
        Locale.TEXT_ANCHOR_Y = "Y"
        Locale.TEXT_ANCHOR_HEIGHT = "高度"
        Locale.TEXT_ANCHOR_IS_PRIMARY = "主字幕"

        Locale.TEXT_LANG_SELECT = "语言"
        Locale.TEXT_LANG_ZH = "中文"
        Locale.TEXT_LANG_EN = "英语"
        Locale.TEXT_LANG_JA = "日语"
        Locale.TEXT_LANG_KO = "韩语"

        Locale.BUTTON_BEGIN = "开始提取"
        Locale.BUTTON_ADD_ANCHOR = "添加字幕锚点"
        Locale.BUTTON_GENERATE_ANCHORS = "一键生成字幕锚点"
        Locale.BUTTON_REMOVE_ANCHOR = "删除"

    @locale
    def load_locale_en():
        Locale.APP_NAME = "SubtitleOCR"

        Locale.WARNING_TITLE_INVALID_VIDEO = "Error"
        Locale.WARNING_CONTENT_INVALID_VIDEO = "is not a valid video file"

        Locale.WARNING_TITLE_TOO_MANY_ANCHORS = "Error"
        Locale.WARNING_CONTENT_TOO_MANY_ANCHORS = "Too many anchors"

        Locale.WARNING_TITLE_NO_ANCHOR = "Error"
        Locale.WARNING_CONTENT_NO_ANCHOR = "At least one anchor is required"

        Locale.WARNING_TITLE_ANCHOR_ATTR_EXCEED = "Error"
        Locale.WARNING_CONTENT_ANCHOR_ATTR_EXCEED = "exceeds range: "

        Locale.WARNING_TITLE_EXPORT_FINISHED = "Info"
        Locale.WARNING_CONTENT_EXPORT_FINISHED = "Exported to srt format at: "

        Locale.TEXT_DROP_VIDEO_HERE = "Drop video here"
        Locale.TEXT_FPS = "Detect FPS"

        Locale.TEXT_ANCHOR_X = "X"
        Locale.TEXT_ANCHOR_Y = "Y"
        Locale.TEXT_ANCHOR_HEIGHT = "Height"
        Locale.TEXT_ANCHOR_IS_PRIMARY = "Primary"

        Locale.TEXT_LANG_SELECT = "Language"
        Locale.TEXT_LANG_ZH = "Chinese"
        Locale.TEXT_LANG_EN = "English"
        Locale.TEXT_LANG_JA = "Japanese"
        Locale.TEXT_LANG_KO = "Korean"

        Locale.BUTTON_BEGIN = "Begin"
        Locale.BUTTON_ADD_ANCHOR = "Add Anchor"
        Locale.BUTTON_GENERATE_ANCHORS = "Generate Anchors"
        Locale.BUTTON_REMOVE_ANCHOR = "Remove"

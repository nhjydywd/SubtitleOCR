

#ifndef SUBOCR_H
#define SUBOCR_H

#ifdef __cplusplus
extern "C"{
#endif

#ifdef _WIN32
#define EXPORT_API __declspec(dllexport)
#else
#define EXPORT_API 
#endif

#define EXPORT_INT(name) EXPORT_API const int name();
#define DEFINE_INT(name, value) extern "C" EXPORT_API const int name(){ return value; }

#include <stddef.h>
#include <stdint.h>

#define DEFINE_ARRAY_TYPE(T) \
typedef struct { \
    size_t size; \
    T *data; \
} T##Array; \
EXPORT_API T##Array T##ArrayMalloc( size_t size); \
EXPORT_API void T##Array##Free(T##Array array);    \


//DEFINE_ARRAY_TYPE(UChar)
DEFINE_ARRAY_TYPE(uint8_t)



typedef struct BoundingBox{
    int center_x, center_y, width, height;
}BoundingBox;
DEFINE_ARRAY_TYPE(BoundingBox)
int bbox_left(const BoundingBox *bbox);
int bbox_right(const BoundingBox *bbox);
int bbox_top(const BoundingBox *bbox);
int bbox_bottom(const BoundingBox *bbox);

typedef enum SubtitleLanguage{
    LANG_ZH=0,
    LANG_EN,
    LANG_JA,
    LANG_KO
}SubtitleLanguage;
typedef struct SubtitleAnchor{
    int center_x, center_y, height;
    SubtitleLanguage lang;
    int is_primary;
    int avg_width, min_width, mid_width, max_width;
}SubtitleAnchor;
DEFINE_ARRAY_TYPE(SubtitleAnchor)


EXPORT_INT(CV_TYPE_64FC1)
EXPORT_INT(CV_TYPE_32FC1)
EXPORT_INT(CV_TYPE_16FC1)
EXPORT_INT(CV_TYPE_8UC1)
EXPORT_INT(CV_TYPE_8UC3)
EXPORT_INT(CV_TYPE_8UC4)
// EXPORT_API extern const int CV_TYPE_64FC1;
// EXPORT_API extern const int CV_TYPE_32FC1;
// EXPORT_API extern const int CV_TYPE_16FC1;
// EXPORT_API extern const int CV_TYPE_8UC1;
// EXPORT_API extern const int CV_TYPE_8UC3;
// EXPORT_API extern const int CV_TYPE_8UC4;



/* OpenCV相关桥接定义 */
typedef struct CVImage{
    void *data;
    int width;
    int height;
    int cv_type;
    int bytes_per_row;
}CVImage;
typedef struct CVColor{
    int r, g, b;
}CVColor;
DEFINE_ARRAY_TYPE(CVColor)

EXPORT_API CVImage cv_image(void *data, int width, int height, int cv_type, int bytes_per_row);

EXPORT_API void cv_copy(CVImage src, CVImage dst);
EXPORT_API void cv_argb_to_bgr(CVImage src, CVImage dst);
EXPORT_API void cv_bgr_to_argb(CVImage src, CVImage dst);

extern const int CV_CVT_BGR2GRAY;
extern const int CV_CVT_GRAY2BGR;
EXPORT_API void cv_convert_color(CVImage src, CVImage dst, int cvtCode);

/* 等比缩放 */
EXPORT_API void cv_resize(CVImage srcImage, CVImage dstImage);
//extern RGB cv_get_anchor_color(int idx);
//extern int cv_get_max_num_anchors();
EXPORT_API void cv_copy(CVImage src, CVImage dst);
EXPORT_API void cv_fp16_to_fp32(CVImage fp16Src, CVImage fp32Dst);

EXPORT_API void debug_imshow(const char *name, CVImage imageARGB);
EXPORT_API void debug_log(const char *msg);


/* 算法核心接口 */
typedef struct SubocrContext SubocrContext;
EXPORT_API SubocrContext *subocr_init(const char *pathModels, const char *pathKeys);
EXPORT_API void subocr_deinit(SubocrContext *ctx);
EXPORT_API BoundingBoxArray subocr_detect(SubocrContext *ctx, CVImage input);
EXPORT_API void subocr_plot_bboxes(CVImage image, BoundingBoxArray bboxes, SubtitleAnchorArray anchors, CVColorArray colors);

// CString
DEFINE_ARRAY_TYPE(char)
typedef charArray CString;
// CString Array
DEFINE_ARRAY_TYPE(CString)
// Subtitle
typedef struct Subtitle{
    int64_t start_us;
    int64_t end_us;
    CStringArray cstringArray;
}Subtitle;
DEFINE_ARRAY_TYPE(Subtitle)
EXPORT_API SubtitleArray subocr_query_new_subtitles(SubocrContext *ctx);

    
EXPORT_API int subocr_start_predet(SubocrContext *ctx, const char *videoPath, int64_t maxSec, SubtitleLanguage defaultLang);
EXPORT_API int subocr_start_pipeline(SubocrContext *ctx, const char *videoPath, int fps, SubtitleAnchorArray anchors, int64_t minSubtitleUs);
EXPORT_API void subocr_stop_all(SubocrContext *ctx);

EXPORT_API SubtitleAnchorArray subocr_query_anchors(SubocrContext *ctx);


typedef struct SubocrProgress{
   int is_finished;
   int64_t start_us;
   int64_t current_us;
   int64_t duration_us;
   double speed_up;
}SubocrProgress;
EXPORT_API SubocrProgress subocr_query_progress(SubocrContext *ctx);

EXPORT_API charArray subocr_encode_png(CVImage image);


#ifdef __cplusplus
}
#endif

#endif

//
//  ffmpeg_decoder.h
//  subocr
//
//  Created by 宁浩鉴 on 2024/10/26.
//

//#define MAX_STR_SIZE 512
#ifndef FFMPEG_DECODER_H
#define FFMPEG_DECODER_H

#ifdef __cplusplus
extern "C" {
#endif

#ifdef _WIN32
#define EXPORT_API __declspec(dllexport)
#else
#define EXPORT_API 
#endif

typedef long long int int64_t;


typedef struct VideoFrameARGB VideoFrameARGB;
// constructor and deconstructor
EXPORT_API VideoFrameARGB *vf_init(const int width, const int height);
EXPORT_API void vf_deinit(VideoFrameARGB *f);
// data
EXPORT_API void *vf_get_data(VideoFrameARGB *f);
EXPORT_API const int vf_get_width(VideoFrameARGB *f);
EXPORT_API const int vf_get_height(VideoFrameARGB *f);
EXPORT_API const int vf_get_bytes_per_row(VideoFrameARGB *f);
EXPORT_API const int64_t vf_get_timestamp_us(VideoFrameARGB *f);
EXPORT_API const int vf_get_eof(VideoFrameARGB *f);    // return 0 if not eof, 1 if eof.
EXPORT_API const char * vf_get_error(VideoFrameARGB *f);


typedef struct VideoDecoder VideoDecoder;
// constructor and deconstructor
EXPORT_API VideoDecoder *vd_init(const char *path);
EXPORT_API void vd_deinit(VideoDecoder *dec);
// meta data
EXPORT_API const char *vd_get_path(VideoDecoder *dec);
EXPORT_API const int vd_get_width(VideoDecoder *dec);
EXPORT_API const int vd_get_height(VideoDecoder *dec);
EXPORT_API const int64_t vd_get_start_us(VideoDecoder *dec);
EXPORT_API const int64_t vd_get_duration_us(VideoDecoder *dec);
EXPORT_API const char *vd_get_error(VideoDecoder *dec);
// operation
EXPORT_API void vd_open(VideoDecoder *d, int reorderSize, int targetWidth, int targetHeight);
EXPORT_API void vd_close(VideoDecoder *d);
EXPORT_API void vd_decode(VideoDecoder *d, VideoFrameARGB *f, int64_t minTimestampUs);
EXPORT_API void vd_seek(VideoDecoder *d, int64_t timestampUs);




#ifdef __cplusplus
}
#endif

#endif

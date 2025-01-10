use serde::{Serialize, Deserialize};
use ts_rs::TS;#[repr(C)]
#[derive(Debug, Copy, Clone)]
pub struct uint8_tArray {
    pub size: usize,
    pub data: *mut u8,
}
#[allow(clippy::unnecessary_operation, clippy::identity_op)]
const _: () = {
    ["Size of uint8_tArray"][::std::mem::size_of::<uint8_tArray>() - 16usize];
    ["Alignment of uint8_tArray"][::std::mem::align_of::<uint8_tArray>() - 8usize];
    ["Offset of field: uint8_tArray::size"][::std::mem::offset_of!(uint8_tArray, size) - 0usize];
    ["Offset of field: uint8_tArray::data"][::std::mem::offset_of!(uint8_tArray, data) - 8usize];
};
unsafe extern "C" {
    pub fn uint8_tArrayMalloc(size: usize) -> uint8_tArray;
}
unsafe extern "C" {
    pub fn uint8_tArrayFree(array: uint8_tArray);
}
#[repr(C)]
#[derive(Debug, Copy, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct BoundingBox {
    pub center_x: ::std::os::raw::c_int,
    pub center_y: ::std::os::raw::c_int,
    pub width: ::std::os::raw::c_int,
    pub height: ::std::os::raw::c_int,
}
#[allow(clippy::unnecessary_operation, clippy::identity_op)]
const _: () = {
    ["Size of BoundingBox"][::std::mem::size_of::<BoundingBox>() - 16usize];
    ["Alignment of BoundingBox"][::std::mem::align_of::<BoundingBox>() - 4usize];
    ["Offset of field: BoundingBox::center_x"]
        [::std::mem::offset_of!(BoundingBox, center_x) - 0usize];
    ["Offset of field: BoundingBox::center_y"]
        [::std::mem::offset_of!(BoundingBox, center_y) - 4usize];
    ["Offset of field: BoundingBox::width"][::std::mem::offset_of!(BoundingBox, width) - 8usize];
    ["Offset of field: BoundingBox::height"][::std::mem::offset_of!(BoundingBox, height) - 12usize];
};
#[repr(C)]
#[derive(Debug, Copy, Clone)]
pub struct BoundingBoxArray {
    pub size: usize,
    pub data: *mut BoundingBox,
}
#[allow(clippy::unnecessary_operation, clippy::identity_op)]
const _: () = {
    ["Size of BoundingBoxArray"][::std::mem::size_of::<BoundingBoxArray>() - 16usize];
    ["Alignment of BoundingBoxArray"][::std::mem::align_of::<BoundingBoxArray>() - 8usize];
    ["Offset of field: BoundingBoxArray::size"]
        [::std::mem::offset_of!(BoundingBoxArray, size) - 0usize];
    ["Offset of field: BoundingBoxArray::data"]
        [::std::mem::offset_of!(BoundingBoxArray, data) - 8usize];
};
unsafe extern "C" {
    pub fn BoundingBoxArrayMalloc(size: usize) -> BoundingBoxArray;
}
unsafe extern "C" {
    pub fn BoundingBoxArrayFree(array: BoundingBoxArray);
}
unsafe extern "C" {
    pub fn bbox_left(bbox: *const BoundingBox) -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn bbox_right(bbox: *const BoundingBox) -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn bbox_top(bbox: *const BoundingBox) -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn bbox_bottom(bbox: *const BoundingBox) -> ::std::os::raw::c_int;
}
pub const SubtitleLanguage_LANG_ZH: SubtitleLanguage = 0;
pub const SubtitleLanguage_LANG_EN: SubtitleLanguage = 1;
pub const SubtitleLanguage_LANG_JA: SubtitleLanguage = 2;
pub const SubtitleLanguage_LANG_KO: SubtitleLanguage = 3;
pub type SubtitleLanguage = ::std::os::raw::c_uint;
#[repr(C)]
#[derive(Debug, Copy, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct SubtitleAnchor {
    pub center_x: ::std::os::raw::c_int,
    pub center_y: ::std::os::raw::c_int,
    pub height: ::std::os::raw::c_int,
    pub lang: SubtitleLanguage,
    pub is_primary: ::std::os::raw::c_int,
    pub avg_width: ::std::os::raw::c_int,
    pub min_width: ::std::os::raw::c_int,
    pub mid_width: ::std::os::raw::c_int,
    pub max_width: ::std::os::raw::c_int,
}
#[allow(clippy::unnecessary_operation, clippy::identity_op)]
const _: () = {
    ["Size of SubtitleAnchor"][::std::mem::size_of::<SubtitleAnchor>() - 36usize];
    ["Alignment of SubtitleAnchor"][::std::mem::align_of::<SubtitleAnchor>() - 4usize];
    ["Offset of field: SubtitleAnchor::center_x"]
        [::std::mem::offset_of!(SubtitleAnchor, center_x) - 0usize];
    ["Offset of field: SubtitleAnchor::center_y"]
        [::std::mem::offset_of!(SubtitleAnchor, center_y) - 4usize];
    ["Offset of field: SubtitleAnchor::height"]
        [::std::mem::offset_of!(SubtitleAnchor, height) - 8usize];
    ["Offset of field: SubtitleAnchor::lang"]
        [::std::mem::offset_of!(SubtitleAnchor, lang) - 12usize];
    ["Offset of field: SubtitleAnchor::is_primary"]
        [::std::mem::offset_of!(SubtitleAnchor, is_primary) - 16usize];
    ["Offset of field: SubtitleAnchor::avg_width"]
        [::std::mem::offset_of!(SubtitleAnchor, avg_width) - 20usize];
    ["Offset of field: SubtitleAnchor::min_width"]
        [::std::mem::offset_of!(SubtitleAnchor, min_width) - 24usize];
    ["Offset of field: SubtitleAnchor::mid_width"]
        [::std::mem::offset_of!(SubtitleAnchor, mid_width) - 28usize];
    ["Offset of field: SubtitleAnchor::max_width"]
        [::std::mem::offset_of!(SubtitleAnchor, max_width) - 32usize];
};
#[repr(C)]
#[derive(Debug, Copy, Clone)]
pub struct SubtitleAnchorArray {
    pub size: usize,
    pub data: *mut SubtitleAnchor,
}
#[allow(clippy::unnecessary_operation, clippy::identity_op)]
const _: () = {
    ["Size of SubtitleAnchorArray"][::std::mem::size_of::<SubtitleAnchorArray>() - 16usize];
    ["Alignment of SubtitleAnchorArray"][::std::mem::align_of::<SubtitleAnchorArray>() - 8usize];
    ["Offset of field: SubtitleAnchorArray::size"]
        [::std::mem::offset_of!(SubtitleAnchorArray, size) - 0usize];
    ["Offset of field: SubtitleAnchorArray::data"]
        [::std::mem::offset_of!(SubtitleAnchorArray, data) - 8usize];
};
unsafe extern "C" {
    pub fn SubtitleAnchorArrayMalloc(size: usize) -> SubtitleAnchorArray;
}
unsafe extern "C" {
    pub fn SubtitleAnchorArrayFree(array: SubtitleAnchorArray);
}
unsafe extern "C" {
    pub fn CV_TYPE_64FC1() -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn CV_TYPE_32FC1() -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn CV_TYPE_16FC1() -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn CV_TYPE_8UC1() -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn CV_TYPE_8UC3() -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn CV_TYPE_8UC4() -> ::std::os::raw::c_int;
}
#[repr(C)]
#[derive(Debug, Copy, Clone)]
pub struct CVImage {
    pub data: *mut ::std::os::raw::c_void,
    pub width: ::std::os::raw::c_int,
    pub height: ::std::os::raw::c_int,
    pub cv_type: ::std::os::raw::c_int,
    pub bytes_per_row: ::std::os::raw::c_int,
}
#[allow(clippy::unnecessary_operation, clippy::identity_op)]
const _: () = {
    ["Size of CVImage"][::std::mem::size_of::<CVImage>() - 24usize];
    ["Alignment of CVImage"][::std::mem::align_of::<CVImage>() - 8usize];
    ["Offset of field: CVImage::data"][::std::mem::offset_of!(CVImage, data) - 0usize];
    ["Offset of field: CVImage::width"][::std::mem::offset_of!(CVImage, width) - 8usize];
    ["Offset of field: CVImage::height"][::std::mem::offset_of!(CVImage, height) - 12usize];
    ["Offset of field: CVImage::cv_type"][::std::mem::offset_of!(CVImage, cv_type) - 16usize];
    ["Offset of field: CVImage::bytes_per_row"]
        [::std::mem::offset_of!(CVImage, bytes_per_row) - 20usize];
};
#[repr(C)]
#[derive(Debug, Copy, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct CVColor {
    pub r: ::std::os::raw::c_int,
    pub g: ::std::os::raw::c_int,
    pub b: ::std::os::raw::c_int,
}
#[allow(clippy::unnecessary_operation, clippy::identity_op)]
const _: () = {
    ["Size of CVColor"][::std::mem::size_of::<CVColor>() - 12usize];
    ["Alignment of CVColor"][::std::mem::align_of::<CVColor>() - 4usize];
    ["Offset of field: CVColor::r"][::std::mem::offset_of!(CVColor, r) - 0usize];
    ["Offset of field: CVColor::g"][::std::mem::offset_of!(CVColor, g) - 4usize];
    ["Offset of field: CVColor::b"][::std::mem::offset_of!(CVColor, b) - 8usize];
};
#[repr(C)]
#[derive(Debug, Copy, Clone)]
pub struct CVColorArray {
    pub size: usize,
    pub data: *mut CVColor,
}
#[allow(clippy::unnecessary_operation, clippy::identity_op)]
const _: () = {
    ["Size of CVColorArray"][::std::mem::size_of::<CVColorArray>() - 16usize];
    ["Alignment of CVColorArray"][::std::mem::align_of::<CVColorArray>() - 8usize];
    ["Offset of field: CVColorArray::size"][::std::mem::offset_of!(CVColorArray, size) - 0usize];
    ["Offset of field: CVColorArray::data"][::std::mem::offset_of!(CVColorArray, data) - 8usize];
};
unsafe extern "C" {
    pub fn CVColorArrayMalloc(size: usize) -> CVColorArray;
}
unsafe extern "C" {
    pub fn CVColorArrayFree(array: CVColorArray);
}
unsafe extern "C" {
    pub fn cv_image(
        data: *mut ::std::os::raw::c_void,
        width: ::std::os::raw::c_int,
        height: ::std::os::raw::c_int,
        cv_type: ::std::os::raw::c_int,
        bytes_per_row: ::std::os::raw::c_int,
    ) -> CVImage;
}
unsafe extern "C" {
    pub fn cv_copy(src: CVImage, dst: CVImage);
}
unsafe extern "C" {
    pub fn cv_argb_to_bgr(src: CVImage, dst: CVImage);
}
unsafe extern "C" {
    pub fn cv_bgr_to_argb(src: CVImage, dst: CVImage);
}
unsafe extern "C" {
    pub static CV_CVT_BGR2GRAY: ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub static CV_CVT_GRAY2BGR: ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn cv_convert_color(src: CVImage, dst: CVImage, cvtCode: ::std::os::raw::c_int);
}
unsafe extern "C" {
    pub fn cv_resize(srcImage: CVImage, dstImage: CVImage);
}
unsafe extern "C" {
    pub fn cv_fp16_to_fp32(fp16Src: CVImage, fp32Dst: CVImage);
}
unsafe extern "C" {
    pub fn debug_imshow(name: *const ::std::os::raw::c_char, imageARGB: CVImage);
}
unsafe extern "C" {
    pub fn debug_log(msg: *const ::std::os::raw::c_char);
}
#[repr(C)]
#[derive(Debug, Copy, Clone)]
pub struct SubocrContext {
    _unused: [u8; 0],
}
unsafe extern "C" {
    pub fn subocr_is_preinited(
        pathResources: *const ::std::os::raw::c_char,
    ) -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn subocr_preinit(pathResources: *const ::std::os::raw::c_char);
}
unsafe extern "C" {
    pub fn subocr_init(pathResources: *const ::std::os::raw::c_char, device: ::std::os::raw::c_int) -> *mut SubocrContext;
}
unsafe extern "C" {
    pub fn subocr_deinit(ctx: *mut SubocrContext);
}
unsafe extern "C" {
    pub fn subocr_detect(ctx: *mut SubocrContext, input: CVImage) -> BoundingBoxArray;
}
unsafe extern "C" {
    pub fn subocr_lang_cls(
        ctx: *mut SubocrContext,
        image: CVImage,
        bboxes: BoundingBoxArray,
    ) -> SubtitleAnchorArray;
}
unsafe extern "C" {
    pub fn subocr_plot_bboxes(
        image: CVImage,
        bboxes: BoundingBoxArray,
        anchors: SubtitleAnchorArray,
        colors: CVColorArray,
    );
}
#[repr(C)]
#[derive(Debug, Copy, Clone)]
pub struct charArray {
    pub size: usize,
    pub data: *mut ::std::os::raw::c_char,
}
#[allow(clippy::unnecessary_operation, clippy::identity_op)]
const _: () = {
    ["Size of charArray"][::std::mem::size_of::<charArray>() - 16usize];
    ["Alignment of charArray"][::std::mem::align_of::<charArray>() - 8usize];
    ["Offset of field: charArray::size"][::std::mem::offset_of!(charArray, size) - 0usize];
    ["Offset of field: charArray::data"][::std::mem::offset_of!(charArray, data) - 8usize];
};
unsafe extern "C" {
    pub fn charArrayMalloc(size: usize) -> charArray;
}
unsafe extern "C" {
    pub fn charArrayFree(array: charArray);
}
pub type CString = charArray;
#[repr(C)]
#[derive(Debug, Copy, Clone)]
pub struct CStringArray {
    pub size: usize,
    pub data: *mut CString,
}
#[allow(clippy::unnecessary_operation, clippy::identity_op)]
const _: () = {
    ["Size of CStringArray"][::std::mem::size_of::<CStringArray>() - 16usize];
    ["Alignment of CStringArray"][::std::mem::align_of::<CStringArray>() - 8usize];
    ["Offset of field: CStringArray::size"][::std::mem::offset_of!(CStringArray, size) - 0usize];
    ["Offset of field: CStringArray::data"][::std::mem::offset_of!(CStringArray, data) - 8usize];
};
unsafe extern "C" {
    pub fn CStringArrayMalloc(size: usize) -> CStringArray;
}
unsafe extern "C" {
    pub fn CStringArrayFree(array: CStringArray);
}
#[repr(C)]
#[derive(Debug, Copy, Clone)]
pub struct Subtitle {
    pub start_us: i64,
    pub end_us: i64,
    pub cstringArray: CStringArray,
}
#[allow(clippy::unnecessary_operation, clippy::identity_op)]
const _: () = {
    ["Size of Subtitle"][::std::mem::size_of::<Subtitle>() - 32usize];
    ["Alignment of Subtitle"][::std::mem::align_of::<Subtitle>() - 8usize];
    ["Offset of field: Subtitle::start_us"][::std::mem::offset_of!(Subtitle, start_us) - 0usize];
    ["Offset of field: Subtitle::end_us"][::std::mem::offset_of!(Subtitle, end_us) - 8usize];
    ["Offset of field: Subtitle::cstringArray"]
        [::std::mem::offset_of!(Subtitle, cstringArray) - 16usize];
};
#[repr(C)]
#[derive(Debug, Copy, Clone)]
pub struct SubtitleArray {
    pub size: usize,
    pub data: *mut Subtitle,
}
#[allow(clippy::unnecessary_operation, clippy::identity_op)]
const _: () = {
    ["Size of SubtitleArray"][::std::mem::size_of::<SubtitleArray>() - 16usize];
    ["Alignment of SubtitleArray"][::std::mem::align_of::<SubtitleArray>() - 8usize];
    ["Offset of field: SubtitleArray::size"][::std::mem::offset_of!(SubtitleArray, size) - 0usize];
    ["Offset of field: SubtitleArray::data"][::std::mem::offset_of!(SubtitleArray, data) - 8usize];
};
unsafe extern "C" {
    pub fn SubtitleArrayMalloc(size: usize) -> SubtitleArray;
}
unsafe extern "C" {
    pub fn SubtitleArrayFree(array: SubtitleArray);
}
unsafe extern "C" {
    pub fn subocr_query_new_subtitles(ctx: *mut SubocrContext) -> SubtitleArray;
}
unsafe extern "C" {
    pub fn subocr_start_predet(
        ctx: *mut SubocrContext,
        videoPath: *const ::std::os::raw::c_char,
        maxSec: i64,
        defaultLang: SubtitleLanguage,
    ) -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn subocr_start_pipeline(
        ctx: *mut SubocrContext,
        videoPath: *const ::std::os::raw::c_char,
        fps: ::std::os::raw::c_int,
        anchors: SubtitleAnchorArray,
        minSubtitleUs: i64,
    ) -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn subocr_stop_all(ctx: *mut SubocrContext);
}
unsafe extern "C" {
    pub fn subocr_query_anchors(ctx: *mut SubocrContext) -> SubtitleAnchorArray;
}
#[repr(C)]
#[derive(Debug, Copy, Clone, Serialize, Deserialize, TS)]
#[ts(export)]
pub struct SubocrProgress {
    pub is_finished: ::std::os::raw::c_int,
    pub start_us: i64,
    pub current_us: i64,
    pub duration_us: i64,
    pub speed_up: f64,
}
#[allow(clippy::unnecessary_operation, clippy::identity_op)]
const _: () = {
    ["Size of SubocrProgress"][::std::mem::size_of::<SubocrProgress>() - 40usize];
    ["Alignment of SubocrProgress"][::std::mem::align_of::<SubocrProgress>() - 8usize];
    ["Offset of field: SubocrProgress::is_finished"]
        [::std::mem::offset_of!(SubocrProgress, is_finished) - 0usize];
    ["Offset of field: SubocrProgress::start_us"]
        [::std::mem::offset_of!(SubocrProgress, start_us) - 8usize];
    ["Offset of field: SubocrProgress::current_us"]
        [::std::mem::offset_of!(SubocrProgress, current_us) - 16usize];
    ["Offset of field: SubocrProgress::duration_us"]
        [::std::mem::offset_of!(SubocrProgress, duration_us) - 24usize];
    ["Offset of field: SubocrProgress::speed_up"]
        [::std::mem::offset_of!(SubocrProgress, speed_up) - 32usize];
};
unsafe extern "C" {
    pub fn subocr_query_progress(ctx: *mut SubocrContext) -> SubocrProgress;
}
unsafe extern "C" {
    pub fn subocr_encode_png(image: CVImage) -> charArray;
}
#[repr(C)]
#[derive(Debug, Copy, Clone)]
pub struct InferenceImage {
    _unused: [u8; 0],
}
unsafe extern "C" {
    pub fn infer_image_init(
        width: ::std::os::raw::c_int,
        height: ::std::os::raw::c_int,
    ) -> *mut InferenceImage;
}
unsafe extern "C" {
    pub fn infer_image_deinit(img: *mut InferenceImage);
}
unsafe extern "C" {
    pub fn infer_image_get_cv_image(ii: *mut InferenceImage) -> CVImage;
}
pub const InferenceModelTag_MODEL_DET: InferenceModelTag = 0;
pub const InferenceModelTag_MODEL_LANG_CLS: InferenceModelTag = 1;
pub const InferenceModelTag_MODEL_REC_ZH: InferenceModelTag = 2;
pub const InferenceModelTag_MODEL_REC_EN: InferenceModelTag = 3;
pub const InferenceModelTag_MODEL_REC_JA: InferenceModelTag = 4;
pub const InferenceModelTag_MODEL_REC_KO: InferenceModelTag = 5;
pub type InferenceModelTag = ::std::os::raw::c_uint;
#[repr(C)]
#[derive(Debug, Copy, Clone)]
pub struct InferenceModel {
    _unused: [u8; 0],
}
unsafe extern "C" {
    pub fn infer_model_init(
        baseDir: *const ::std::os::raw::c_char,
        tag: InferenceModelTag,
    ) -> *mut InferenceModel;
}
unsafe extern "C" {
    pub fn infer_model_deinit(m: *mut InferenceModel);
}
unsafe extern "C" {
    pub fn infer_model_inference(
        m: *mut InferenceModel,
        images: *mut *mut InferenceImage,
        outputs: *mut *mut CVImage,
        batch_size: ::std::os::raw::c_int,
        use_batch: ::std::os::raw::c_int,
    );
}
unsafe extern "C" {
    pub static mut INFER_TRT_POSTFIX: *const ::std::os::raw::c_char;
}
unsafe extern "C" {
    pub static mut INFER_ONNX_POSTFIX: *const ::std::os::raw::c_char;
}
unsafe extern "C" {
    pub static mut INFER_DET_MODEL_NAME: *const ::std::os::raw::c_char;
}
unsafe extern "C" {
    pub static INFER_DET_BATCH_SIZE: ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub static INFER_DET_WIDTH: ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub static INFER_DET_HEIGHT: ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn infer_get_det_batch_size() -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn infer_get_det_width() -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn infer_get_det_height() -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub static mut INFER_LANG_CLS_MODEL_NAME: *const ::std::os::raw::c_char;
}
unsafe extern "C" {
    pub static INFER_LANG_CLS_WIDTH: ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub static INFER_LANG_CLS_HEIGHT: ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn infer_get_lang_cls_width() -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn infer_get_lang_cls_height() -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn infer_get_rec_model_name(lang: SubtitleLanguage) -> *const ::std::os::raw::c_char;
}
unsafe extern "C" {
    pub fn infer_get_rec_key_name(lang: SubtitleLanguage) -> *const ::std::os::raw::c_char;
}
unsafe extern "C" {
    pub static mut INFER_REC_KEY_POSTFIX: *const ::std::os::raw::c_char;
}
unsafe extern "C" {
    pub static INFER_REC_WIDTH: ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub static INFER_REC_HEIGHT: ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub static INFER_REC_SCALE_FACTOR: ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn infer_get_rec_width() -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn infer_get_rec_height() -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn infer_get_rec_scale_factor() -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn infer_cal_edit_distance(
        a: *const ::std::os::raw::c_char,
        b: *const ::std::os::raw::c_char,
    ) -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn infer_load_lang_keys(
        baseDir: *const ::std::os::raw::c_char,
        lang: SubtitleLanguage,
    ) -> CString;
}
#[repr(C)]
#[derive(Debug, Copy, Clone)]
pub struct VideoFrame {
    _unused: [u8; 0],
}
unsafe extern "C" {
    pub fn vf_init(width: ::std::os::raw::c_int, height: ::std::os::raw::c_int) -> *mut VideoFrame;
}
unsafe extern "C" {
    pub fn vf_deinit(f: *mut VideoFrame);
}
unsafe extern "C" {
    pub fn vf_get_data(f: *mut VideoFrame) -> *mut ::std::os::raw::c_void;
}
unsafe extern "C" {
    pub fn vf_get_width(f: *mut VideoFrame) -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn vf_get_height(f: *mut VideoFrame) -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn vf_get_bytes_per_row(f: *mut VideoFrame) -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn vf_get_timestamp_us(f: *mut VideoFrame) -> i64;
}
unsafe extern "C" {
    pub fn vf_get_eof(f: *mut VideoFrame) -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn vf_get_error(f: *mut VideoFrame) -> *const ::std::os::raw::c_char;
}
unsafe extern "C" {
    pub fn vf_get_num_channels(f: *mut VideoFrame) -> ::std::os::raw::c_int;
}
#[repr(C)]
#[derive(Debug, Copy, Clone)]
pub struct VideoDecoder {
    _unused: [u8; 0],
}
unsafe extern "C" {
    pub fn vd_init(path: *const ::std::os::raw::c_char) -> *mut VideoDecoder;
}
unsafe extern "C" {
    pub fn vd_deinit(dec: *mut VideoDecoder);
}
unsafe extern "C" {
    pub fn vd_get_path(dec: *mut VideoDecoder) -> *const ::std::os::raw::c_char;
}
unsafe extern "C" {
    pub fn vd_get_width(dec: *mut VideoDecoder) -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn vd_get_height(dec: *mut VideoDecoder) -> ::std::os::raw::c_int;
}
unsafe extern "C" {
    pub fn vd_get_start_us(dec: *mut VideoDecoder) -> i64;
}
unsafe extern "C" {
    pub fn vd_get_duration_us(dec: *mut VideoDecoder) -> i64;
}
unsafe extern "C" {
    pub fn vd_get_error(dec: *mut VideoDecoder) -> *const ::std::os::raw::c_char;
}
unsafe extern "C" {
    pub fn vd_open(
        d: *mut VideoDecoder,
        reorderSize: ::std::os::raw::c_int,
        targetWidth: ::std::os::raw::c_int,
        targetHeight: ::std::os::raw::c_int,
    );
}
unsafe extern "C" {
    pub fn vd_close(d: *mut VideoDecoder);
}
unsafe extern "C" {
    pub fn vd_decode(
        d: *mut VideoDecoder,
        f: *mut VideoFrame,
        minTimestampUs: i64,
        sf: *mut VideoFrame,
    );
}
unsafe extern "C" {
    pub fn vd_seek(d: *mut VideoDecoder, timestampUs: i64);
}
pub type __builtin_va_list = *mut ::std::os::raw::c_char;

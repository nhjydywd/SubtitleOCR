use std::env;
use std::io::Write;
use std::process::{Command, Child};
use std::ptr::{null, null_mut};
use tauri::{path::BaseDirectory, Manager};
use reqwest::Client;
use serde::Serialize;
use serde_json::json;
use std::sync::{Arc, Mutex};
use zip::ZipArchive;
use std::ffi::CString;
use tauri::State;
use base64::{engine::general_purpose, Engine as _};
use ts_rs::TS;
mod subocr_abi;
use subocr_abi::*;

static MTX:Mutex<i32> = Mutex::new(0);
static PATH_RESOURCES: Mutex<String> = Mutex::new(String::new());
static IS_PREINIT_STARTED: Mutex<bool> = Mutex::new(false);
static mut SUBOCR: *mut SubocrContext = std::ptr::null_mut();
static mut DECODER: *mut VideoDecoder = std::ptr::null_mut();
static mut VDWIDTH: i32 = 0;
static mut VDHEIGHT: i32 = 0;


#[tauri::command]
fn is_preinited()->bool{
    return true;
    // let _lock = MTX.lock().expect("Failed to acquire lock");
    // unsafe{
    //     let path_resources = PATH_RESOURCES.lock().unwrap();
    //     let c_str = CString::new(path_resources.clone()).expect("CString::new failed");
    //     let c_str_path_resources = c_str.as_ptr();
    //     let res = subocr_is_preinited(c_str_path_resources);
    //     if res != 0 {
    //         return true;
    //     }else{
    //         return false;
    //     }
    // }
}

#[tauri::command]
fn is_inited()->bool{
    let _lock = MTX.lock().expect("Failed to acquire lock");
    unsafe{
        return SUBOCR != null_mut();
    }
}

#[tauri::command]
fn set_device(device: i32){
    let _lock = MTX.lock().expect("Failed to acquire lock");
    unsafe{
        subocr_deinit(SUBOCR);
        let path_resources = PATH_RESOURCES.lock().unwrap();
        let c_str_path_resources = CString::new(path_resources.clone()).expect("CString::new failed");
        SUBOCR = subocr_init(c_str_path_resources.as_ptr(), device);
    }
}

// #[tauri::command]
// fn start_preinit(){
//     if(*IS_PREINIT_STARTED.lock().unwrap()){
//         return;
//     }
//     *IS_PREINIT_STARTED.lock().unwrap() = true;
//     std::thread::spawn(|| {
//         unsafe{
//             let path_resources = PATH_RESOURCES.lock().unwrap();
//             let c_str_path_resources = CString::new(path_resources.clone()).expect("CString::new failed");
//             subocr_preinit(c_str_path_resources.as_ptr());
//         }
//     });
//     println!("here!!!!!!!!!!!!!!!");
// }

// #[tauri::command]
// fn init(){
//     unsafe{
//         let path_resources = PATH_RESOURCES.lock().unwrap();
//         let c_str_path_resources = CString::new(path_resources.clone()).expect("CString::new failed");
//         SUBOCR = subocr_init(c_str_path_resources.as_ptr());
//     }
// }

#[derive(Serialize, TS)]
#[ts(export)]
struct SetVideoResponse{
    valid: bool,
    width: i32,
    height: i32,
    start_us: f64,
    duration_us: f64,
}
#[tauri::command]
fn set_video(path: &str)->SetVideoResponse{
    let _lock = MTX.lock().expect("Failed to acquire lock");
    unsafe{
        let mut res = SetVideoResponse{
            valid: false,
            width: 0,
            height: 0,
            start_us: 0.0,
            duration_us: 0.0,
        };
        let c_string = CString::new(path).expect("CString::new failed");
        let c_ptr = c_string.as_ptr();
        if DECODER != null_mut(){
            vd_deinit(DECODER);
        }
        DECODER = vd_init(c_ptr);
        let mut err = vd_get_error(DECODER);
        if(*err != 0){
            println!("Error: {err:?}");
            return res;
        }
        VDWIDTH = vd_get_width(DECODER);
        VDHEIGHT = vd_get_height(DECODER);
        println!("Video path:'{path}', width:{VDWIDTH}, height:{VDHEIGHT}");
        vd_open(DECODER, 10, VDWIDTH, VDHEIGHT);
        res.valid = true;
        res.width = VDWIDTH;
        res.height = VDHEIGHT;
        res.start_us = vd_get_start_us(DECODER) as f64;
        res.duration_us = vd_get_duration_us(DECODER) as f64;
        println!("set_video finished!");
        return res;
    }
}

#[derive(Serialize, TS)]
#[ts(export)]
struct GetVideoFrameResponse{
    valid: bool,
    image_b64: String,
    bboxes: Vec<BoundingBox>,
    langs: Vec<SubtitleLanguage>,
}
#[tauri::command]
fn get_video_frame(us:i64, anchors:Vec<SubtitleAnchor>, colors:Vec<CVColor>)->String{
    let _lock = MTX.lock().expect("Failed to acquire lock");
    let mut res = GetVideoFrameResponse{
        valid: false,
        image_b64: "".to_string(),
        bboxes: Vec::new(),
        langs: Vec::new(),
    };
    unsafe{
        if DECODER == null_mut(){
            return json!(res).to_string();
        }
        res.valid = true;


        let frame = vf_init(VDWIDTH, VDHEIGHT);
        vd_seek(DECODER, us);
        vd_decode(DECODER, frame, us, null_mut());
        let image = cv_image(vf_get_data(frame), VDWIDTH, VDHEIGHT, CV_TYPE_8UC3(), vf_get_bytes_per_row(frame));
        let bboxArray = subocr_detect(SUBOCR, image);
        let slice = std::slice::from_raw_parts(bboxArray.data, bboxArray.size as usize);
        let bboxes: Vec<BoundingBox> = slice.to_vec();
        res.bboxes = bboxes;

        let mut anchorArray = SubtitleAnchorArrayMalloc(anchors.len());
        let colorArray = CVColorArrayMalloc(colors.len());
        for i in 0..anchors.len(){
            *anchorArray.data.offset(i as isize) = anchors[i];
            *colorArray.data.offset(i as isize) = colors[i];
        }

        subocr_plot_bboxes(image, bboxArray, anchorArray, colorArray);

        SubtitleAnchorArrayFree(anchorArray);
        anchorArray = subocr_lang_cls(SUBOCR, image, bboxArray);
        for i in 0..anchorArray.size{
            let anchor = *anchorArray.data.offset(i as isize);
            res.langs.push(anchor.lang);
        }

        let png_data = subocr_encode_png(image);
        // let data: Vec<u8> = Vec::from_raw_parts(png_data.data as *mut u8, png_data.size, png_data.size);
        let data = std::slice::from_raw_parts(png_data.data as *const u8, png_data.size);
        let encoded = general_purpose::STANDARD.encode(&data);
        res.image_b64 = "data:image/png;base64,".to_string() + &encoded;

        charArrayFree(png_data);
        CVColorArrayFree(colorArray);
        SubtitleAnchorArrayFree(anchorArray);
        BoundingBoxArrayFree(bboxArray);        
        vf_deinit(frame);
        return json!(res).to_string();
    }
}

#[tauri::command]
fn start_predet(path: &str, max_sec:i64, default_lang: SubtitleLanguage){
    let _lock = MTX.lock().expect("Failed to acquire lock");
    unsafe{
        let c_string = CString::new(path).expect("CString::new failed");
        let c_ptr = c_string.as_ptr();
        subocr_start_predet(SUBOCR, c_ptr, max_sec, default_lang);
    }
}
#[tauri::command]
fn start_pipeline(path: &str, fps: i32, anchors: Vec<SubtitleAnchor>, min_subtitle_us: i64){
    let _lock = MTX.lock().expect("Failed to acquire lock");
    unsafe{
        let c_string = CString::new(path).expect("CString::new failed");
        let c_ptr = c_string.as_ptr();
        let anchorArray = SubtitleAnchorArrayMalloc(anchors.len());
        for i in 0..anchors.len(){
            *anchorArray.data.offset(i as isize) = anchors[i];
        }
        subocr_start_pipeline(SUBOCR, c_ptr, fps, anchorArray, min_subtitle_us);
        SubtitleAnchorArrayFree(anchorArray);
    }
}

#[tauri::command]
fn query_progress()->String{
    let _lock = MTX.lock().expect("Failed to acquire lock");
    unsafe{
        let res = subocr_query_progress(SUBOCR);
        return json!(res).to_string();
    }
}
#[tauri::command]
fn query_anchors()->String{
    let _lock = MTX.lock().expect("Failed to acquire lock");
    unsafe{
        let anchors = subocr_query_anchors(SUBOCR);
        let mut anchor_vec = Vec::new();
        for i in 0..anchors.size {
            anchor_vec.push(*anchors.data.offset(i as isize));
        }
        SubtitleAnchorArrayFree(anchors);
        return json!(anchor_vec).to_string();
    }
}

#[derive(Serialize, TS)]
#[ts(export)]
struct RustSubtitle{
    start_us: f64,
    end_us: f64,
    strs: Vec<String>,
}
#[tauri::command]
fn query_new_subtitles()->String{
    let _lock = MTX.lock().expect("Failed to acquire lock");
    unsafe{
        let subtitles = subocr_query_new_subtitles(SUBOCR);
        let mut vec:Vec<RustSubtitle> = Vec::new();
        for i in 0..subtitles.size {
            let sub = *subtitles.data.offset(i as isize);
            let mut rust_sub = RustSubtitle{
                start_us: sub.start_us as f64,
                end_us: sub.end_us as f64,
                strs: Vec::new(),
            };
            for j in 0..sub.cstringArray.size {
                let cstring = *sub.cstringArray.data.offset(j as isize);
                let data = cstring.data as *mut u8;
                let size = cstring.size;
                let slice = std::slice::from_raw_parts(data, size as usize);
                let str = String::from_utf8(slice.to_vec()).expect("failed to convert cstring to string");
                rust_sub.strs.push(str);
                charArrayFree(cstring);
            }
            vec.push(rust_sub);
            CStringArrayFree(sub.cstringArray);
        }
        SubtitleArrayFree(subtitles);
        return json!(vec).to_string();
    }
}
// #[tauri::command]
// fn get_request(url: &str)->String{
//     let client = reqwest::blocking::Client::new();
//     let res = client.get(url).send().expect("failed to send request");
//     let x = res.status();
//     println!("Status: {}", x);
//     let text = res.text().expect("failed to get msg");
//     return text;
// }

#[tauri::command]
fn write_file(path:&str, content: &str) -> String {
    let mut file = std::fs::File::create(path).expect("failed to create file");
    
    file.write_all(content.as_bytes()).expect("failed to write to file");

    return "".to_string();
}


extern "C" {
    pub fn test_tensorrt();
}


use std::ffi::OsStr;
use std::os::windows::ffi::OsStrExt;
use std::slice;

fn utf8_to_utf16(s: &str) -> Vec<u16> {
    OsStr::new(s).encode_wide().collect()
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
    .setup(move |app| {
    unsafe{
        let path = env::current_exe().expect("Failed to get current executable path");
        let path_resources = path.parent().unwrap().join("alg-resources");
        let str_path_resources = path_resources.to_str()
            .expect("failed to convert path to string")
            .to_string();
        let mut foo = PATH_RESOURCES.lock().unwrap();
        *foo = str_path_resources;
        
        let c_str_path_resources = CString::new((*foo).clone()).expect("CString::new failed");
        SUBOCR = subocr_init(c_str_path_resources.as_ptr(), 0);
        
        // std::thread::spawn(|| {
        //     unsafe{
        //         let str_path:CString;
        //         {
        //             let path_resources = PATH_RESOURCES.lock().unwrap();
        //             str_path = CString::new(path_resources.clone()).expect("CString::new failed");
        //         }
        //         let c_str_path_resources = str_path.as_ptr();
        //         println!("c_str_path_resources: {:?}", c_str_path_resources);
        //         println!("str_path_resources: {:?}", str_path);
        //         if subocr_is_preinited(c_str_path_resources) == 0{
        //             subocr_preinit(c_str_path_resources);
        //         }
        //         SUBOCR = subocr_init(c_str_path_resources);
        //     }
        // });
        println!("\n\n\nsetup finished!\n\n\n");

        // let path_resources = app.path().resolve("alg-resources", BaseDirectory::Resource)
        //     .expect("failed to get alg server resources");
        // let str_path_resources = path_resources.to_str()
        //     .expect("failed to convert path to string");
        // let c_str_path_resources = CString::new(str_path_resources).expect("CString::new failed");
        // SUBOCR = subocr_init(c_str_path_resources.as_ptr());
    };
    Ok(())
    })
    .plugin(tauri_plugin_shell::init())
    .plugin(tauri_plugin_dialog::init())
    .invoke_handler(tauri::generate_handler![ 
        write_file,
        is_preinited, is_inited,
        set_video, get_video_frame,
        start_predet, start_pipeline,
        query_progress, query_anchors, query_new_subtitles])
    .run(tauri::generate_context!())
    .expect("error while running tauri application");
}




// static mut alg_server: Option<Child> = None;



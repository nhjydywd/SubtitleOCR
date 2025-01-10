use std::process;
use std::env;
use std::path::PathBuf;
use std::process::Command;
use std::fs;
use std::fs::File;
use std::io::{self, Read, Write, Seek, SeekFrom};


fn main() {
    let opt_level = env::var("OPT_LEVEL").unwrap_or_default();
    let profile = env::var("PROFILE").unwrap_or_default();
    println!("OPT_LEVEL: {opt_level}");
    println!("PROFILE: {profile}");
    let mut debug = false;
    if opt_level == "0" || profile == "debug" {
        debug = true;
        println!("Debug mode build");
    } else {
        println!("Release mode build");
    }

    let out_dir = env::var("OUT_DIR").unwrap();
    let out_dir = PathBuf::from(out_dir);
    let out_dir = out_dir.parent().unwrap().parent().unwrap().parent().unwrap();
    let out_dir = out_dir.to_str().unwrap();
    println!("OUT_DIR: {}", out_dir);
    
    
    
    
    let mut alg_dir = "C:\\Data\\Codes\\dev\\SubtitleOCR\\subocr-win-cli\\x64\\Debug";
    // 算法库
    if debug{
        alg_dir = "C:\\Data\\Codes\\dev\\SubtitleOCR\\subocr-win-cli\\x64\\Debug";

    }else{
        alg_dir = "C:\\Data\\Codes\\dev\\SubtitleOCR\\subocr-win-cli\\x64\\Release";
        // let alg_release_dir = "C:\\Data\\Codes\\dev\\SubtitleOCR\\SubtitleOCR\\subocr-alg\\build\\Release";
        // println!("cargo:rustc-link-search={}", alg_release_dir);
        // copy_file(format!("{}/subocr.dll", alg_release_dir).as_str(), format!("{}/subocr.dll", out_dir).as_str()).unwrap();
        // println!("cargo:rustc-link-lib=subocr");
    }
    
    println!("cargo-rerun-if-changed={}", alg_dir);
    println!("cargo:rustc-link-search={}", alg_dir);
    println!("cargo:rustc-link-lib=subocr");


    let entries = fs::read_dir(alg_dir).unwrap();
    for entry in entries {
        let entry = entry.unwrap();
        let path = entry.path();
        let path = path.to_str().unwrap();
        let name = entry.file_name();
        let name = name.to_str().unwrap();
        println!("name: {}", name);
        if !name.ends_with("dll") && !name.ends_with("lib"){
            continue;
        }
        copy_file(path, format!("{}/{}", out_dir, name).as_str()).unwrap();
    }

    // dll复制到可执行程序目录
    // if debug{
        // let dir_dll = "libs";
        // println!("cargo-rerun-if-changed={}/", dir_dll);
        // let entries = fs::read_dir(dir_dll).unwrap();
        // for entry in entries {
        //     let entry = entry.unwrap();
        //     let path = entry.path();
        //     let path = path.to_str().unwrap();
        //     let name = entry.file_name();
        //     let name = name.to_str().unwrap();
        //     println!("name: {}", name);
        //     if !name.ends_with("dll"){
        //         continue;
        //     }
        //     copy_file(path, format!("{}/{}", out_dir, name).as_str()).unwrap();
        // }
    // }

    tauri_build::build()
}

fn copy_file(src:&str, dst:&str) -> io::Result<()> {
    println!("copy file from {} to {}", src, dst);
    let mut source_file = File::open(src).unwrap();
    // 创建目标文件
    let mut target_file = File::create(dst).unwrap();


    let mut buffer = [0; 1024]; // 创建一个1024字节的缓冲区
    loop {
        let count = source_file.read(&mut buffer)?;
        if count == 0 {
            break;
        }
        target_file.write_all(&buffer[..count])?;
    }

    Ok(())
}
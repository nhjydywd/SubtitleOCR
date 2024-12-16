//
//  BatchView.swift
//  subocr-macos
//
//  Created by 宁浩鉴 on 2024/11/27.
//

import SwiftUI
import Foundation
import UniformTypeIdentifiers


let WINDOW_ID_BATCH = "batch"
let NAME_ANCHORS_JSON = "subocr.anchor.json"
let POSTFIX_OUT_SRT_POSTFIX = ".subocr.srt"

@Observable
class SubocrTask{
    let path:String
    let jsonPath:String
    let outPath:String
    init?(path:String, jsonPath:String, outPath:String){
        self.path = path
        self.jsonPath = jsonPath
        self.outPath = outPath
        guard let decoder = vd_init(path.cString(using: .utf8)) else{
            print("failed to create decoder!")
            return nil
        }
        defer{vd_deinit(decoder)}
        var err = vd_get_error(decoder)!
        if strlen(err) > 0{
            print("Error: " + String(String(cString: err)))
            return nil
        }
        currentUs = vd_get_start_us(decoder)
        endUs = vd_get_start_us(decoder) + vd_get_duration_us(decoder)
        
    }
    var uiAnchors:[UISubtitleAnchor] = []
    var endUs:Int64 = -1
    var currentUs:Int64 = -1
    var finished = false
    func start(){
        
    }
}

struct BatchView: View{
    @State private var alertNoJson = false
    
    @EnvironmentObject var debug:DebugData
    
    var body:some View{
        VStack{
//            List(Array(subtitles.enumerated()), id: \.offset, selection: $selectedIdx){ idx, subtitle in
//                VStack(alignment: .leading){
//                    Text("\(us2mmss(durationUs: subtitle.startUs, needMs: false))  -->  \(us2mmss(durationUs: subtitle.endUs, needMs: false))")
//                        .font(.footnote)
//                        .foregroundStyle(.gray)
//                        .frame(alignment: .leading)
//                    ForEach(Array(subtitle.strs.enumerated()), id: \.offset){idx, str in
//                        Text(str)
//                            .frame(alignment: .leading)
//                    }
//                    //                ForEach(0..<numAnchors){idx in
//                    //                    Text(subtitle.strs[idx])
//                    //                        .frame(alignment: .leading)
//                    //                }
//                }
//            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        
        .alert("目录中没有\(NAME_ANCHORS_JSON)文件", isPresented: $alertNoJson, actions: {})
        
        .onDrop(of: [.directory], isTargeted: nil){ providers in
            if providers.count <= 0{
                return false
            }
            providers.first?.loadItem(forTypeIdentifier: UTType.directory.identifier, options: nil, completionHandler: { (item, error) in
                guard let url = item as? URL else { return }
                do {
                    let fileManager = FileManager.default
                    let files = try fileManager.contentsOfDirectory(at: url, includingPropertiesForKeys: nil)
                    let filePaths = files.map { $0.path }
                    addDirectory(paths: filePaths)
                } catch {
                    print("读取文件夹内容时出错: \(error)")
                }
            })
            return true
        }
    }
    func addDirectory(paths:[String]){
        // 首先找到字幕锚点信息文件
        print(paths)
    }
    
    static func saveAnchors(url:URL, uiAnchors: [UISubtitleAnchor]){
        
        do {
            let data = try JSONEncoder().encode(uiAnchors)
            try data.write(to: url)
            print("JSON 文件已写入: \(url)")
        } catch {
            print("写入 JSON 文件时出错: \(error)")
        }
    }
    
}

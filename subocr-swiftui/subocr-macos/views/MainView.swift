//
//  MainView.swift
//  subocr
//
//  Created by 宁浩鉴 on 2024/10/26.
//

import SwiftUI
import AVFoundation

import os.log

let MIN_FPS = 1
let MAX_FPS = 999


@MainActor var x = 1
func foo(){
    DispatchQueue.main.sync{
        x = 2
    }
}

@MainActor
public struct MainView: View {
    @EnvironmentObject private var debug:DebugData
    
    @State private var nsImage:NSImage?
    @State private var sliderValue = 0.0
    @State private var fps = max(MIN_FPS, 10)
    @State private var minSubtitleMs = 500
    
    @State private var autoAnalyze = !UserDefaults.standard.bool(forKey: "!autoAnalyze")
    
    @State private var videoPath:String? = nil
    @State private var videoDecoder:OpaquePointer? = nil
    @State private var videoFrame:OpaquePointer? = nil
    @State private var startTimestampUs = Int64(0)
    @State private var currentTimestampUs = Int64(0)
    @State private var totalTimestampUs = Int64(0)
    
    @State private var alertCenterAlign = false
    @State private var alertVideoError = false
    @State private var alertFrameError = false
    @State private var alertZeroAnchors = false
    @State private var alertPredetAlready = false
    @State private var alertPipelineAlready = false
    
    @State private var alertExportFinished = false
    @State private var alertExportFinishedText = ""
    @State private var alertExportFailed = false
    @State private var alertExportFailedText = ""
    

    
    @State private var detectedBBoxes:[BoundingBox] = []

    @State private var uiAnchors:[UISubtitleAnchor] = []
    
    
    
    @Environment(SubocrWrapper.self) private var subocr
    
    // predet stat
    @State private var isProgressHidden = true;
    @State private var isPredetRunning = false
    @State private var subocrTaskName = "分析字幕";
    @State private var subocrStartUs:Int64 = 0
    @State private var subocrCurrentUs:Int64 = 0;
    @State private var subocrDurationUs:Int64 = 0;
    @State private var subocrSpeedUp = 1.0;
    
    @State private var isPipelineRunning = false
    
    @Binding private var uiSubtitles:[UISubtitle]
    @Binding private var selectedUs:Int64
    
    init(subtitles:Binding<[UISubtitle]>, selectedUs:Binding<Int64>){
        _uiSubtitles = subtitles
        _selectedUs = selectedUs
    }
    let timer = Timer.publish(every: 0.5, on: .main, in: .common).autoconnect()
    
    public var body: some View{
        VStack{
            mainScrollView
            Spacer()
            Divider()
            Text("[Github: https://github.com/nhjydywd/SubtitleOCR](https://github.com/nhjydywd/SubtitleOCR)").font(.subheadline)
            Text("[如果本项目对你有帮助，请点一个免费的Star吧~谢谢](https://github.com/nhjydywd/SubtitleOCR)").font(.subheadline)
        }
        .onDrop(of: [.movie], isTargeted: nil){ providers in
            if providers.count <= 0{
                return false
            }
            let type:UTType = .movie
            providers[0].loadItem(forTypeIdentifier: type.identifier){ (data, error) in
                if let url = data as? URL{
                    let path = url.path(percentEncoded: false)
                    print(url, path)
                    DispatchQueue.main.sync{
                        videoPath = path
                    }
                }
            }
            return true
        }
        .onReceive(timer){input in
            updateProgress()
        }
        .alert("视频读取错误", isPresented: $alertVideoError, actions: {})
        .alert("视频帧错误", isPresented: $alertFrameError, actions: {})
        .alert("缺少主字幕", isPresented: $alertZeroAnchors, actions: {}, message: {Text("至少需要有一个主字幕")})
        .alert("分析字幕锚点", isPresented: $alertPredetAlready, actions: {
            Button(action: {startPredet(skipAlert: true)}, label: {Text("确定")})
            Button(action: {}, label: {Text("取消")})
        }, message: {Text("将会清除当前已设置的字幕锚点，是否继续？")})
        .alert("已提取", isPresented: $alertPipelineAlready, actions: {
            Button(action: {startPipeline(skipAlert: true)}, label: {Text("重新提取")})
            Button(action: {}, label: {Text("取消")})
        }, message: {Text("是否要重新提取？")})
        .alert("导出成功", isPresented: $alertExportFinished, actions: {}, message: {Text("已将字幕导出到\(alertExportFinishedText)")})
        .alert("导出失败", isPresented: $alertExportFailed, actions: {}, message: {Text("导出时发生错误: \(alertExportFailedText)")})
    }
    var mainScrollView:some View{
        GeometryReader{ mainSize in
            ScrollView{
                VStack{
                    ZStack{
                        if let image = nsImage{
                            Image(nsImage: image)
                                .resizable()
                                .aspectRatio(contentMode: .fit)
                                .frame(maxWidth: mainSize.size.width, maxHeight: mainSize.size.height-150)
                        }else{
                            Text("将视频拖拽到此处")
                                .font(.largeTitle)
                                .foregroundStyle(.white)
                                .frame(maxWidth: mainSize.size.width, minHeight: min(mainSize.size.width/2, mainSize.size.height-150))
                                .background(.black)
                        }
                    }
                    .padding(.bottom, 5)
                    // seek controls
                    Slider(value: $sliderValue,label: {}, minimumValueLabel: {Text(us2mmss(durationUs: currentTimestampUs, needMs:false))}, maximumValueLabel: {Text(us2mmss(durationUs: totalTimestampUs, needMs: false))}, onEditingChanged: {beforeChange in
                        if beforeChange || videoDecoder==nil{
                            return
                        }
                        currentTimestampUs = vd_get_start_us(videoDecoder) + Int64(Double(vd_get_duration_us(videoDecoder)) * sliderValue)
                    })
                    HStack{
                        Spacer()
                        Button(action: {
                            alterTime(us: -10_000_000)
                        }){
                            Image(systemName: "backward")
                            Text("10S")
                        }
                        Button(action: {
                            alterTime(us: -1_000_000)
                        }){
                            Image(systemName: "arrowtriangle.backward")
                            Text("1S")
                        }
                        Spacer()
                            .frame(maxWidth: 50)
                        Button(action: {
                            alterTime(us: 1_000_000)
                        }){
                            Image(systemName: "arrowtriangle.forward")
                            Text("1S")
                        }
                        Button(action: {
                            alterTime(us: 10_000_000)
                        }){
                            Image(systemName: "forward")
                            Text("10S")
                        }
                        Spacer()
                    }
                    progressHStack
                    // main control buttons
                    HStack{
                        Button(action: {
                            startPipeline()
                        }, label: {
                            Text("开始提取")
                        })
                        .buttonStyle(.borderedProminent)
                        .disabled(videoPath == nil || isPredetRunning || isPipelineRunning)
                        
                        Button(action: {
                            startPredet()
                            
                        }, label: {
                            Text("分析字幕锚点")
                        })
                        .disabled(videoPath == nil || isPredetRunning || isPipelineRunning)
                        
                        Button(action: {
                            appendAnchorsByBBoxes()
                        }, label: {
                            Text("添加字幕锚点")
                        })
                        .disabled(detectedBBoxes.count == 0 || isPredetRunning || isPipelineRunning)
                        Spacer()
                            .frame(maxWidth: 20)
                        Text("FPS")
                        TextField("", value: $fps, formatter: NumberFormatter())
                            .frame(maxWidth: 30)
                        Stepper("", value: $fps)
                        
                        Spacer()
                            .frame(maxWidth: 20)
                        Text("字幕阈值(毫秒)")
                        TextField("", value: $minSubtitleMs, formatter: NumberFormatter())
                            .frame(maxWidth: 40)
                        Stepper("", value: $minSubtitleMs)
                        
                        Spacer()
                            .frame(maxWidth: 20)
                        Toggle(isOn: $autoAnalyze, label: {Text("自动分析")})
                        Spacer()
                    }// HStack alg buttons
                    .onChange(of: fps){
                        fps = max(MIN_FPS, fps)
                        fps = min(MAX_FPS, fps)
                    }
                    .disabled(isPredetRunning || isPipelineRunning)
                    // anchors
                    AnchorView(anchors: $uiAnchors, onAnchorChanged: {updateImage()})
                        .disabled(isPredetRunning || isPipelineRunning)
                    
                    changeHandler
                } // Main VStack
            } // Main ScrollView
            .scrollIndicators(.hidden)
        }
    }
    var progress:Double{
        if(subocrDurationUs > 0){
            return min(Double(subocrCurrentUs - subocrStartUs) / Double(subocrDurationUs), 1)
        }else{
            return 0;
        }
    }
    var progressHStack:some View{
        HStack{
            if(uiSubtitles.count > 0){
                Button("导出SRT", action: {
                    Task{ await exportSrt() }
                })
                .buttonStyle(.borderedProminent)
                .disabled(isPredetRunning || isPipelineRunning)
            }
            Text(subocrTaskName)
            if(isPredetRunning || isPipelineRunning){
                Text("[x\(String(format: "%.2f", subocrSpeedUp))]")
                    .foregroundStyle(.red)
            }else{
                Text("[已完成]")
                    .foregroundStyle(.green)
            }
            Spacer()
                .frame(maxWidth: 10)
            Text(us2mmss(durationUs: subocrCurrentUs))
            ProgressView(value: progress)
            Text(us2mmss(durationUs: subocrStartUs + subocrDurationUs))
            Spacer()
                .frame(maxWidth: 10)

        } // Progress HStack
        .opacity(isProgressHidden ? 0 : 1)
    }
    var changeHandler:some View{
        EmptyView()
            .onChange(of: autoAnalyze){
                UserDefaults.standard.set(!autoAnalyze, forKey: "!autoAnalyze")
            }
//            .onChange(of: autoStart){
//                UserDefaults.standard.set(autoStart, forKey: "autoStart")
//            }

            .onChange(of: videoPath){
                alertCenterAlign = true
                
                isPipelineRunning = false
                isPredetRunning = false
                isProgressHidden = true
                subocr_stop_all(subocr.ctx)
  
                uiSubtitles = []
                uiAnchors = []
                
                nsImage = nil
                if videoDecoder != nil{
                    vd_deinit(videoDecoder)
                    videoDecoder = nil
                }
                videoDecoder = vd_init(videoPath?.cString(using: .utf8))
                var err = vd_get_error(videoDecoder)!
                if strlen(err) > 0{
                    print("Error: " + String(String(cString: err)))
                    alertVideoError = true
                    vd_deinit(videoDecoder)
                    videoDecoder = nil
                    return
                }
                let width = vd_get_width(videoDecoder)
                let height = vd_get_height(videoDecoder)
                startTimestampUs = vd_get_start_us(videoDecoder)
                totalTimestampUs = vd_get_duration_us(videoDecoder)
                vd_open(videoDecoder, 10, width, height)
                err = vd_get_error(videoDecoder)!
                if strlen(err) > 0{
                    print("Error: " + String(String(cString: err)))
                    alertVideoError = true
                    vd_deinit(videoDecoder)
                    videoDecoder = nil
                    return
                }
                
                if videoFrame != nil{
                    vf_deinit(videoFrame)
                    videoFrame = nil
                }
                
                if(currentTimestampUs != startTimestampUs){
                    currentTimestampUs = startTimestampUs
                }else{
                    updateImage()
                }
                if(autoAnalyze){
                    startPredet()
                }
            }
            .onChange(of: currentTimestampUs){
                updateImage()
            }
            .onChange(of: selectedUs){
                currentTimestampUs = selectedUs
                sliderValue = Double(selectedUs - startTimestampUs) / Double(totalTimestampUs)
            }
            .onChange(of: isPredetRunning){
                if(isPredetRunning) {
                    isProgressHidden = false;
                    subocrTaskName = "分析字幕"
                }
            }
            .onChange(of: isPipelineRunning){
                if(isPipelineRunning) {
                    isProgressHidden = false;
                    subocrTaskName = "提取字幕"
                }
            }
    }
//    var alerts:some View{
//        EmptyView()
//
//    }
    func updateImage(){
        if videoDecoder == nil {
            return
        }
        if videoFrame == nil{
            videoFrame = vf_init(vd_get_width(videoDecoder), vd_get_height(videoDecoder))
        }
        let seekUs = min(currentTimestampUs, vd_get_start_us(videoDecoder) + vd_get_duration_us(videoDecoder) - 1)
        vd_seek(videoDecoder, seekUs)
        vd_decode(videoDecoder, videoFrame, currentTimestampUs)
        
        let err = vf_get_error(videoFrame)!;
        if strlen(err) > 0{
            print("Error: " + String(String(cString: err)))
            alertFrameError = true
            return
        }
        if vf_get_eof(videoFrame) != 0{
            return;
        }
        
        let width = vf_get_width(videoFrame)
        let height = vf_get_height(videoFrame)
        let data:UnsafeMutableRawPointer = vf_get_data(videoFrame)
        let bytesPerRow = vf_get_bytes_per_row(videoFrame)
        
        let cvImage = CVImage(data: data, width: width, height: height, cv_type: CV_TYPE_8UC4, bytes_per_row: bytesPerRow)
        
        
        let bboxArray = subocr_detect(subocr.ctx, cvImage)
        defer{ BoundingBoxArrayFree(bboxArray) }
        detectedBBoxes = []
        for i in 0..<bboxArray.size{
            detectedBBoxes.append(bboxArray.data[i])
        }
//        var anchors = convertUIAnchors(uiAnchors: uiAnchors)
//        let anchorData = anchors.withUnsafeMutableBufferPointer(){$0.baseAddress}
//        let inputAnchors = SubtitleAnchorArray(anchors: anchorData, num: Int32(anchors.count))
        let anchors = WrappedSubtitleAnchors(uiAnchors: uiAnchors)
        let colors = WrappedCVColorArray(n: anchors.anchorArray.size)
        subocr_plot_bboxes(cvImage, bboxArray, anchors.anchorArray, colors.colorArray)
//        cv_plot_bboxes(cvImage, detectedBBoxes!, anchors.inputAnchors)
        

        
        guard let colorSpace = CGColorSpace(name: CGColorSpace.sRGB) else{
            print("failed to create colorSpace")
            return
        }
        let bitmapInfo = CGBitmapInfo(rawValue: CGImageAlphaInfo.first.rawValue)

        guard let dataProvider = CGDataProvider(data: NSData(bytes: data, length: Int(height * vf_get_bytes_per_row(videoFrame)))) else{
            print("failed to create data provider")
            return
        }

        guard let cgImage = CGImage(width: Int(width), height: Int(height), bitsPerComponent: 8, bitsPerPixel: 32, bytesPerRow: Int(bytesPerRow), space: colorSpace, bitmapInfo: bitmapInfo, provider: dataProvider, decode: nil, shouldInterpolate: true, intent: .defaultIntent) else{
            print("failed to create cgimage")
            return
        }
        nsImage = NSImage(cgImage: cgImage, size: CGSize(width: cgImage.width, height: cgImage.height))



    }
    func alterTime(us:Int64){
        if videoDecoder == nil{
            return
        }
        currentTimestampUs = max(startTimestampUs, min(currentTimestampUs + us, startTimestampUs + totalTimestampUs))
        sliderValue = Double(currentTimestampUs - startTimestampUs) / Double(totalTimestampUs)
    }
    func appendAnchorsByBBoxes(){
        if detectedBBoxes.count == 0{
            print("detected bboxes is empty!")
            return
        }
        for bbox in detectedBBoxes{
            let uiAnchor = UISubtitleAnchor(centerX: Int(bbox.center_x), centerY: Int(bbox.center_y), height: Int(bbox.height), lang: LANG_ZH.rawValue)
            uiAnchors.append(uiAnchor)
        }
    }
    
    func startPredet(skipAlert:Bool=false){
        if(isPredetRunning || isPipelineRunning){
            print("Can't start predet. isPredetRunning: \(isPredetRunning), isPipelineRunning: \(isPipelineRunning)")
            return
        }
        if(uiAnchors.count > 0 && !skipAlert){
            alertPredetAlready = true
            return
        }
        uiAnchors = []
        if(subocr_start_predet(subocr.ctx, videoPath?.cString(using: .utf8), 1200, LANG_ZH) != 0){
            isPredetRunning = true
        }
    }
    func startPipeline(skipAlert:Bool=false){
        if(isPredetRunning || isPipelineRunning){
            print("Can't start pipeline. isPredetRunning: \(isPredetRunning), isPipelineRunning: \(isPipelineRunning)")
            return
        }
        if(uiSubtitles.count > 0 && !skipAlert){
            alertPipelineAlready = true
            return
        }
        if(fps < 5){
            fps = 5
        }
//        var anchors = convertUIAnchors(uiAnchors: uiAnchors)
        var hasPrimary = false;
        for anchor in uiAnchors{
            if(anchor.isPrimary){
                hasPrimary = true
                break
            }
        }
        if(!hasPrimary){
            alertZeroAnchors = true
            return
        }
        uiSubtitles = []
        let wrappedAnchors = WrappedSubtitleAnchors(uiAnchors: uiAnchors)
//        let anchorData = UnsafeMutablePointer<SubtitleAnchor>.allocate(capacity: anchors.count)
//        let size = anchors.count * MemoryLayout<SubtitleAnchor>.size
//        let _ = anchors.withUnsafeMutableBufferPointer(){
//            memcpy(anchorData, $0.baseAddress, size)
//        }
//        let inputAnchors = SubtitleAnchorArray(anchors: anchorData, num: Int32(anchors.count))
//        debug_log("ui input anchor num: \(inputAnchors.num), data: \(anchorData)".cString(using: .utf8))
//        for i in 0..<inputAnchors.num{
//            let anchor = inputAnchors.anchors[Int(i)]
//            debug_log("ui anchor[\(i)]  x: \(anchor.center_x) y: \(anchor.center_y) height: \(anchor.height)".cString(using: .utf8))
//        }
        let minSubtitleUs = Int64(max(100_000, minSubtitleMs*1000))
        if((subocr_start_pipeline(subocr.ctx, videoPath?.cString(using: .utf8), Int32(fps), wrappedAnchors.anchorArray, minSubtitleUs)) != 0){
            isPipelineRunning = true
        }
//        anchorData.deallocate()
    }
    func updateProgress(){
        if(isPredetRunning){
            let stat = subocr_query_progress(subocr.ctx);
//            print((Double(stat.done_us) / Double(stat.total_us)) * 100.0, stat.speed_up, stat.is_finished);
            subocrStartUs = stat.start_us
            subocrCurrentUs = stat.current_us
            subocrDurationUs = stat.duration_us
            subocrSpeedUp = stat.speed_up;
            if(stat.is_finished == 1){
                subocrCurrentUs = subocrStartUs + subocrDurationUs
                isPredetRunning = false
                let anchors = subocr_query_anchors(subocr.ctx);
                for i in 0..<anchors.size{
                    let anchor = anchors.data[Int(i)];
                    let uiAnchor = UISubtitleAnchor(centerX: Int(anchor.center_x), centerY: Int(anchor.center_y), height: Int(anchor.height), lang: anchor.lang.rawValue)
                    uiAnchor.isPrimary = anchor.is_primary != 0
                    uiAnchors.append(uiAnchor)
                }
//                if(autoStart && autoAnalyze){
//                    startPipeline()
//                }
            }
            
        }else if(isPipelineRunning){
            let stat = subocr_query_progress(subocr.ctx);
            subocrStartUs = stat.start_us
            subocrCurrentUs = stat.current_us
            subocrDurationUs = stat.duration_us
            subocrSpeedUp = stat.speed_up;
            
            let querySubtitles = {
                let subtitleArray = subocr_query_new_subtitles(subocr.ctx);
                for i in 0..<subtitleArray.size{
                    let sub = subtitleArray.data[Int(i)]
                    let startUs = sub.start_us
                    let endUs = sub.end_us
                    var strs:[String] = []
                    for j in 0..<sub.cstringArray.size{
                        let cstring = sub.cstringArray.data[j];
                        strs.append(String(cString: cstring.data))
                        charArrayFree(cstring)
                    }
                    CStringArrayFree(sub.cstringArray)
                    let uiSub = UISubtitle(startUs: startUs, endUs: endUs, strs: strs)
                    self.uiSubtitles.append(uiSub)
                }
                SubtitleArrayFree(subtitleArray)
            }
            querySubtitles()
            if(stat.is_finished == 1){
                subocrCurrentUs = subocrStartUs + subocrDurationUs
                isPipelineRunning = false
                querySubtitles()
            }
        }
    }
    func exportSrt()async{

        
        let savePanel = NSSavePanel()
        
        savePanel.nameFieldStringValue = URL(string: videoPath!)!.deletingPathExtension().appendingPathExtension("srt").lastPathComponent
        savePanel.title = "导出SRT"
        savePanel.prompt = "选择"
        savePanel.message = "请选择要导出的路径"
        savePanel.canCreateDirectories = true
        
        savePanel.begin { (result) in
            if result.rawValue == NSApplication.ModalResponse.OK.rawValue, let url = savePanel.url {
                do{
                    let srt = subtitleToSRT(subtitles: uiSubtitles)
                    try srt.write(to: url, atomically: true, encoding: .utf8)
                    alertExportFinishedText = url.path(percentEncoded: false)
                    alertExportFinished = true
                }catch{
                    alertExportFailedText = error.localizedDescription
                    alertExportFailed = true
                }
            }
        }
    }
    func saveAnchors(){
        let savePanel = NSSavePanel()
        let url = URL(string: videoPath!)!.deletingLastPathComponent().appendingPathComponent(NAME_ANCHORS_JSON)
        savePanel.nameFieldStringValue = url.lastPathComponent
        savePanel.directoryURL = url.deletingLastPathComponent()
        
        savePanel.begin { (result) in
            if result.rawValue == NSApplication.ModalResponse.OK.rawValue, let url = savePanel.url {
                BatchView.saveAnchors(url: url, uiAnchors: uiAnchors)
            }
        }
    }
}

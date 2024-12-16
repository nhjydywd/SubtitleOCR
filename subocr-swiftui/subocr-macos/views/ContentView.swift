//
//  ContentView.swift
//  subocr
//
//  Created by 宁浩鉴 on 2024/10/26.
//

import SwiftUI
import CoreML

@Observable
class UISubtitle{
    init(startUs: Int64, endUs: Int64, strs: [String]) {
        self.startUs = startUs
        self.endUs = endUs
        self.strs = strs
    }
    let startUs:Int64
    let endUs:Int64
    let strs:[String]
}
private func usToSRTTime(us:Int64)->String{
    let totalSeconds = us / 1_000_000 // 转换为秒
    let hours = totalSeconds / 3600
    let minutes = (totalSeconds % 3600) / 60
    let seconds = totalSeconds % 60
    let ms = us % 1_000_000 / 1_000
    return String(format: "%02ld:%02ld:%02ld,%03ld", hours, minutes, seconds, ms)
}
func subtitleToSRT(subtitles:[UISubtitle])->String{
    var res = ""
    var idx = 1
    for sub in subtitles{
        let strStart = usToSRTTime(us: sub.startUs)
        let strEnd = usToSRTTime(us: sub.endUs)
        for str in sub.strs{
            
            res += "\(idx)\n\(strStart) --> \(strEnd)\n\(str)\n\n"
            idx += 1
        }
    }
    return res
}

struct ContentView: View {
    @EnvironmentObject private var debug:DebugData
    @Environment(\.openWindow) private var openWindow
    @State private var initialized = false;
    
    @State var subtitles:[UISubtitle] = []
    @State var selectedUs:Int64 = 0
    
    var body: some View {
        GeometryReader{ geometry in
            HSplitView{
                MainView(subtitles: $subtitles, selectedUs: $selectedUs)
                    .padding(.trailing, 15)
                .frame(minWidth: !initialized ? geometry.size.width/4*3 : 200, maxWidth: .infinity, maxHeight: .infinity)
                .environmentObject(debug)
                SubtitleView(subtitles: subtitles, selectedUs: $selectedUs)
//                SubtitleView(subtitles: $subtitles, selectedUs: $selectedUs)
                    .padding(.leading, 5)
                .frame(minWidth: !initialized ? geometry.size.width/4 : 200, maxWidth: .infinity, maxHeight: .infinity)
            
            } // HSplitView
            .padding()
            .onAppear(){
                test_extern_lib()
                initialized = true
                if(debug.isDebugMode){
                    openWindow(id: WINDOW_ID_DEBUG)
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
    }
}

#Preview {
    ContentView()
}

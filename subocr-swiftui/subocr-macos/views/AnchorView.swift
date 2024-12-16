//
//  AnchorView.swift
//  subocr
//
//  Created by 宁浩鉴 on 2024/10/31.
//

import SwiftUI

func getSubtitleLangStr(lang:SubtitleLanguage)->String{
    switch lang{
    case LANG_ZH:
        return "中文"
    case LANG_EN:
        return "英语"
    case LANG_JA:
        return "日语"
    case LANG_KO:
        return "韩语"
    default:
        print("Unknown lang: \(lang)")
        return "未知语言"
    }
}

@Observable
class UISubtitleAnchor:Codable{
    init(centerX: Int, centerY: Int, height: Int, lang: UInt32) {
        self.centerX = centerX
        self.centerY = centerY
        self.height = height
        self.lang = lang
    }
    var centerX:Int
    var centerY:Int
    var height:Int
    var lang:UInt32
    var isPrimary = false
}

//func convertUIAnchors(uiAnchors:[UISubtitleAnchor])->[SubtitleAnchor]{
//    return uiAnchors.map(){uiAnchor in
//        return SubtitleAnchor(center_x: Int32(uiAnchor.centerX), center_y: Int32(uiAnchor.centerY), height: Int32(uiAnchor.height), lang: SubtitleLanguage(uiAnchor.lang), is_primary: uiAnchor.isPrimary ? 1:0, avg_width: 0, min_width: 0, mid_width: 0, max_width: 0)
//    }
//}

class WrappedSubtitleAnchors{
    let anchorArray:SubtitleAnchorArray
//    let data:UnsafeMutablePointer<SubtitleAnchor>
//    let inputAnchors:SubtitleAnchorArray
    init(uiAnchors:[UISubtitleAnchor]){
        anchorArray = SubtitleAnchorArrayMalloc(uiAnchors.count)
        for i in 0..<uiAnchors.count{
            let uiAnchor = uiAnchors[i]
            let anchor = SubtitleAnchor(center_x: Int32(uiAnchor.centerX), center_y: Int32(uiAnchor.centerY), height: Int32(uiAnchor.height), lang: SubtitleLanguage(rawValue: uiAnchor.lang), is_primary: uiAnchor.isPrimary ? 1:0, avg_width: 0, min_width: 0, mid_width: 0, max_width: 0)
            anchorArray.data[i] = anchor
        }
    }
    deinit{
        SubtitleAnchorArrayFree(anchorArray)
    }
}
class WrappedCVColorArray{
    let colorArray:CVColorArray
    init(n:Int){
        colorArray = CVColorArrayMalloc(n)
        for i in 0..<n{
            let rgb = ANCHOR_RGB[i%ANCHOR_RGB.count]
            let cvColor = CVColor(r: Int32(rgb[0]), g: Int32(rgb[1]), b: Int32(rgb[2]))
            colorArray.data[i] = cvColor
        }
    }
    deinit{
        CVColorArrayFree(colorArray)
    }
}

//const ANCHOR_COLOR = [
//  [255, 0, 0], // Red
//  [0, 0, 255], // Blue
//  [0, 128, 128], // Teal
//  [128, 0, 128], // Purple
//  [255, 255, 0], // Yellow
//  [255, 165, 0], // Orange
//  [0, 128, 0], // Green
//  [255, 192, 203], // Pink
//  [128, 128, 128], //Gray
//  [165, 42, 42], // Brown
//]
let ANCHOR_RGB:[[Int]] = [
    [255, 0, 0], // Red
    [0, 0, 255], // Blue
    [0, 128, 128], // Teal
    [128, 0, 128], // Purple
    [255, 255, 0], // Yellow
    [255, 165, 0], // Orange
    [0, 128, 0], // Green
    [255, 192, 203], // Pink
    [128, 128, 128], //Gray
    [165, 42, 42], // Brown    
]
func getAnchorColor(idx:Int)->Color{
//    let rgb = cv_get_anchor_color(Int32(idx))
    let i = idx % ANCHOR_RGB.count
    let rgb = ANCHOR_RGB[i]
    return Color(red: Double(rgb[0])/255.0, green: Double(rgb[1])/255.0, blue: Double(rgb[2])/255.0)
}
struct AnchorView: View{
    
    @Binding var  anchors:[UISubtitleAnchor]
    let onAnchorChanged:()->Void
    var body: some View{
        VStack{
            ForEach(Array(anchors.enumerated()), id: \.offset){ idx, anchor in
                @Bindable var anchor = anchor
                HStack{
                    Spacer(minLength: 1)
                    Text("字幕\(idx+1)")
                    getAnchorColor(idx: idx).frame(minWidth: 10, maxWidth: 40, maxHeight: 30)
                    Spacer(minLength: 1)
                    
                    Text("x")
                    TextField("", value: $anchor.centerX, format:.number).frame(minWidth: 20, maxWidth: 50)
                    Stepper(value: $anchor.centerX, label: {})
                    Spacer(minLength: 1)
                    
                    Text("y")
                    TextField("", value: $anchor.centerY, format:.number).frame(minWidth: 20,maxWidth: 50)
                    Stepper(value: $anchor.centerY, label: {})
                    Spacer(minLength: 1)
                    
                    Text("高度")
                    TextField("", value: $anchor.height, format:.number).frame(minWidth: 20,maxWidth: 50)
                    Stepper(value: $anchor.height, label: {})
                    Spacer(minLength: 1)
                    
                    Picker("语言", selection: $anchor.lang){
//                        Text("你好").tag(UInt32(0))
//                        Text("你好呀").tag(UInt32(1))
                        ForEach(0..<4, id:\.self){id in
                            Text(getSubtitleLangStr(lang: SubtitleLanguage(UInt32(id)))).tag(UInt32(id))
                        }
                    }.frame(minWidth: 30,maxWidth: 120).layoutPriority(1)
                    Spacer(minLength: 1)
//                    
                    Toggle( isOn: $anchor.isPrimary){
                        Text("主字幕").layoutPriority(2).foregroundStyle(anchor.isPrimary ? .black : .gray)
                    }
                    Spacer(minLength: 1)
                    
                    Button(action: {
                        anchors.remove(at: idx)
                    }, label: {
                        Text("删除").foregroundStyle(.red)
                    })
                    Spacer(minLength: 1)
                } // HStack
                .onChange(of: anchor.centerX){ onAnchorChanged() }
                .onChange(of: anchor.centerY){ onAnchorChanged() }
                .onChange(of: anchor.height){ onAnchorChanged() }
            }
            .onChange(of: anchors.count){
                onAnchorChanged()
            }
        }
    }
}

//
//  DebugView.swift
//  subtitle-extractor
//
//  Created by nhj on 2024/7/1.
//

import Foundation
import SwiftUI


class DebugData:ObservableObject{
    @Published var isDebugMode:Bool
    
    @Published var predetDecodeFrame:NSImage? = nil
    @Published var predetXPlot:NSImage? = nil
    @Published var predetYPlot:NSImage? = nil
    @Published var predetTextImage:NSImage? = nil
    
    @Published var recDetextedImage:NSImage? = nil
    @Published var recClippedTextImage:NSImage? = nil
    @Published var recTextImage:NSImage? = nil
    
    init(isDebugMode:Bool){
        self.isDebugMode = isDebugMode
    }
}

let WINDOW_ID_DEBUG = "debug"

@Observable
class DebugImages{
    var debugImages:Dictionary<String, NSImage> = [:]
};
nonisolated(unsafe) var DEBUG_IMAGES = DebugImages()

@_cdecl("debug_imshow")
func debug_imshow(name:UnsafePointer<CChar>!, imageARGB:CVImage){
    let data = imageARGB.data
    let width = imageARGB.width
    let height = imageARGB.height
    let bytesPerRow = imageARGB.bytes_per_row
    guard let colorSpace = CGColorSpace(name: CGColorSpace.sRGB) else{
        print("failed to create colorSpace")
        return
    }
    let bitmapInfo = CGBitmapInfo(rawValue: CGImageAlphaInfo.first.rawValue)

    guard let dataProvider = CGDataProvider(data: NSData(bytes: data, length: Int(height * bytesPerRow))) else{
        print("failed to create data provider")
        return
    }
    guard let cgImage = CGImage(width: Int(width), height: Int(height), bitsPerComponent: 8, bitsPerPixel: 32, bytesPerRow: Int(bytesPerRow), space: colorSpace, bitmapInfo: bitmapInfo, provider: dataProvider, decode: nil, shouldInterpolate: true, intent: .defaultIntent) else{
        print("failed to create cgimage")
        return
    }
    let nsImage = NSImage(cgImage: cgImage, size: CGSize(width: cgImage.width, height: cgImage.height))
    let key = String(cString: name)
    if(Thread.isMainThread){
        DEBUG_IMAGES.debugImages[key] = nsImage
    }else{
        DispatchQueue.main.sync{
            DEBUG_IMAGES.debugImages[key] = nsImage
        }
    }
}

//@_cdecl("debug_log")
//func debug_log(str: UnsafePointer<CChar>){
//    LOGGER.warning("clog: \(String(cString: str))")
//}

struct DebugView: View{
    @EnvironmentObject var debug:DebugData
    @State var selection = 0
    
    @State var debug_images = DEBUG_IMAGES
    
//    @State var avfoundationURL:URL? = nil
//    @State var isFileImporterPresented = false
    var body:some View{
        NavigationSplitView{
            List(selection: $selection){
                ForEach(DEBUG_IMAGES.debugImages.keys.sorted(),id: \.self){key in
                    NavigationLink{
                        Image(nsImage: DEBUG_IMAGES.debugImages[key]!)
                            .resizable()
                            .scaledToFit()
                    }label:{
                        Text(key)

                    }
                }
            }
            .listStyle(.sidebar)

        }detail: {
            
        }
    }
}



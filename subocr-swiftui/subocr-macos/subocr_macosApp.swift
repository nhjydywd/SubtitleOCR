//
//  subocr_macosApp.swift
//  subocr-macos
//
//  Created by 宁浩鉴 on 2024/11/17.
//

import SwiftUI


@Observable
class SubocrWrapper{
    let ctx = subocr_init("", "")
    deinit{
        subocr_deinit(ctx)
    }
}

@main
struct subocr_macosApp: App {
    @StateObject var debug = DebugData( isDebugMode: true )
    @State var subocr = SubocrWrapper()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .frame(minWidth: 900, minHeight: 600)
        }
        .environmentObject(debug)
        .environment(subocr)
        .commands {
            CommandGroup(replacing: .newItem, addition: { })
        }
//        if(debug.isDebugMode){
//            Window(WINDOW_ID_DEBUG, id: WINDOW_ID_DEBUG){
//                DebugView()
//            }
//            .environmentObject(debug)
//            Window(WINDOW_ID_BATCH, id: WINDOW_ID_BATCH){
//                BatchView()
//            }
//            .environmentObject(debug)
//            Window()
//        }
    }
}

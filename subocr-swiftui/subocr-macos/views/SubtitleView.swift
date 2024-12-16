//
//  Caption.swift
//  subocr
//
//  Created by 宁浩鉴 on 2024/10/26.
//

import SwiftUI

public struct SubtitleView: View {
    private let subtitles:[UISubtitle]
//    @Binding private var subtitles:[UISubtitle]
    
//    @Binding private var numAnchors:Int
    @State private var selectedIdx = -1
    @Binding private var selectedUs:Int64
    init(subtitles: [UISubtitle], selectedUs: Binding<Int64>) {
        self.subtitles = subtitles
        self._selectedUs = selectedUs
    }
    
    
    public var body: some View{
        List(Array(subtitles.enumerated()), id: \.offset, selection: $selectedIdx){ idx, subtitle in
            VStack(alignment: .leading){
                Text("\(us2mmss(durationUs: subtitle.startUs, needMs: false))  -->  \(us2mmss(durationUs: subtitle.endUs, needMs: false))")
                    .font(.footnote)
                    .foregroundStyle(.gray)
                    .frame(alignment: .leading)
                ForEach(Array(subtitle.strs.enumerated()), id: \.offset){idx, str in
                    Text(str)
                        .frame(alignment: .leading)
                }
//                ForEach(0..<numAnchors){idx in
//                    Text(subtitle.strs[idx])
//                        .frame(alignment: .leading)
//                }
            }
        }
        .onChange(of: selectedIdx){
            selectedUs = subtitles[selectedIdx].startUs
        }
    }
}

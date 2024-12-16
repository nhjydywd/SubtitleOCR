//
//  SubViews.swift
//  subocr
//
//  Created by 宁浩鉴 on 2024/10/26.
//
import SwiftUI

func us2mmss(durationUs:Int64, needMs:Bool = false)->String{
    if durationUs <= 0{
        return "00:00"
    }
    let totalSeconds = durationUs / 1_000_000 // 转换为秒
    let hours = totalSeconds / 3600
    let minutes = (totalSeconds % 3600) / 60
    let seconds = totalSeconds % 60
    var res = String(format: "%02ld:%02ld", minutes, seconds)
    if hours > 0{
        res = String(format: "%ld:", hours) + res
    }
    if needMs{
        let ms = durationUs % 1_000_000 / 1_000
        res = res + String(format: ",%03ld", ms)
    }
    return res
}

class FileImported{
    var urls:[URL] = []
    let error:Error?
    let needAccess:Bool
    init(error:Error?, needAccess:Bool){
        self.error = error
        self.needAccess = needAccess
    }
}

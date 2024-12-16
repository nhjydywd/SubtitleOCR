////
////  DebugDecoderView.swift
////  hardcode-subtitle-extractor
////
////  Created by nhj on 2024/9/1.
////
//
//import Foundation
//import SwiftUI
//import AVFoundation
//import CoreML
//
//struct DebugDecoderView:View{
//    @State var ffmpegFrame:NSImage? = nil
//    @State var ffmpegURL:URL? = nil
//    
//    @State var decoderActor = DecoderActor()
//    
//    var body:some View{
//        VStack{
//            if let frame = ffmpegFrame{
//                Image(nsImage: frame)
//                    .resizable()
//            }
//        }
//        .frame(maxWidth: .infinity, maxHeight: .infinity)
//        .background(.black)
//        // vstack
//        .onDrop(of: [.movie], isTargeted: nil){ providers in
//            if providers.count <= 0{
//                return false
//            }
//            let type:UTType = .movie
//            providers[0].loadItem(forTypeIdentifier: type.identifier){ (data, error) in
//                print("loaded!")
//
//                if let url = data as? URL{
//                    
//                    let path = url.path(percentEncoded: false)
//                    print(url, path)
//                    Task{
//                        let startTime = DispatchTime.now()
//                        var lastPrintTime = startTime
//                        var startTimestampUs = Int64(-1)
//                        print("starting decoder....")
//                        await decoderActor.start(videoPath: path, fps: 120, bufferSize: 20)
//                        print("decoder started!")
//                        guard let colorSpace = CGColorSpace(name: CGColorSpace.sRGB) else{
//                            print("failed to create colorSpace")
//                            return
//                        }
//                        let bitmapInfo = CGBitmapInfo(rawValue: CGImageAlphaInfo.first.rawValue)
//                        while(true){
//                            let frame = await decoderActor.buffer.popReadyData()!
//                            
//                            let err = vf_get_error(frame)
//                            guard strlen(err!) == 0 else{
//                                print("frame error: " + String(cString: err!))
//                                await decoderActor.buffer.appendEmptyData(data: frame)
//                                break;
//                            }
//                            if vf_get_eof(frame) != 0{
//                                print("eof reached!")
//                                await decoderActor.buffer.appendEmptyData(data: frame)
//                                break;
//                            }
//                            if startTimestampUs < 0{
//                                startTimestampUs = vf_get_timestamp_us(frame)
//                            }
//                            let currTime = DispatchTime.now()
//                            
//                            if currTime.uptimeNanoseconds - lastPrintTime.uptimeNanoseconds > 1_000_000_000{
//                                lastPrintTime = currTime
//                                let elapsedNs = currTime.uptimeNanoseconds - startTime.uptimeNanoseconds
//                                let finishedUs = vf_get_timestamp_us(frame) - startTimestampUs
//                                let speedup = Double(finishedUs) / Double(elapsedNs/1000)
//                                print(String(format: "speedup: %.2f", speedup))
//                            }
//                            
//                            let width = await decoderActor.width
//                            let height = await decoderActor.height
//                            var dataProvider:CGDataProvider? = nil
//                            let data = vf_get_data(frame)
//    
//                            dataProvider = CGDataProvider(data: NSData(bytes: data, length: Int(height * vf_get_bytes_per_row(frame))))
//    
//                            guard let dataProvider = dataProvider else{
//                                print("failed to create data provider")
//                                return
//                            }
//    
//                            guard let cgImage = CGImage(width: Int(width), height: Int(height), bitsPerComponent: 8, bitsPerPixel: 32, bytesPerRow: Int(vf_get_bytes_per_row(frame)), space: colorSpace, bitmapInfo: bitmapInfo, provider: dataProvider, decode: nil, shouldInterpolate: true, intent: .defaultIntent) else{
//                                print("failed to create cgimage")
//                                return
//                            }
//                            DispatchQueue.main.sync {
//                                ffmpegFrame = NSImage(cgImage: cgImage, size: CGSize(width: cgImage.width, height: cgImage.height))
//                            }
//                            await decoderActor.buffer.appendEmptyData(data: frame)
//                        }
//                        
//                        await decoderActor.stop()
//                    }
//                    // 直接操作下层decoder
////                    let decoder = vd_init(path);
////                    defer{ vd_deinit(decoder)}
////                    
////                    var err = vd_get_error(decoder)
////                    guard strlen(err!) == 0 else{
////                        print("decoder error: " + String(cString: err!))
////                        return;
////                    }
////                    let width = vd_get_width(decoder)
////                    let height = vd_get_height(decoder)
////                    let durationUs = vd_get_duration_us(decoder)
////                    print("width: \(width)", "height: \(height)", "duration: \(durationUs/1_000_000)")
////                    
////                    vd_open(decoder, 10, width, height)
////                    defer{vd_close(decoder)}
////                    err = vd_get_error(decoder)
////                    guard strlen(err!) == 0 else{
////                        print("decoder error: " + String(cString: err!))
////                        return;
////                    }
//                    
//                    
//                    
////                    let frame = vf_init(width, height)
////                    err = vf_get_error(frame)
////                    guard strlen(err!) == 0 else{
////                        print("frame error: " + String(cString: err!))
////                        return;
////                    }
////                    
////                    guard let colorSpace = CGColorSpace(name: CGColorSpace.sRGB) else{
////                        print("failed to create colorSpace")
////                        return
////                    }
////                    let bitmapInfo = CGBitmapInfo(rawValue: CGImageAlphaInfo.first.rawValue)
////
////                    let startTime = DispatchTime.now()
////                    var lastPrintTime = startTime
////                    var startTimestampUs = Int64(-1)
////                    
////                    while(true){
////                        vd_decode(decoder, frame, 0)
////                        err = vf_get_error(frame)
////                        guard strlen(err!) == 0 else{
////                            print("frame error: " + String(cString: err!))
////                            return;
////                        }
////                        if vf_get_eof(frame) != 0{
////                            print("eof reached!")
////                            return;
////                        }
////                        if startTimestampUs < 0{
////                            startTimestampUs = vf_get_timestamp_us(frame)
////                        }
////                        let currTime = DispatchTime.now()
////                        
////                        if currTime.uptimeNanoseconds - lastPrintTime.uptimeNanoseconds > 1_000_000_000{
////                            lastPrintTime = currTime
////                            let elapsedNs = currTime.uptimeNanoseconds - startTime.uptimeNanoseconds
////                            let finishedUs = vf_get_timestamp_us(frame) - startTimestampUs
////                            let speedup = Double(finishedUs) / Double(elapsedNs/1000)
////                            print(String(format: "speedup: %.2f", speedup))
////                        }
////                        var dataProvider:CGDataProvider? = nil
////                        let data = vf_get_data(frame)
////
////                        dataProvider = CGDataProvider(data: NSData(bytes: data, length: Int(height * vf_get_bytes_per_row(frame))))
////
////                        guard let dataProvider = dataProvider else{
////                            print("failed to create data provider")
////                            return
////                        }
////                        
////                        guard let cgImage = CGImage(width: Int(width), height: Int(height), bitsPerComponent: 8, bitsPerPixel: 32, bytesPerRow: Int(vf_get_bytes_per_row(frame)), space: colorSpace, bitmapInfo: bitmapInfo, provider: dataProvider, decode: nil, shouldInterpolate: true, intent: .defaultIntent) else{
////                            print("failed to create cgimage")
////                            return
////                        }
////                        DispatchQueue.main.sync {
////                            ffmpegFrame = NSImage(cgImage: cgImage, size: CGSize(width: cgImage.width, height: cgImage.height))
////                        }
////                    }
//
//                    
//                }
//            }
//            return true
//        }
//    } // body
//} // view
//
//

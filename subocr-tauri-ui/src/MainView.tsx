import { useState, useEffect, useMemo } from "react";
import { Slider, Button, Stack, TextField,Typography, Link,
      Checkbox, Collapse, Card, CardContent, FormControlLabel, Divider, Select, MenuItem,
      List, ListItemButton,
      LinearProgress} from "@mui/material";
import { useTheme } from '@mui/material/styles';
import { us2mmss, us2srt } from "./utils";
import { save, message, confirm } from '@tauri-apps/plugin-dialog';
import "./MainView.css";

import { getCurrentWebview, Webview } from "@tauri-apps/api/webview";

import { invoke } from "@tauri-apps/api/core";
// import { save } from '@tauri-apps/api/dialog';

// import {  SetVideoResponse, SubtitleAnchor, BoundingBox } from "./protocol";
import { BoundingBox } from "./bindings/BoundingBox";
import { CVColor } from "./back/CVColor";
import { SubocrProgress } from "./bindings/SubocrProgress";
import { SubtitleAnchor } from "./back/SubtitleAnchor";
import { SetVideoResponse } from "./bindings/SetVideoResponse";
import { RustSubtitle } from "./bindings/RustSubtitle";
import { GetVideoFrameResponse } from "./bindings/GetVideoFrameResponse";


const LanguageText = [
  "中文",
  "英语",
  "日语",
  "韩语",
]


const ANCHOR_COLOR = [
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
const ANCHOR_COLOR_STR = ANCHOR_COLOR.map(c => `rgb(${c[0]}, ${c[1]}, ${c[2]})`);




function MainView() {
  
  const theme = useTheme();
  const primaryColor = theme.palette.primary.main;

  const [videoUrl, setVideoUrl] = useState<string>("");
  // const [inputEnabled, setInputEnabled] = useState<boolean>(false);
  const [isPredetRunning, setIsPredetRunning] = useState<boolean>(false);
  const [isPipelineRunning, setIsPipelineRunning] = useState<boolean>(false);
  const [progressStarted, setProgressStarted] = useState<boolean>(false);
  const [progressStartUs, setProgressStartUs] = useState(0);
  const [progressCurrentUs, setProgressCurrentUs] = useState(0);
  const [progressDurationUs, setProgressDurationUs] = useState(0);
  const [progressSpeedup, setProgressSpeedup] = useState<number>(1);
  var innerSubtitles:RustSubtitle[] = [];
  const [subtitles, setSubtitles] = useState<RustSubtitle[]>([]);
  const [selectedSubtitleIdx, setSelectedSubtitleIdx] = useState<number>(-1);

  const [fps, setFps] = useState<number>(10);
  const [minSubtitleMs, setMinSubtitleMs] = useState<number>(500);
  const [autoAnalyze, setAutoAnalyze] = useState<boolean>(false);

  const [rightWidth, setRightWidth] = useState(window.innerWidth * 0.25); // 初始右侧宽度为窗口大小的1/4
  const [windowHeight, setWindowHeight] = useState(window.innerHeight); // 初始高度为窗口高度
  
  const [startUs, setStartUs] = useState(0);
  const [currentUs, setCurrentUs] = useState(0);
  const [endUs, setEndUs] = useState(0);


  const [imageData, setImageData] = useState<string | null>(null); // 初始图片数据为空
  const [bboxes, setBBoxes] = useState<BoundingBox[]>([]);
  const [bboxLangs, setBBoxLangs] = useState<number[]>([]);
  const [anchors, setAnchors] = useState<SubtitleAnchor[]>([]);

  const [sliderValue, setSliderValue] = useState(0);

  const [opened, setOpened] = useState(false);

  const isInputDisabled = useMemo(() => videoUrl.length <= 0 || isPredetRunning || isPipelineRunning, 
                [videoUrl, isPredetRunning, isPipelineRunning]);
  const isBeginDisabled = useMemo(() => anchors.length <= 0 || anchors.every(anchor => anchor.is_primary===0), [anchors]);

  const handleFps = (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log(event.target.value);
    const newValue = parseInt(event.target.value, 10);
    if (!isNaN(newValue)) {
      var value = Math.min(newValue, 999);
      value = Math.max(value, 1);
      setFps(value);
    }
  };
  
  const handleMinsubtitleMs = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseInt(event.target.value, 10);
    if (!isNaN(newValue)) {
      var value = Math.min(newValue, 5000);
      value = Math.max(value, 1);
      setMinSubtitleMs(value);
    }
  }

  
  // var anchors: SubtitleAnchor[] = [];
  const updateImage = async (us: number, skipCheck = false) => {

    if(!skipCheck){
    //   if(endUs <= 0){
    //     return;
    //   }
    }
    let colors:CVColor[] = anchors.map((_, index)=>{
      let color:CVColor = {r: ANCHOR_COLOR[index%ANCHOR_COLOR.length][0], g: ANCHOR_COLOR[index%ANCHOR_COLOR.length][1], b: ANCHOR_COLOR[index%ANCHOR_COLOR.length][2]};
      return color;
      // return {r: ANCHOR_COLOR[index%ANCHOR_COLOR.length][0], g: ANCHOR_COLOR[index%ANCHOR_COLOR.length][1], b: ANCHOR_COLOR[index%ANCHOR_COLOR.length][2]};
    });
    let ret:string = await invoke("get_video_frame", { us:  Math.round(us), anchors: anchors, colors: colors });
    // console.log("update image ret: " + ret);
    const res:GetVideoFrameResponse = JSON.parse(ret)
    console.log(res.valid, res.bboxes);
    if(res.valid === false){
      return;
    }
    setImageData(res.image_b64);
    setBBoxes(res.bboxes);
    setBBoxLangs(res.langs);
  }
  const addAnchors = ()=>{
    var newAnchors:SubtitleAnchor[] = [];
    for(let i=0; i<bboxes.length; i++){
      let lang = bboxLangs[i];
      newAnchors.push({center_x: bboxes[i].center_x, center_y: bboxes[i].center_y, height: bboxes[i].height, lang: lang, is_primary: lang==0?1:0,
        avg_width: 0, min_width: 0, mid_width: 0, max_width: 0});
    }
    // 按centery排序
    newAnchors.sort((a, b) => a.center_y - b.center_y);
    console.log("bboxes: " + bboxes);
    console.log("anchors: " + anchors);
    setAnchors([...anchors, ...newAnchors]);
  }
  useEffect(() => {
    updateImage(currentUs);
  }, [currentUs, anchors]);

  
  const maxSliderValue = 1000;
  useEffect(() => {
    setCurrentUs(startUs + sliderValue * (endUs-startUs) / maxSliderValue);
  }, [sliderValue])

  const startPredet = async(url:string)=>{
    if(anchors.length > 0){
      const confirmation = await confirm(
        '将会删除已有的字幕锚点，是否继续？',
        { title: '分析字幕锚点', kind: 'warning' }
      );
      if(!confirmation){
        return;
      }
    }
    setAnchors([]);
    setIsPredetRunning(true);
    setProgressStarted(true);
    await invoke("start_predet", { path:url, maxSec: 1200, defaultLang: 0 });
  }

  const startPipeline = async(url:string)=>{
    if(subtitles.length > 0){
      const confirmation = await confirm(
        '将会删除已有字幕，是否继续？',
        { title: '开始提取', kind: 'warning' }
      );
      if(!confirmation){
        return;
      }
    }
    setIsPipelineRunning(true);
    setProgressStarted(true);
    innerSubtitles = [];
    setSubtitles([]);
    await invoke("start_pipeline", {path: url, fps: fps, minSubtitleUs: minSubtitleMs*1000, anchors: anchors});
  }
  // 定时更新进度
  useEffect(() => {
    const interval = setInterval(async() => {
      if((!isPredetRunning) && (!isPipelineRunning)){
        return;
      }
      let ret:string = await invoke("query_progress");
      let res:SubocrProgress = JSON.parse(ret);
      let isFinished = res.is_finished;
      let startUs = Number(res.start_us);
      let currentUs = Number(res.current_us);
      let durationUs =  Number( res.duration_us);
      let speed_up = res.speed_up;

      setProgressStartUs(startUs);
      setProgressCurrentUs(currentUs);
      setProgressDurationUs(durationUs);
      setProgressSpeedup(speed_up);
      if(isFinished){
        setProgressCurrentUs(startUs + durationUs);
      }
      if(isPredetRunning){
        if(isFinished){
          setIsPredetRunning(false);
          let ret:string = await invoke("query_anchors");
          let anchors:SubtitleAnchor[] = JSON.parse(ret);
          console.log(ret, typeof ret);
          console.log(anchors, typeof anchors);
          setAnchors(anchors);
          // setAnchors(ret);
          // const qstring = buildQueryStringUrl("query-anchors", {});
          // let ret:string = await invoke("get_request", { url: qstring });
          // console.log(ret);
          // let res = JSON.parse(ret);
          // console.log(res)
          // var newAnchors:SubtitleAnchor[] = [];
          // for(let i=0; i<res.anchors.length; i++){
          //   let tmp = res.anchors[i];
          //   newAnchors.push({center_x: tmp[0], center_y: tmp[1], height: tmp[2], lang: tmp[3], is_primary: tmp[4],
          //     avg_width: 0, min_width: 0, mid_width: 0, max_width: 0});
          // }
          // setAnchors(newAnchors);
        }
      }else if(isPipelineRunning){
        const querySubtitles = async()=>{
          let ret:string = await invoke("query_new_subtitles");
          console.log(ret);
          let res:RustSubtitle[] = JSON.parse(ret);
          console.log(res)
          if(res.length <= 0){
            return;
          }
          for(let i=0; i<res.length; i++){
            innerSubtitles.push({start_us: res[i].start_us, end_us: res[i].end_us, strs: res[i].strs});
          }
          setSubtitles(innerSubtitles);
        }
        await querySubtitles();
        if(isFinished){
          setIsPipelineRunning(false);
          await querySubtitles();
          innerSubtitles.sort((a,b)=>Number(a.start_us-b.start_us));
          setSubtitles(innerSubtitles)
        }
      }
    }, 500); // 500 毫秒
    return () => clearInterval(interval);
  }, [isPredetRunning, isPipelineRunning]);

  // 导出SRT
  const exportSrt = async(subs:RustSubtitle[])=>{
    if(isPipelineRunning){
      await message("请等待字幕提取完成", { title: '尚未完成', kind: 'warning' });
      return;
    }
    // 视频后缀替换为.srt
    var idx = -1
    for(let i=0; i<videoUrl.length; i++){
      if(videoUrl[i] === '.'){
        idx = i;
      }
    }
    var options:any = {
      title: "选择要保存的路径",
      filters: [{
        name: '字幕文件',
        extensions: ['srt']
      }]
    }
    if(idx >= 0){
      var path = videoUrl.substring(0, idx) + '.srt';
      options["defaultPath"] = path;
    }

    const foo = await save(options);
    if(foo === null) return;
    console.log(foo);

    let res = "";
    var idx = 1
    for(let i=0; i<subs.length; i++){
      let sub = subs[i];
      let strStart = us2srt(sub.start_us);
      let strEnd = us2srt(sub.end_us);
      for(let j=0; j<sub.strs.length; j++){
        let str = sub.strs[j];
        res += `${idx}\n${strStart} --> ${strEnd}\n${str}\n\n`;
        idx += 1;
      }
    }
    await invoke("write_file", { path: foo, content: res });
    await message(`已将字幕导出到: "${foo}" `, { title: '导出完成', kind: 'info' });
  }

  const [webview, setWebview] = useState<Webview | undefined>(undefined);
  // 禁用默认的drag  drop
  useEffect(() => {
    const handleFileDrop = (event: DragEvent) => { event.preventDefault(); };
    const handleDragOver = (event: DragEvent) => { event.preventDefault(); };
    const handleResize = () => { setWindowHeight(window.innerHeight); };
    window.addEventListener('drop', handleFileDrop);
    window.addEventListener('dragover', handleDragOver);
    window.addEventListener('resize', handleResize);

    let fn = async()=>{
      setWebview(await getCurrentWebview());
    }
    fn()
    return () => {
      window.removeEventListener('drop', handleFileDrop);
      window.removeEventListener('dragover', handleDragOver);
      window.removeEventListener('resize', handleResize);
    };
  }, []);
  // 处理drag drop
  useEffect(() => {
    console.log(webview)
    if (webview) {
      const unlistenDrop = webview.onDragDropEvent((event) => {
        if (event.payload.type === 'over') {
          console.log('drag over');
        } else if (event.payload.type === 'drop') {
          console.log('User dropped', event.payload.paths);
          const path = event.payload.paths[0];
          let fn = async()=>{
            let res:SetVideoResponse = await invoke("set_video", { path: path });
            console.log("set video ret: " + res);
            console.log(res.valid);
            console.log(res, typeof res.duration_us);
            if (res.valid) {
              setVideoUrl(path);
              setAnchors([]);
              setBBoxes([]);
              setStartUs(res.start_us);
              setEndUs(startUs + (res.duration_us));
              setCurrentUs(startUs);
              setSliderValue(0);
              updateImage(startUs, true);
              if(autoAnalyze){
                startPredet(path);
              }
            }
          }
          fn();

          // let path = event.payload.paths[0];
          // // 发送post请求，参数为url: path
          // // axios.post('http://localhost:2024/set-video', { path: path })
  
          // let fn = async()=>{
          //   const param:SetVideoParams = { url: path };
          //   // 使用server地址和param构造querystring
          //   const qstring = buildQueryStringUrl("set-video", param);
          //   console.log(qstring);
          //   let ret:string = await invoke("get_request", { url: qstring });
          //   console.log(ret);
          //   const res: SetVideoResponse = JSON.parse(ret);
          //   console.log(res);
          //   if (res.valid) {
          //     setVideoUrl(path);
          //     setAnchors([]);
          //     setBBoxes([]);
          //     setStartUs(res.startUs ?? 0);
          //     setEndUs(startUs + (res.durationUs ?? 0));
          //     setCurrentUs(startUs);
          //     setSliderValue(0);
          //     updateImage(startUs, true);
          //     if(autoAnalyze){
          //       startPredet(path);
          //     }
          //   }
          // };
          // fn();
          
        } else {
          // console.log('File drop cancelled');
        }
      });
      return () => {
        const cleanup = async()=>{
          (await unlistenDrop)();
        };
        cleanup();
      }
    }
  }, [webview]);


  const handleMouseDown = (e: React.MouseEvent) => {
    const startX = e.clientX;
    const startWidth = rightWidth;

    const handleMouseMove = (e: MouseEvent) => {
      const newWidth = startWidth - (e.clientX - startX);
      setRightWidth(newWidth);
    };

    const handleMouseUp = () => {
      document.removeEventListener("mousemove", handleMouseMove);
      document.removeEventListener("mouseup", handleMouseUp);
    };

    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
  };
//   <div className="image-container" style={{ backgroundColor: "black", display: "flex", justifyContent: "center", alignItems: "center" }}>
//   {/* <span style={{ color: "white" }}>将视频拖拽到此处</span> */}

// </div>
  
  return (
    <Stack direction="row" style={{height: windowHeight - 20, overflowX:"hidden" }}>
      
    <div style={{minWidth: 600, height: "100%", display: "flex", flexDirection:"column"}} className="left-pane">
        <div style={{flex: "1"}}>
        <Stack className="left-pane" sx={{padding: "0.5rem", paddingBottom: 0}}>
        {imageData ? <img src={imageData} alt="Base64 Image" style={{maxWidth: "100%", maxHeight: window.innerHeight*0.5, objectFit: 'contain'}} /> : 
                    <Typography style={{ color: "white", fontSize: "2rem", background: "black", width: "100%", height:window.innerHeight*0.5, 
                      alignItems:"center", alignContent:"center", textAlign:"center", }}>
                      将视频拖拽到此处
                    </Typography>
                    //  <span style={{ color: "white", fontSize: "1.4rem", background: "black", width: "100%", height:"60%", 
                    //           alignItems:"center", alignContent:"center", textAlign:"center", }}>
                    //     将视频拖拽到此处
                    //   </span>
        }

          
          <div style={{ display: "flex", justifyContent: "center", alignItems: "center", marginTop: "0.5rem" }}>
            <span style={{ fontSize: "1.2rem" }}>{us2mmss(currentUs)}</span>
            <Slider 
              value={sliderValue} 
              min={0}
              max={maxSliderValue}
              onChange={(_e, newValue) => setSliderValue(newValue as number)} 
              aria-label="Video Progress" 
              valueLabelDisplay="off" 
              style={{marginLeft:"1rem", marginRight:"0.2rem"}}
            />
            <span style={{ fontSize: "1.2rem", marginLeft: "1rem" }}>{us2mmss(endUs)}</span>
          </div>

          <Stack spacing={2} direction="row" style={{marginTop:"1rem", height:"2rem"}}>
            <Button variant="contained" onClick={()=>startPipeline(videoUrl)} disabled={isInputDisabled || isBeginDisabled}>开始提取</Button>
            <Button variant="outlined" onClick={() => addAnchors()} disabled={bboxes.length === 0 || isInputDisabled}>添加字幕锚点</Button>
            <Button variant="outlined" disabled={isInputDisabled} onClick={(_e)=>{ startPredet(videoUrl);}}>分析字幕锚点</Button>



            <FormControlLabel
              control={
                <Checkbox
                checked={opened}
                onChange={(e) => setOpened(e.target.checked)}
                inputProps={{ 'aria-label': 'controlled' }}
                style={{marginLeft:"1rem"}}
                />
              }
              label="显示设置"
            />
          </Stack>
          <Collapse in={opened} style={{marginTop:"0.5rem",marginBottom:"0.5rem"}}>
            <Card>
              <CardContent>
                <Stack direction={"column"}>
                  <FormControlLabel
                    control={
                      <Checkbox
                      checked={autoAnalyze}
                      onChange={(e) => setAutoAnalyze(e.target.checked)}
                      inputProps={{ 'aria-label': 'controlled' }}
                      />
                    }
                    label="拖入视频时，自动分析字幕锚点"
                  />
                  <Stack direction={"row"} alignItems={"center"} alignContent={"center"}>
                    <Typography>字幕检测频率(FPS): </Typography>
                    <TextField disabled={isInputDisabled}
                      variant="standard" size="small"
                      type="number"
                      className="custom-textfield"
                      value={fps}
                      style={{maxWidth:"6rem", width: "4rem", marginLeft: "1rem"}}
                      onChange={handleFps}
                      />
                  </Stack>

                  <Stack direction={"row"} alignItems={"center"} alignContent={"center"}>
                    <Typography>字幕最短时间(毫秒): </Typography>
                    <TextField disabled={isInputDisabled}
                      variant="standard" size="small"
                      type="number"
                      className="custom-textfield"
                      value={minSubtitleMs}
                      style={{maxWidth:"6rem", width: "4rem", marginLeft: "1rem"}}
                      onChange={handleMinsubtitleMs}
                      />
                  </Stack>
                </Stack>
              </CardContent>
            </Card>
          </Collapse>
          <Collapse in={progressStarted} style={{marginBottom:"1rem"}}>
            <div style={{width: "100%", display:"flex", flexDirection:"row", alignContent:"center", alignItems:"center", height:"2rem"}}>
              {subtitles.length>0 && <Button variant="contained" onClick={(_e)=>exportSrt(subtitles)} >导出字幕</Button>}
              <Typography style={{marginLeft:"1rem", marginRight:"0.5rem"}}>
                {((isPipelineRunning) || (subtitles.length > 0)) ? "提取字幕" : "分析字幕"}
              </Typography>
              { (isPredetRunning || isPipelineRunning) ?
              <Typography  style={{marginRight:"0.5rem"}} color="red">[x{progressSpeedup.toFixed(1)}]</Typography> :
              <Typography  style={{marginRight:"0.5rem"}} color="green">[已完成]</Typography>
              }
              <Typography style={{marginRight:"0.5rem"}}>{us2mmss(progressCurrentUs)}</Typography>
              <LinearProgress style={{flex:1, marginRight:"0.5rem"}} variant="determinate" value={Number(progressCurrentUs-progressStartUs) * 100 / Number(progressDurationUs)}></LinearProgress>
              <Typography>{us2mmss(progressStartUs+progressDurationUs)}</Typography>
            </div>
          </Collapse>


            {anchors.map((anchor, index) => (
              // <li key={index}>
                <Stack direction={"row"} key={index} style={{alignContent: "center", alignItems:"center", marginBottom:"0.5rem", marginLeft:"1rem"}}>
                  <Typography style={{minWidth:"3.5rem"}}>字幕{index+1}</Typography>
                    <div style={{ background:ANCHOR_COLOR_STR[index%ANCHOR_COLOR_STR.length ], width:"2.5rem", height:"1.2rem", marginRight:"1rem"}}/>
                    <Typography>X: </Typography>
                    <TextField disabled={isInputDisabled}
                      variant="standard" size="small"
                      type="number"
                      value={anchor.center_x}
                      style={{maxWidth:"6rem", width: "3.5rem", marginLeft: "0.5rem"}}
                      onChange={(event)=>{
                        const newValue = parseInt(event.target.value, 10);
                        setAnchors((prevAnchors) => {
                          const newAnchors = [...prevAnchors];
                          newAnchors[index].center_x = newValue;
                          return newAnchors;
                        });
                      }}
                      />

                    <Typography style={{marginLeft: "1rem"}}>Y: </Typography>
                    <TextField disabled={isInputDisabled}
                      variant="standard" size="small"
                      type="number"
                      value={anchor.center_y}
                      style={{maxWidth:"6rem", width: "3.5rem", marginLeft: "0.5rem"}}
                      onChange={(event)=>{
                        const newValue = parseInt(event.target.value, 10);
                        setAnchors((prevAnchors) => {
                          const newAnchors = [...prevAnchors];
                          newAnchors[index].center_y = newValue;
                          return newAnchors;
                        });
                      }}
                      />

                    <Typography style={{marginLeft: "1rem"}}>高度: </Typography>
                    <TextField disabled={isInputDisabled}
                      variant="standard" size="small"
                      type="number"
                      value={anchor.height}
                      style={{maxWidth:"6rem", width: "3rem", marginLeft: "0.5rem"}}
                      onChange={(event)=>{
                        const newValue = parseInt(event.target.value, 10);
                        setAnchors((prevAnchors) => {
                          const newAnchors = [...prevAnchors];
                          newAnchors[index].height = newValue;
                          return newAnchors;
                        });
                      }}
                      />

                    <Typography style={{marginLeft: "1rem"}}>语言: </Typography>
                  
                    <Select disabled={isInputDisabled}
                      variant="standard"
                      style={{marginLeft: "0.5rem"}}
                      value={anchor.lang}
                      label="语言: "
                      onChange={(event)=>{
                        console.log(event.target.value);
                        if(typeof event.target.value === "number"){
                          const newValue = event.target.value;
                          setAnchors((prevAnchors) => {
                            const newAnchors = [...prevAnchors];
                            newAnchors[index].lang = newValue;
                            return newAnchors;
                          })
                        }
                      }}
                    >
                      {
                        LanguageText.map((lang, index)=>{
                          return <MenuItem key={index} value={index}>{lang}</MenuItem>
                        })
                      }
                    </Select>

                    <FormControlLabel style={{color:anchor.is_primary ? "black" : "gray"}}
                    control={
                      <Checkbox disabled={isInputDisabled}
                      checked={anchor.is_primary ? true : false}
                      onChange={(e) =>                           
                        setAnchors((prevAnchors) => {
                        const newAnchors = [...prevAnchors];
                        newAnchors[index].is_primary = e.target.checked ? 1 : 0;
                        return newAnchors;
                      })}
                      inputProps={{ 'aria-label': 'controlled' }}
                      style={{marginLeft:"2rem", color:anchor.is_primary ? primaryColor : "gray"}}
                      />
                    }
                    label="主字幕"
                    />
                    <Button disabled={isInputDisabled}
                      variant="contained"
                      style={{height:"1.4rem", background: "white", marginLeft: "1rem"}}
                      onClick={()=>{
                        setAnchors((prevAnchors) => {
                          const newAnchors = [...prevAnchors];
                          newAnchors.splice(index, 1);
                          return newAnchors;
                        })
                      }}
                    >
                      <Typography color="red">删除</Typography>
                    </Button>
                    
                </Stack>
              // </li>
            ))}
          


        </Stack>
        </div>
        {/* <div style={{flex: "1"}}/> */}
        <Stack
            direction="column"
            // justifyContent="center" // 沿主轴（x轴）居中
            alignItems="center" // 沿交叉轴（y轴）居中
            margin={0}
            padding={0}
        >
          <Typography variant="caption"><Link href='https://github.com/nhjydywd/SubtitleOCR' target="_blank">GitHub: https://github.com/nhjydywd/SubtitleOCR</Link> </Typography>
          {/* <Typography variant="caption"><Link href='https://github.com/nhjydywd/SubtitleOCR' target="_blank">如果本项目对你有帮助，请点一个免费的Star❤️吧~谢谢</Link> </Typography> */}
        </Stack>

      </div>
      <div className="divider" onMouseDown={handleMouseDown} style={{minWidth: 3}}></div>
      <div className="right-pane" style={{width: rightWidth, minWidth:200}}>
        <List dense={true} style={{padding:0, margin:0, borderSpacing: 0}}>
          {
            subtitles.map((subtitle, index) => (
              <ListItemButton
              style={{padding:0}}
              selected={selectedSubtitleIdx === index}
              onClick={(_event) => {
                setSelectedSubtitleIdx(index)
                let us = subtitle.start_us;
                let percent = (us-startUs) / (endUs - startUs);
                setSliderValue(percent * maxSliderValue);
                }
              }
            >
              <Stack direction="column" style={{width:"100%", marginTop:3}}>
              <Typography fontSize="0.7rem" color="gray" style={{paddingLeft: 10, paddingBottom:2}}>{us2mmss(subtitle.start_us) + " --> " + us2mmss(subtitle.end_us)}</Typography> 

              {
                subtitle.strs.map((str, _i) => (
                  <Typography fontSize="0.8rem" style={{paddingLeft: 10}}>{str}</Typography> 
                ))
              }
              <Divider style={{paddingTop:3}}/>
              </Stack>
            </ListItemButton>
            ))
          }

        </List>
      </div>
    </Stack>
  );
}

export default MainView;

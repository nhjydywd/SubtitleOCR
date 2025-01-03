/*
格式化时间
返回格式: hh:mm:ss,ms  其中:
hh: 小时, 长度无限制, 若<1则省略。
mm: 分钟, 长度为2, 不足2位补0。
ss: 秒, 长度为2, 不足2位补0。
ms: 毫秒, 长度为3, 不足3位补0。
*/
export function us2mmss(us: number, needMs:Boolean=false):string{
    let ms = us / 1000;
    let s = Math.floor(ms / 1000);
    let m = Math.floor(s / 60);
    let h = Math.floor(m / 60);
    ms = ms % 1000;
    s = s % 60;
    m = m % 60;
    let res = `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    if (h > 0){
      res = `${h}:${res}`;
    }
    if (needMs){
      res += `,${ms.toString().padStart(3, '0')}`;
    }
    return res;
  }


export function us2srt(us:number):string{
  //参照上面实现
  let totalSeconds = us / 1_000_000 // 转换为秒
  let hours = Math.floor(totalSeconds / 3600)
  let minutes = Math.floor((totalSeconds % 3600) / 60)
  let seconds = Math.floor(totalSeconds % 60)
  let ms = Math.floor(us % 1_000_000 / 1_000)
  let res = `${String(hours)}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')},${String(ms).padStart(3, '0')}`
  // if (hours > 0){
  //   res = `${res}`;
  // }
  return res;
}
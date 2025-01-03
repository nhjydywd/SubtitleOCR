
import React, { useEffect } from 'react';
import MainView from './MainView';
import { useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { CircularProgress,  Stack, LinearProgress, Typography } from '@mui/material';


const App: React.FC = () => {
  const [isPreinitFinished, setIsPreinitFinished] = useState(true);
  const [isInitFinished, setIsInitFinished] = useState(false);

  const baseProgress = 5;
  const [progress, setProgress] = useState(baseProgress);
  const [windowHeight, setWindowHeight] = useState(window.innerHeight); // 初始高度为窗口高度
  
  const startDate = new Date();
  const intervalMs = 1000.0;
  const expectedTimeSec = 150.0;
  useEffect(() => {
    let fn = async () => {
      setIsPreinitFinished(await invoke('is_preinited') as boolean);
      setIsInitFinished(await invoke('is_inited') as boolean);
    }
    fn();

    const interval = setInterval(async() => {
      if (isPreinitFinished && isInitFinished){
        return;
      }
      const passedMs = new Date().getTime() - startDate.getTime();
      let newProgress = Math.min(baseProgress + passedMs * 100 / expectedTimeSec / 1000 , 100);
      setProgress(newProgress);

      setIsPreinitFinished(await invoke('is_preinited') as boolean);
      setIsInitFinished(await invoke('is_inited') as boolean);
    }, intervalMs);

    const handleResize = () => { setWindowHeight(window.innerHeight); };
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
      clearInterval(interval);
    }
  }, []);
  
  return (
    <div>
      {!isPreinitFinished && 
      <Stack direction="column" style={{height: windowHeight-100, width:"100%", 
              alignItems:"center", justifyContent:"center"}} spacing="1rem">
        <CircularProgress size="4rem" />
        <Typography variant="h5">编译模型中，请稍等...</Typography> 
        <LinearProgress variant="determinate" value={progress} style={{width:"50%", height:"0.8rem"}}/>
      </Stack>
      }
      {isInitFinished && <MainView /> }
    </div>
  );
}

export default App;
// import { useState, useEffect } from "react";
// import "./App.css";


// import { invoke } from "@tauri-apps/api/core";




// function App() {
//   const [rightWidth, setRightWidth] = useState(window.innerWidth * 0.25); // 初始右侧宽度为窗口大小的1/4

//   const handleMouseDown = (e: React.MouseEvent) => {
//     const startX = e.clientX;
//     const startWidth = rightWidth;

//     const handleMouseMove = (e: MouseEvent) => {
//       const newWidth = startWidth - (e.clientX - startX);
//       setRightWidth(newWidth);
//     };

//     const handleMouseUp = () => {
//       document.removeEventListener("mousemove", handleMouseMove);
//       document.removeEventListener("mouseup", handleMouseUp);
//     };

//     document.addEventListener("mousemove", handleMouseMove);
//     document.addEventListener("mouseup", handleMouseUp);
//   };

//   return (
//     <div className="container">
      
//       <div className="left-pane" style={{minWidth: 600}}>
//         左侧内容
//       </div>
//       <div className="divider" onMouseDown={handleMouseDown}></div>
//       <div className="right-pane" style={{minWidth:200, width: rightWidth, background: "red"}}>
//         右侧内容
//       </div>
//     </div>
//   );
// }

// export default App;

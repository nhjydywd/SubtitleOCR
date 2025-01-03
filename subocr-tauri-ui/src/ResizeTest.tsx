import { useEffect } from 'react';

function ResizeTest() {
    useEffect(() => {
        const onResize = () => {
            console.log('resize. innerHeight:', window.innerHeight)
        }
        window.addEventListener('resize', onResize)
        return () => {
            window.removeEventListener('resize', onResize)
        }
    })
    // window.addEventListener('resize', () => {
    //     console.log('resize')
    // }
    return (
        <div style={{height:window.innerHeight, background:"green"}}>
            <h1>Resize Test</h1>
            <div style={{ width: '100%', height: '100%', backgroundColor: 'red' }}></div>
        </div>
    )
}

export default ResizeTest;
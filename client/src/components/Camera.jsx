import { useRef, useEffect } from "react";
import WebCam from 'react-webcam';
import './Camera.css';

export function Camera(props) {
    const {setImage} = props;
    const webcamRef = useRef(null);

    async function capture() {
        const imageSrc = await webcamRef.current.getScreenshot();
        await setImage(imageSrc);
    }

    useEffect(() => {
        const interval = setInterval(() => {
            capture();
        }, 1000);

        return () => {
            clearInterval(interval);
        }
    }, []);

    return (
        <div className="camera">
            <WebCam
                audio={false}
                height={300}
                width={300}
                ref={webcamRef}
                screenshotFormat="image/jpeg"
            />
        </div>
    )
}
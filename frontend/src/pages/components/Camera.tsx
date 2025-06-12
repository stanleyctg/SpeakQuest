import React, { useEffect, useRef, useState } from "react";
import Webcam from "react-webcam";
import Button from "./Button";
import "./../styles/Camera.css";

// Define the video constraints for webcam
const VIDEO_CONSTRAINTS: MediaTrackConstraints = {
  width: 940,
  height: 640,
} as const;

export default function Camera() {
  const [permission, setPermission] = useState<boolean | null>(null);
  const webcamRef = useRef<Webcam | null>(null);

  // Check media permissions
  async function checkPermission() {
    let stream: MediaStream | null = null;
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: VIDEO_CONSTRAINTS,
      });
      setPermission(true);
    } catch (err) {
      console.error("Error accessing media devices.", err);
      setPermission(false);
      return;
    } finally {
      stream?.getTracks().forEach((t) => t.stop());
    }
  }

  useEffect(() => {
    checkPermission();
  }, []);

  if (permission === null) {
    return <p>Checking permissions...</p>;
  }

  return (
    <div className="wrapper">
      {permission === false ? (
        <p>
          Please allow access to your camera and microphone to use this feature.
        </p>
      ) : (
        <>
          <div className="overlay-info">
            <span>Attempts Remaining: 3</span>
            <span>Time Left: 2:00</span>
          </div>
          <div className="webcam-container">
            <Webcam
              audio={true}
              ref={webcamRef}
              videoConstraints={VIDEO_CONSTRAINTS}
              height={VIDEO_CONSTRAINTS.height as number}
              width={VIDEO_CONSTRAINTS.width as number}
            />
          </div>

          <div className="button-container">
            <Button
              onClick={() => {
                console.log("Starting...");
              }}
              children="Start/Stop Recording"
            />
          </div>
        </>
      )}
    </div>
  );
}

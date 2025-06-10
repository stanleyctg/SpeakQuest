import React, { useState, useRef, useEffect } from "react";
import Webcam from "react-webcam";

// Define the video constraints for webcam
const VIDEO_CONSTRAINTS: MediaTrackConstraints = {
  width: 780,
  height: 640,
};

export default function Practice() {
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

  // Display webcam feed if permission is granted
  return (
    <div>
      <h1>Live Capture</h1>
      {permission === false ? (
        <p>
          Please allow access to your camera and microphone to use this feature.
          <button onClick={checkPermission}>Retry</button>
        </p>
      ) : (
        <Webcam
          audio={true}
          ref={webcamRef}
          videoConstraints={VIDEO_CONSTRAINTS}
          height={VIDEO_CONSTRAINTS.height as number}
          width={VIDEO_CONSTRAINTS.width as number}
        />
      )}
    </div>
  );
}

import * as React from "react";
import { AudioRecorder } from "react-audio-voice-recorder";

export default function Microphone() {
  // Function to handle the completion of audio recording
  const saveAudioFile = async (data: Blob) => {
    console.log("Audio file saved:", data);
  };

  return (
    <div>
      <AudioRecorder
        onRecordingComplete={saveAudioFile}
        audioTrackConstraints={{
          noiseSuppression: true,
          echoCancellation: true,
        }}
        onNotAllowedOrFound={(err) => console.table(err)}
        downloadOnSavePress={false}
        downloadFileExtension="webm"
        mediaRecorderOptions={{
          audioBitsPerSecond: 128000,
        }}
        // showVisualizer={true}
      />
      <br />
    </div>
  );
}

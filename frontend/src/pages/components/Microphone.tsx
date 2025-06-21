import * as React from "react";
import { AudioRecorder } from "react-audio-voice-recorder";

export default function Microphone() {
  // Function to handle the completion of audio recording
  const saveAudioFile = async (data: Blob) => {
    const formData = new FormData();
    formData.append("audio", data, "recording.webm");
    try {
      const response = await fetch("http://localhost:8000/api/upload-audio", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Failed to upload audio file");
      }
      const result = await response.json();
      console.log("Audio file uploaded successfully:", result);
      getFeedback();
    } catch (error) {
      console.error("Error uploading audio file:", error);
    }
  };

  const getFeedback = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/feedback", {
        method: "POST",
      });
      if (!response.ok) {
        throw new Error("Failed to transcribe audio file");
      }
      const result = await response.json();
      console.log("Transcription result:", result.transcription);
      return result.transcription;
    } catch (error) {
      console.error("Error transcribing audio file:", error);
    }
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

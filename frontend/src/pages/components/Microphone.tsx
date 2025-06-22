import * as React from "react";
import { AudioRecorder } from "react-audio-voice-recorder";

interface MicrophoneProps {
  question: string;
  onNext: () => void;
}

export default function Microphone({ question, onNext }: MicrophoneProps) {
  // Function to handle the completion of audio recording
  const saveAudioFileAndQuestion = async (data: Blob) => {
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
    const formData = new FormData();
    formData.append("question", question);
    try {
      const response = await fetch("http://localhost:8000/api/feedback", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) {
        throw new Error("Failed to transcribe audio file");
      }
      const result = await response.json();
      console.log("Transcription result:", result.transcription);
      console.log("Feedback result:    ", result.feedback);
      console.log("question result: ", question);
      onNext();
    } catch (error) {
      console.error("Error transcribing audio file:", error);
    }
  };

  return (
    <div>
      <AudioRecorder
        onRecordingComplete={saveAudioFileAndQuestion}
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

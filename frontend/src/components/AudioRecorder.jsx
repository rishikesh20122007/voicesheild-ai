import { useState, useRef } from "react";

function AudioRecorder({ onRecordingComplete }) {
  const [isRecording, setIsRecording] = useState(false);
  const [recordedBlob, setRecordedBlob] = useState(null);
  const [error, setError] = useState("");
  const [seconds, setSeconds] = useState(0);

  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const timerRef = useRef(null);
  const streamRef = useRef(null);

  const startRecording = async () => {
    setError("");
    setRecordedBlob(null);
    setSeconds(0);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        setRecordedBlob(blob);
        onRecordingComplete(blob);
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);

      timerRef.current = setInterval(() => {
        setSeconds((prev) => prev + 1);
      }, 1000);
    } catch (err) {
      setError("Microphone access denied or unavailable. Please allow microphone permissions.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      clearInterval(timerRef.current);
    }
  };

  const formatTime = (totalSeconds) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className="bg-slate-800 border border-slate-600 rounded p-4">
      <p className="text-sm text-slate-300 mb-3">Record Audio Live</p>

      {error && (
        <div className="bg-red-900/30 border border-vs-danger text-red-300 text-sm rounded p-3 mb-3">
          {error}
        </div>
      )}

      <div className="flex items-center gap-4">
        {!isRecording ? (
          <button
            type="button"
            onClick={startRecording}
            className="bg-vs-danger text-white font-semibold px-4 py-2 rounded hover:bg-red-500 transition flex items-center gap-2"
          >
            <span className="w-2 h-2 bg-white rounded-full"></span>
            Start Recording
          </button>
        ) : (
          <button
            type="button"
            onClick={stopRecording}
            className="bg-slate-600 text-white font-semibold px-4 py-2 rounded hover:bg-slate-500 transition flex items-center gap-2"
          >
            <span className="w-2 h-2 bg-vs-danger rounded-full animate-pulse"></span>
            Stop Recording ({formatTime(seconds)})
          </button>
        )}

        {recordedBlob && !isRecording && (
          <span className="text-vs-safe text-sm">
            Recording captured ({formatTime(seconds)})
          </span>
        )}
      </div>

      {recordedBlob && !isRecording && (
        <audio className="mt-3 w-full" controls src={URL.createObjectURL(recordedBlob)} />
      )}
    </div>
  );
}

export default AudioRecorder;

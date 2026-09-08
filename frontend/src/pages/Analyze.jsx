import { useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import AudioUploader from "../components/AudioUploader";
import AudioRecorder from "../components/AudioRecorder";
import RiskCard from "../components/RiskCard";
import { analyzeAudio } from "../services/api";

function Analyze() {
  const [mode, setMode] = useState("upload"); // "upload" or "record"
  const [file, setFile] = useState(null);
  const [recordedBlob, setRecordedBlob] = useState(null);
  const [transcript, setTranscript] = useState("");
  const [description, setDescription] = useState("");
  const [transactionAmount, setTransactionAmount] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleModeChange = (newMode) => {
    setMode(newMode);
    setFile(null);
    setRecordedBlob(null);
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    const audioToSend =
      mode === "upload" ? file : recordedBlob ? new File([recordedBlob], "recording.webm", { type: "audio/webm" }) : null;

    if (!audioToSend) {
      setError(
        mode === "upload"
          ? "Please select an audio file first."
          : "Please record audio first."
      );
      return;
    }

    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append("file", audioToSend);
    if (transcript) formData.append("transcript", transcript);
    if (description) formData.append("description", description);
    if (transactionAmount) formData.append("transaction_amount", transactionAmount);

    try {
      const response = await analyzeAudio(formData);
      setResult(response.data);
    } catch (err) {
      const detail = err.response?.data?.detail || "Analysis failed. Please try again.";
      setError(typeof detail === "string" ? detail : "Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleNewAnalysis = () => {
    setFile(null);
    setRecordedBlob(null);
    setTranscript("");
    setDescription("");
    setTransactionAmount("");
    setResult(null);
    setError("");
  };

  return (
    <div className="min-h-screen bg-vs-dark">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6 max-w-3xl">
          <h2 className="text-2xl font-bold text-slate-100 mb-6">Audio Analysis</h2>

          {!result && (
            <form onSubmit={handleSubmit} className="bg-vs-panel border border-slate-700 rounded-lg p-6 space-y-4">
              <div className="flex gap-2 mb-2">
                <button
                  type="button"
                  onClick={() => handleModeChange("upload")}
                  className={`px-4 py-2 rounded text-sm font-semibold transition ${
                    mode === "upload"
                      ? "bg-vs-accent text-vs-dark"
                      : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                  }`}
                >
                  Upload File
                </button>
                <button
                  type="button"
                  onClick={() => handleModeChange("record")}
                  className={`px-4 py-2 rounded text-sm font-semibold transition ${
                    mode === "record"
                      ? "bg-vs-accent text-vs-dark"
                      : "bg-slate-700 text-slate-300 hover:bg-slate-600"
                  }`}
                >
                  Record Live
                </button>
              </div>

              {mode === "upload" ? (
                <AudioUploader file={file} onFileChange={setFile} />
              ) : (
                <AudioRecorder onRecordingComplete={setRecordedBlob} />
              )}

              <div>
                <label className="block text-sm text-slate-300 mb-1">
                  Call Transcript (optional)
                </label>
                <textarea
                  value={transcript}
                  onChange={(e) => setTranscript(e.target.value)}
                  rows={3}
                  className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-slate-100 focus:outline-none focus:border-vs-accent"
                  placeholder="Paste or type what was said during the call..."
                />
              </div>

              <div>
                <label className="block text-sm text-slate-300 mb-1">
                  Description (optional)
                </label>
                <input
                  type="text"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-slate-100 focus:outline-none focus:border-vs-accent"
                  placeholder="Brief context about this call/recording"
                />
              </div>

              <div>
                <label className="block text-sm text-slate-300 mb-1">
                  Transaction Amount, if any (optional)
                </label>
                <input
                  type="number"
                  value={transactionAmount}
                  onChange={(e) => setTransactionAmount(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-600 rounded px-3 py-2 text-slate-100 focus:outline-none focus:border-vs-accent"
                  placeholder="e.g. 50000"
                />
              </div>

              {error && (
                <div className="bg-red-900/30 border border-vs-danger text-red-300 text-sm rounded p-3">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-vs-accent text-vs-dark font-semibold py-2 rounded hover:bg-cyan-300 transition disabled:opacity-50"
              >
                {loading ? "Analyzing..." : "Analyze Audio"}
              </button>
            </form>
          )}

          {result && (
            <div className="space-y-4">
              <RiskCard result={result} />
              <button
                onClick={handleNewAnalysis}
                className="w-full bg-slate-700 text-slate-100 font-semibold py-2 rounded hover:bg-slate-600 transition"
              >
                New Analysis
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default Analyze;

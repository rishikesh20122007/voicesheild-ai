import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import RiskCard from "../components/RiskCard";
import { getHistory, getScanDetail, deleteScan } from "../services/api";

const RISK_BADGE_STYLES = {
  LOW: "bg-green-900/40 text-vs-safe border-vs-safe",
  MEDIUM: "bg-yellow-900/40 text-vs-warning border-vs-warning",
  HIGH: "bg-orange-900/40 text-orange-400 border-orange-500",
  CRITICAL: "bg-red-900/40 text-vs-danger border-vs-danger",
};

function History() {
  const [scans, setScans] = useState([]);
  const [selectedScan, setSelectedScan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [detailLoading, setDetailLoading] = useState(false);

  const loadHistory = async () => {
    setLoading(true);
    try {
      const response = await getHistory();
      setScans(response.data);
    } catch (err) {
      setError("Could not load scan history.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleViewDetail = async (scanId) => {
    setDetailLoading(true);
    setError("");
    try {
      const response = await getScanDetail(scanId);
      setSelectedScan(response.data);
    } catch (err) {
      setError("Could not load scan detail.");
    } finally {
      setDetailLoading(false);
    }
  };

  const handleDelete = async (scanId, e) => {
    e.stopPropagation();
    if (!window.confirm("Delete this scan? This cannot be undone.")) return;

    try {
      await deleteScan(scanId);
      setScans((prev) => prev.filter((s) => s.id !== scanId));
      if (selectedScan && selectedScan.scan_id === scanId) {
        setSelectedScan(null);
      }
    } catch (err) {
      setError("Could not delete scan.");
    }
  };

  const formatDate = (isoString) => {
    return new Date(isoString).toLocaleString();
  };

  return (
    <div className="min-h-screen bg-vs-dark">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <h2 className="text-2xl font-bold text-slate-100 mb-6">Scan History</h2>

          {error && (
            <div className="bg-red-900/30 border border-vs-danger text-red-300 text-sm rounded p-3 mb-4">
              {error}
            </div>
          )}

          {selectedScan && (
            <div className="mb-6">
              <button
                onClick={() => setSelectedScan(null)}
                className="text-vs-accent text-sm mb-3 hover:underline"
              >
                ← Back to list
              </button>
              <RiskCard result={selectedScan} />
            </div>
          )}

          {!selectedScan && (
            <>
              {loading && <p className="text-slate-400">Loading history...</p>}

              {!loading && scans.length === 0 && (
                <p className="text-slate-400">
                  No scans yet. Go to Analyze Audio to run your first scan.
                </p>
              )}

              {!loading && scans.length > 0 && (
                <div className="space-y-3">
                  {scans.map((scan) => (
                    <div
                      key={scan.id}
                      onClick={() => handleViewDetail(scan.id)}
                      className="bg-vs-panel border border-slate-700 rounded-lg p-4 flex items-center justify-between cursor-pointer hover:border-vs-accent transition"
                    >
                      <div>
                        <p className="text-slate-100 font-medium">
                          {scan.filename || "Live Recording"}
                        </p>
                        <p className="text-slate-400 text-sm">
                          {formatDate(scan.created_at)}
                        </p>
                      </div>

                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <p className="text-slate-400 text-xs">Risk Score</p>
                          <p className="text-slate-100 font-semibold">
                            {scan.risk_score}/100
                          </p>
                        </div>

                        <span
                          className={`text-xs font-bold px-3 py-1 rounded border ${
                            RISK_BADGE_STYLES[scan.risk_level] || RISK_BADGE_STYLES.LOW
                          }`}
                        >
                          {scan.risk_level}
                        </span>

                        <button
                          onClick={(e) => handleDelete(scan.id, e)}
                          className="text-slate-500 hover:text-vs-danger transition text-sm"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {detailLoading && (
                <p className="text-slate-400 mt-4">Loading scan detail...</p>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
}

export default History;

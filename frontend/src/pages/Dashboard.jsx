import { useEffect, useState } from "react";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";
import { getDashboardStats } from "../services/api";

const RISK_COLORS = {
  LOW: "#22c55e",
  MEDIUM: "#f59e0b",
  HIGH: "#f97316",
  CRITICAL: "#ef4444",
};

function StatCard({ label, value, accent }) {
  return (
    <div className="bg-vs-panel border border-slate-700 rounded-lg p-5">
      <p className="text-slate-400 text-sm mb-1">{label}</p>
      <p className={`text-3xl font-bold ${accent || "text-slate-100"}`}>{value}</p>
    </div>
  );
}

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await getDashboardStats();
        setStats(response.data);
      } catch (err) {
        setError("Could not load dashboard stats.");
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  const chartData = stats
    ? Object.entries(stats.risk_distribution)
        .filter(([, count]) => count > 0)
        .map(([level, count]) => ({ name: level, value: count }))
    : [];

  return (
    <div className="min-h-screen bg-vs-dark">
      <Navbar />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-6">
          <h2 className="text-2xl font-bold text-slate-100 mb-6">Security Dashboard</h2>

          {loading && <p className="text-slate-400">Loading stats...</p>}
          {error && <p className="text-vs-danger">{error}</p>}

          {stats && (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <StatCard label="Total Scans" value={stats.total_scans} />
                <StatCard label="Real Voice" value={stats.real_voice_count} accent="text-vs-safe" />
                <StatCard label="AI / Deepfake" value={stats.ai_voice_count} accent="text-vs-danger" />
                <StatCard label="Avg Risk Score" value={`${stats.average_risk_score}/100`} />
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <StatCard label="High Risk Alerts" value={stats.high_risk_count} accent="text-orange-400" />
                <StatCard label="Critical Risk Alerts" value={stats.critical_risk_count} accent="text-vs-danger" />
              </div>

              <div className="bg-vs-panel border border-slate-700 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-slate-100 mb-4">Risk Distribution</h3>
                {chartData.length === 0 ? (
                  <p className="text-slate-400">No scans yet. Run an analysis to see data here.</p>
                ) : (
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={chartData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={100}
                        label
                      >
                        {chartData.map((entry) => (
                          <Cell key={entry.name} fill={RISK_COLORS[entry.name]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                )}
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}

export default Dashboard;

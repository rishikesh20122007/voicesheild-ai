const RISK_STYLES = {
  LOW: { bg: "bg-green-900/30", border: "border-vs-safe", text: "text-vs-safe" },
  MEDIUM: { bg: "bg-yellow-900/30", border: "border-vs-warning", text: "text-vs-warning" },
  HIGH: { bg: "bg-orange-900/30", border: "border-orange-500", text: "text-orange-400" },
  CRITICAL: { bg: "bg-red-900/30", border: "border-vs-danger", text: "text-vs-danger" },
};

function RiskCard({ result }) {
  const style = RISK_STYLES[result.risk_level] || RISK_STYLES.LOW;

  return (
    <div className={`border rounded-lg p-6 ${style.bg} ${style.border}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-slate-100">Voice Security Analysis</h3>
        <span className={`text-sm font-bold px-3 py-1 rounded ${style.text} border ${style.border}`}>
          {result.risk_level} RISK
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <p className="text-slate-400 text-sm">Human Voice Probability</p>
          <p className="text-2xl font-bold text-slate-100">{result.human_probability}%</p>
        </div>
        <div>
          <p className="text-slate-400 text-sm">AI Generated Probability</p>
          <p className={`text-2xl font-bold ${style.text}`}>{result.ai_probability}%</p>
        </div>
        <div>
          <p className="text-slate-400 text-sm">Authenticity Score</p>
          <p className="text-2xl font-bold text-slate-100">{result.authenticity_score}/100</p>
        </div>
        <div>
          <p className="text-slate-400 text-sm">Impersonation Risk</p>
          <p className={`text-2xl font-bold ${style.text}`}>{result.risk_score}/100</p>
        </div>
      </div>

      {result.indicators.length > 0 && (
        <div className="mb-4">
          <p className="text-slate-300 font-semibold mb-2">Detected Indicators:</p>
          <ul className="list-disc list-inside space-y-1">
            {result.indicators.map((indicator, idx) => (
              <li key={idx} className="text-slate-300 text-sm">{indicator}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="mb-4">
        <p className="text-slate-300 font-semibold mb-1">Recommended Action:</p>
        <p className="text-slate-300 text-sm">{result.recommendation}</p>
      </div>

      {result.actions.length > 0 && (
        <div>
          <ul className="list-disc list-inside space-y-1">
            {result.actions.map((action, idx) => (
              <li key={idx} className="text-slate-300 text-sm">{action}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default RiskCard;

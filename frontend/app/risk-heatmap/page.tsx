"use client";

import { useState, useEffect } from "react";
import { getApiUrl } from "../lib/api";
import { Flame, GitCommit, AlertTriangle, ShieldAlert, FileText, Info, History } from "lucide-react";

interface HeatmapCell {
  file_path: string;
  time_bucket: string;
  bug_proneness_score: number;
  churn_count: number;
  bugfix_count: number;
  last_incident: string;
}

interface HeatmapData {
  repo_id: number;
  repo_name: string;
  files: string[];
  time_buckets: string[];
  cells: HeatmapCell[];
}

export default function RiskHeatmapPage() {
  const [data, setData] = useState<HeatmapData>({
    repo_id: 1,
    repo_name: "sentinel-demo/payment-gateway",
    files: [
      "backend/app/services/payment_processor.py",
      "backend/app/auth/jwt_verifier.py",
      "backend/app/db/session_manager.py",
      "backend/app/api/checkout.py",
      "backend/app/utils/helpers.py"
    ],
    time_buckets: ["W26", "W27", "W28", "W29", "W30", "W31"],
    cells: [
      { file_path: "backend/app/services/payment_processor.py", time_bucket: "W26", bug_proneness_score: 95.0, churn_count: 38, bugfix_count: 7, last_incident: "2026-07-28" },
      { file_path: "backend/app/services/payment_processor.py", time_bucket: "W27", bug_proneness_score: 92.0, churn_count: 35, bugfix_count: 6, last_incident: "2026-07-28" },
      { file_path: "backend/app/services/payment_processor.py", time_bucket: "W28", bug_proneness_score: 88.5, churn_count: 38, bugfix_count: 7, last_incident: "2026-07-28" },
      { file_path: "backend/app/services/payment_processor.py", time_bucket: "W29", bug_proneness_score: 85.0, churn_count: 30, bugfix_count: 5, last_incident: "2026-07-28" },
      { file_path: "backend/app/services/payment_processor.py", time_bucket: "W30", bug_proneness_score: 88.5, churn_count: 38, bugfix_count: 7, last_incident: "2026-07-28" },
      { file_path: "backend/app/services/payment_processor.py", time_bucket: "W31", bug_proneness_score: 88.5, churn_count: 38, bugfix_count: 7, last_incident: "2026-07-28" },

      { file_path: "backend/app/auth/jwt_verifier.py", time_bucket: "W26", bug_proneness_score: 82.0, churn_count: 22, bugfix_count: 4, last_incident: "2026-07-20" },
      { file_path: "backend/app/auth/jwt_verifier.py", time_bucket: "W27", bug_proneness_score: 79.0, churn_count: 22, bugfix_count: 4, last_incident: "2026-07-20" },
      { file_path: "backend/app/auth/jwt_verifier.py", time_bucket: "W28", bug_proneness_score: 76.2, churn_count: 22, bugfix_count: 4, last_incident: "2026-07-20" },
      { file_path: "backend/app/auth/jwt_verifier.py", time_bucket: "W29", bug_proneness_score: 72.0, churn_count: 20, bugfix_count: 3, last_incident: "2026-07-20" },
      { file_path: "backend/app/auth/jwt_verifier.py", time_bucket: "W30", bug_proneness_score: 76.2, churn_count: 22, bugfix_count: 4, last_incident: "2026-07-20" },
      { file_path: "backend/app/auth/jwt_verifier.py", time_bucket: "W31", bug_proneness_score: 76.2, churn_count: 22, bugfix_count: 4, last_incident: "2026-07-20" },

      { file_path: "backend/app/db/session_manager.py", time_bucket: "W26", bug_proneness_score: 60.0, churn_count: 15, bugfix_count: 2, last_incident: "2026-06-15" },
      { file_path: "backend/app/db/session_manager.py", time_bucket: "W27", bug_proneness_score: 58.0, churn_count: 15, bugfix_count: 2, last_incident: "2026-06-15" },
      { file_path: "backend/app/db/session_manager.py", time_bucket: "W28", bug_proneness_score: 54.0, churn_count: 15, bugfix_count: 2, last_incident: "2026-06-15" },
      { file_path: "backend/app/db/session_manager.py", time_bucket: "W29", bug_proneness_score: 50.0, churn_count: 12, bugfix_count: 1, last_incident: "2026-06-15" },
      { file_path: "backend/app/db/session_manager.py", time_bucket: "W30", bug_proneness_score: 54.0, churn_count: 15, bugfix_count: 2, last_incident: "2026-06-15" },
      { file_path: "backend/app/db/session_manager.py", time_bucket: "W31", bug_proneness_score: 54.0, churn_count: 15, bugfix_count: 2, last_incident: "2026-06-15" },

      { file_path: "backend/app/api/checkout.py", time_bucket: "W26", bug_proneness_score: 85.0, churn_count: 29, bugfix_count: 5, last_incident: "2026-07-25" },
      { file_path: "backend/app/api/checkout.py", time_bucket: "W27", bug_proneness_score: 83.0, churn_count: 29, bugfix_count: 5, last_incident: "2026-07-25" },
      { file_path: "backend/app/api/checkout.py", time_bucket: "W28", bug_proneness_score: 81.0, churn_count: 29, bugfix_count: 5, last_incident: "2026-07-25" },
      { file_path: "backend/app/api/checkout.py", time_bucket: "W29", bug_proneness_score: 78.0, churn_count: 25, bugfix_count: 4, last_incident: "2026-07-25" },
      { file_path: "backend/app/api/checkout.py", time_bucket: "W30", bug_proneness_score: 81.0, churn_count: 29, bugfix_count: 5, last_incident: "2026-07-25" },
      { file_path: "backend/app/api/checkout.py", time_bucket: "W31", bug_proneness_score: 81.0, churn_count: 29, bugfix_count: 5, last_incident: "2026-07-25" },

      { file_path: "backend/app/utils/helpers.py", time_bucket: "W26", bug_proneness_score: 22.0, churn_count: 6, bugfix_count: 0, last_incident: "N/A" },
      { file_path: "backend/app/utils/helpers.py", time_bucket: "W27", bug_proneness_score: 20.0, churn_count: 6, bugfix_count: 0, last_incident: "N/A" },
      { file_path: "backend/app/utils/helpers.py", time_bucket: "W28", bug_proneness_score: 18.2, churn_count: 6, bugfix_count: 0, last_incident: "N/A" },
      { file_path: "backend/app/utils/helpers.py", time_bucket: "W29", bug_proneness_score: 15.0, churn_count: 5, bugfix_count: 0, last_incident: "N/A" },
      { file_path: "backend/app/utils/helpers.py", time_bucket: "W30", bug_proneness_score: 18.2, churn_count: 6, bugfix_count: 0, last_incident: "N/A" },
      { file_path: "backend/app/utils/helpers.py", time_bucket: "W31", bug_proneness_score: 18.2, churn_count: 6, bugfix_count: 0, last_incident: "N/A" },
    ]
  });

  const [selectedCell, setSelectedCell] = useState<HeatmapCell | null>(data.cells[4]); // Default to payment_processor.py

  useEffect(() => {
    fetch(getApiUrl("/api/risk-heatmap-latest"))
      .then((res) => res.json())
      .then((d) => {
        if (d && d.cells && d.cells.length > 0) {
          setData(d);
          setSelectedCell(d.cells[0]);
        }
      })
      .catch(() => {});
  }, []);

  const getCellColor = (score: number) => {
    if (score >= 80) return "bg-rose-600 hover:bg-rose-500 shadow-lg shadow-rose-600/30 text-white font-bold";
    if (score >= 60) return "bg-amber-500 hover:bg-amber-400 shadow-md shadow-amber-500/20 text-gray-950 font-bold";
    if (score >= 40) return "bg-indigo-600 hover:bg-indigo-500 text-white font-semibold";
    if (score >= 20) return "bg-emerald-600/80 hover:bg-emerald-500 text-white";
    return "bg-gray-800 hover:bg-gray-700 text-gray-400";
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="border-b border-gray-800 pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-3xl font-extrabold text-white tracking-tight">Repository Risk Heatmap</h1>
            <span className="px-3 py-1 text-xs font-black bg-gradient-to-r from-amber-500 to-rose-600 text-white rounded-md uppercase tracking-wider shadow-md shadow-rose-500/20">
              Unique Differentiator
            </span>
          </div>
          <p className="text-gray-400 text-sm mt-1">
            PyDriller git history mining: file churn count, bugfix commit frequency, and recency weight independently of static syntax.
          </p>
        </div>

        <div className="flex items-center space-x-4 text-xs font-mono bg-gray-900/80 p-2.5 rounded-xl border border-gray-800">
          <span className="text-gray-400 font-semibold">Intensity Legend:</span>
          <span className="px-2 py-0.5 rounded bg-gray-800 text-gray-400">&lt;20 Low</span>
          <span className="px-2 py-0.5 rounded bg-emerald-600 text-white">20-40</span>
          <span className="px-2 py-0.5 rounded bg-indigo-600 text-white">40-60</span>
          <span className="px-2 py-0.5 rounded bg-amber-500 text-gray-950 font-bold">60-80</span>
          <span className="px-2 py-0.5 rounded bg-rose-600 text-white font-bold">80+ Fragile</span>
        </div>
      </div>

      {/* Grid + Inspector Sidebar Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Heatmap Grid */}
        <div className="lg:col-span-2 glass-panel p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Flame className="w-5 h-5 text-rose-500" />
              <span>File Fragility Timeline (Files × Weekly Buckets)</span>
            </h2>
            <span className="text-xs font-mono text-gray-400">Click any cell to inspect commit audit</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-gray-800 text-xs font-mono text-gray-400">
                  <th className="py-3 px-4 font-semibold">File Path</th>
                  {data.time_buckets.map((b) => (
                    <th key={b} className="py-3 px-3 text-center font-semibold">{b}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800/60 text-xs">
                {data.files.map((file) => {
                  const fileCells = data.cells.filter((c) => c.file_path === file);

                  return (
                    <tr key={file} className="hover:bg-gray-900/40 transition-colors">
                      <td className="py-4 px-4 font-mono font-medium text-gray-200 max-w-xs truncate" title={file}>
                        {file}
                      </td>
                      {data.time_buckets.map((bucket) => {
                        const cell = fileCells.find((c) => c.time_bucket === bucket) || {
                          file_path: file,
                          time_bucket: bucket,
                          bug_proneness_score: 10,
                          churn_count: 2,
                          bugfix_count: 0,
                          last_incident: "N/A"
                        };

                        const isSelected = selectedCell?.file_path === file && selectedCell?.time_bucket === bucket;

                        return (
                          <td key={bucket} className="py-2 px-2 text-center">
                            <button
                              onClick={() => setSelectedCell(cell)}
                              className={`w-full py-2.5 rounded-lg text-xs transition-all duration-150 transform hover:scale-105 ${getCellColor(
                                cell.bug_proneness_score
                              )} ${isSelected ? "ring-2 ring-white scale-105 shadow-xl" : ""}`}
                            >
                              {cell.bug_proneness_score}
                            </button>
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Selected Cell Risk Inspector Sidebar */}
        <div className="glass-panel p-6 flex flex-col justify-between border-l-4 border-l-rose-500">
          {selectedCell ? (
            <div className="space-y-6">
              <div>
                <div className="flex items-center justify-between text-xs font-mono text-rose-400 mb-1">
                  <span>RISK AGENT AUDIT</span>
                  <span>{selectedCell.time_bucket}</span>
                </div>
                <h3 className="text-lg font-black text-white break-all">{selectedCell.file_path}</h3>
              </div>

              {/* Bug Proneness Score Gauge */}
              <div className="p-4 rounded-xl bg-gray-900/80 border border-gray-800 text-center">
                <div className="text-xs uppercase font-mono text-gray-400 mb-1">Bug-Proneness Score</div>
                <div className="text-4xl font-black text-rose-400 mb-1">{selectedCell.bug_proneness_score} <span className="text-sm text-gray-500">/ 100</span></div>
                <div className="text-xs font-semibold text-rose-400/90">
                  {selectedCell.bug_proneness_score >= 75 ? "🚨 Mandatory Senior Review Required" : "⚠️ Standard QA Required"}
                </div>
              </div>

              {/* PyDriller Metrics */}
              <div className="space-y-3 font-mono text-xs">
                <div className="flex items-center justify-between p-3 rounded-lg bg-gray-900/50 border border-gray-800">
                  <span className="text-gray-400 flex items-center gap-1.5"><GitCommit className="w-4 h-4 text-indigo-400" /> Historical Churn Count:</span>
                  <span className="font-bold text-white">{selectedCell.churn_count} commits</span>
                </div>

                <div className="flex items-center justify-between p-3 rounded-lg bg-gray-900/50 border border-gray-800">
                  <span className="text-gray-400 flex items-center gap-1.5"><AlertTriangle className="w-4 h-4 text-amber-400" /> Bugfix Commits Regex:</span>
                  <span className="font-bold text-amber-400">{selectedCell.bugfix_count} matching fixes</span>
                </div>

                <div className="flex items-center justify-between p-3 rounded-lg bg-gray-900/50 border border-gray-800">
                  <span className="text-gray-400 flex items-center gap-1.5"><History className="w-4 h-4 text-rose-400" /> Last Incident Date:</span>
                  <span className="font-bold text-gray-200">{selectedCell.last_incident}</span>
                </div>
              </div>

              {/* Formula & Recommendation */}
              <div className="p-4 rounded-xl bg-indigo-950/30 border border-indigo-500/20 text-xs space-y-2">
                <div className="font-bold text-indigo-300 flex items-center gap-1.5">
                  <Info className="w-4 h-4" /> Risk Score Formula Rationale
                </div>
                <p className="text-gray-300 leading-relaxed font-mono">
                  norm(churn={selectedCell.churn_count}) * 0.3 + norm(bugfix={selectedCell.bugfix_count}) * 0.5 + recency * 0.2
                </p>
                <div className="text-amber-300 font-medium pt-1">
                  &bull; Syntactically clean PRs touching this file will still be escalated to senior reviewers due to high historical failure recurrence.
                </div>
              </div>
            </div>
          ) : (
            <div className="text-center py-12 text-gray-500 text-sm">Select a cell in the heatmap grid to view PyDriller historical commit metrics.</div>
          )}
        </div>

      </div>
    </div>
  );
}

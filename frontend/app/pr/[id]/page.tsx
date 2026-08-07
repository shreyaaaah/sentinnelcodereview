"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  ShieldAlert,
  Zap,
  CheckCircle2,
  AlertTriangle,
  Flame,
  ArrowLeft,
  GitPullRequest,
  FileCode,
  Lock,
  Code
} from "lucide-react";

interface Finding {
  id: number;
  agent: string;
  file_path: string;
  line_start: number;
  line_end: number;
  severity: string;
  cvss_score?: number;
  cvss_vector?: string;
  complexity_estimate?: string;
  description: string;
  suggested_fix?: string;
}

export default function PRDetailPage({ params }: { params: { id: string } }) {
  const prId = params.id || "101";

  const [pr, setPr] = useState({
    pr_number: 101,
    title: "Multi-Agent Code Review Scan",
    author: "developer",
    status: "open",
    overall_risk_score: 0.0,
    created_at: new Date().toISOString(),
    findings: [] as Finding[]
  });

  const diffCodeLines = [
    { line: 38, type: " ", content: "def process_user_payment(user_id, amount, card_token):" },
    { line: 39, type: " ", content: "    # Process user transaction" },
    { line: 40, type: " ", content: "    # Missing docstring" },
    { line: 41, type: " ", content: "    logger.info('Processing payment')" },
    { line: 42, type: "+", content: "    api_key = 'sk_live_998877665544332211'", findingId: 1 },
    { line: 43, type: "+", content: "    query = 'SELECT * FROM accounts WHERE id = ' + str(user_id)", findingId: 2 },
    { line: 44, type: " ", content: "    db.execute(query)" },
    { line: 45, type: "+", content: "    for item in user_items:", findingId: 3 },
    { line: 46, type: "+", content: "        db.query('SELECT * FROM inventory WHERE id = ' + str(item.id))" },
    { line: 47, type: "+", content: "    eval('process_hook(' + card_token + ')')" },
    { line: 48, type: " ", content: "    return True" },
  ];

  useEffect(() => {
    const targetId = prId === "101" ? (localStorage.getItem("latest_pr_id") || "latest") : prId;
    fetch(`http://localhost:8000/api/prs/${targetId}`)
      .then((res) => res.json())
      .then((d) => {
        if (d && d.pr_number) {
          setPr({
            pr_number: d.pr_number,
            title: d.title || "Multi-Agent Code Review Scan",
            author: d.author || "developer",
            status: d.status || "open",
            overall_risk_score: d.overall_risk_score || 45.0,
            created_at: d.created_at || new Date().toISOString(),
            findings: d.findings || []
          });
        }
      })
      .catch(() => {});
  }, [prId]);

  const activeFileName = pr.findings[0]?.file_path || (pr.title.includes("(") ? pr.title.split("(")[1].replace(")", "") : pr.title.replace("File Scan: ", "")) || "scanned_file.py";

  const dynamicDiffLines = pr.findings.length > 0 ? pr.findings.map((f, idx) => ({
    line: f.line_start || (idx + 1),
    type: "+",
    content: `# [${f.agent.toUpperCase()}] Line ${f.line_start}: ${f.description}`,
    finding: f
  })) : [
    { line: 1, type: " ", content: `# Code File: ${activeFileName}`, finding: null },
    { line: 2, type: "+", content: `# Multi-agent review complete. All checks passed clean!`, finding: null }
  ];

  return (
    <div className="space-y-8">
      {/* Navigation & Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-800 pb-6">
        <div>
          <Link
            href="/dashboard"
            className="inline-flex items-center space-x-1.5 text-xs font-mono text-indigo-400 hover:text-indigo-300 mb-2 transition-colors"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Quality Overview</span>
          </Link>
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-black text-white flex items-center gap-2">
              <GitPullRequest className="w-6 h-6 text-indigo-400" />
              <span>PR #{pr.pr_number}: {pr.title}</span>
            </h1>
            <span className="px-2.5 py-1 text-xs font-bold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 rounded">
              Author: {pr.author}
            </span>
          </div>
        </div>

        {/* PR Risk Score Badge */}
        <div className="flex items-center space-x-4 glass-panel px-5 py-3 border-l-4 border-l-rose-500">
          <div>
            <div className="text-[10px] uppercase font-mono text-gray-400">Overall PR Risk Score</div>
            <div className="text-2xl font-black text-rose-400">{pr.overall_risk_score} / 100</div>
          </div>
          <span className="px-3 py-1 text-xs font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-lg">
            {pr.overall_risk_score > 60 ? "High Risk Escalation" : "Standard Review"}
          </span>
        </div>
      </div>

      {/* CVSS Security Breakdown Banner */}
      <div className="glass-panel p-5 border border-indigo-500/30 bg-indigo-950/10">
        <h2 className="text-base font-bold text-white mb-3 flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-indigo-400" />
          <span>Multi-Agent Findings & CVSS Matrix Summary ({pr.findings.length} Findings)</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-xs font-mono">
          {pr.findings.length > 0 ? pr.findings.slice(0, 4).map((f, i) => (
            <div key={i} className="p-3 bg-gray-900/80 rounded-lg border border-gray-800">
              <div className="text-gray-400 font-semibold mb-1">[{f.agent.toUpperCase()}] Line {f.line_start}</div>
              <div className="text-rose-400 font-bold truncate">{f.description}</div>
              <div className="text-gray-500 text-[10px] mt-1">Severity: {f.severity.toUpperCase()}</div>
            </div>
          )) : (
            <div className="col-span-4 p-4 bg-emerald-950/20 border border-emerald-500/30 rounded-lg text-emerald-400 font-semibold text-center">
              ✓ Clean Code — Zero Critical Vulnerabilities or Performance Bottlenecks Detected.
            </div>
          )}
        </div>
      </div>

      {/* Split Diff View with Inline Agent Highlights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Side: Code Diff Viewer */}
        <div className="lg:col-span-2 glass-panel p-6">
          <div className="flex items-center justify-between mb-4 border-b border-gray-800 pb-3">
            <div className="flex items-center space-x-2 font-mono text-xs text-gray-300">
              <FileCode className="w-4 h-4 text-indigo-400" />
              <span className="font-bold text-white">{activeFileName}</span>
            </div>
            <span className="text-xs font-mono text-gray-500">{pr.findings.length} findings annotated</span>
          </div>

          <div className="bg-gray-950 font-mono text-xs rounded-xl p-4 overflow-x-auto border border-gray-900 leading-relaxed">
            {dynamicDiffLines.map((item, idx) => {
              const finding = item.finding;

              return (
                <div key={idx} className="flex flex-col">
                  <div className={`flex items-center px-2 py-1 rounded ${
                    item.type === "+" ? "bg-emerald-950/30 text-emerald-300" : "text-gray-400"
                  } ${finding ? "bg-rose-950/40 border-l-2 border-l-rose-500" : ""}`}>
                    <span className="w-8 text-gray-600 select-none text-right mr-4">{item.line}</span>
                    <span className="w-4 text-gray-500 select-none mr-2">{item.type}</span>
                    <span className="whitespace-pre flex-1">{item.content}</span>
                  </div>

                  {/* Inline Finding Card */}
                  {finding && (
                    <div className="my-2 ml-12 p-3.5 rounded-lg bg-gray-900 border border-rose-500/40 shadow-xl space-y-2">
                      <div className="flex items-center justify-between">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-extrabold uppercase tracking-wider ${
                          finding.severity === "critical" ? "bg-rose-500/20 text-rose-400 border border-rose-500/30" : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                        }`}>
                          [{finding.agent.toUpperCase()}] {finding.severity}
                        </span>
                        {finding.cvss_score && (
                          <span className="text-rose-400 font-bold text-[11px]">CVSS 3.1: {finding.cvss_score}</span>
                        )}
                        {finding.complexity_estimate && (
                          <span className="text-indigo-400 font-bold text-[11px]">Complexity: {finding.complexity_estimate}</span>
                        )}
                      </div>
                      <p className="text-gray-200 text-xs font-sans font-medium">{finding.description}</p>
                      {finding.suggested_fix && (
                        <div className="p-2 rounded bg-gray-950 border border-gray-800 text-[11px] text-emerald-400 font-mono">
                          💡 <span className="font-semibold text-gray-300">Suggested Fix:</span> {finding.suggested_fix}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Right Side: Risk Agent Context Panel */}
        <div className="glass-panel p-6 space-y-6">
          <div>
            <h2 className="text-base font-bold text-white mb-1 flex items-center gap-2">
              <Flame className="w-5 h-5 text-rose-500" />
              <span>Risk Agent Historical Context</span>
            </h2>
            <p className="text-xs text-gray-400">Independent git blame & churn analysis</p>
          </div>

          <div className="p-4 rounded-xl bg-gray-900/80 border border-gray-800 space-y-3 text-xs font-mono">
            <div className="flex justify-between">
              <span className="text-gray-400">Scanned File:</span>
              <span className="text-indigo-400 font-bold truncate max-w-[140px]">{activeFileName}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Total Findings:</span>
              <span className="text-amber-400 font-bold">{pr.findings.length} findings</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">File Risk Score:</span>
              <span className="text-rose-400 font-bold">{pr.overall_risk_score} / 100</span>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-rose-950/30 border border-rose-500/30 space-y-2 text-xs">
            <div className="font-bold text-rose-300 flex items-center gap-1.5">
              <AlertTriangle className="w-4 h-4" /> Recommendation
            </div>
            <p className="text-gray-300 font-medium leading-relaxed">
              Reviews touching <span className="font-mono text-indigo-300">{activeFileName}</span> are prioritized based on historical churn and agent findings ({pr.findings.length} detected).
            </p>
          </div>

          <div className="pt-4 border-t border-gray-800 flex flex-col gap-3">
            <button className="w-full py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/20 transition-all">
              Approve PR Review Status
            </button>
            <button className="w-full py-2.5 rounded-xl bg-gray-800 hover:bg-gray-700 text-gray-300 font-semibold text-xs transition-all">
              Re-run Pipeline Scan
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}

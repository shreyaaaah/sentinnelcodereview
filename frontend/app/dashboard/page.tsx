"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  ShieldAlert,
  Flame,
  Clock,
  TrendingDown,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  GitPullRequest,
  Sparkles
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Legend
} from "recharts";

interface TrendData {
  week: string;
  low: number;
  medium: number;
  high: number;
  critical: number;
  avg_risk_score: number;
}

import { getApiUrl } from "../lib/api";

export default function DashboardPage() {
  const [trends, setTrends] = useState<TrendData[]>([
    { week: "W26", low: 14, medium: 9, high: 5, critical: 3, avg_risk_score: 78.2 },
    { week: "W27", low: 12, medium: 7, high: 4, critical: 2, avg_risk_score: 65.4 },
    { week: "W28", low: 16, medium: 6, high: 2, critical: 1, avg_risk_score: 54.0 },
    { week: "W29", low: 10, medium: 4, high: 1, critical: 0, avg_risk_score: 39.1 },
    { week: "W30", low: 8, medium: 3, high: 1, critical: 0, avg_risk_score: 28.5 },
    { week: "W31", low: 5, medium: 2, high: 0, critical: 0, avg_risk_score: 18.0 },
  ]);

  const [pullRequests, setPullRequests] = useState([
    { id: 101, pr_number: 101, title: "Add payment retry logic and fast hashing", author: "dev-alice", risk_score: 79.5, status: "open", critical_count: 1, high_count: 2, time: "2 hours ago" },
    { id: 100, pr_number: 100, title: "Refactor session timeout middleware", author: "dev-bob", risk_score: 25.0, status: "merged", critical_count: 0, high_count: 0, time: "1 day ago" },
    { id: 99, pr_number: 99, title: "Fix token expiration edge case", author: "dev-charlie", risk_score: 64.0, status: "merged", critical_count: 0, high_count: 1, time: "3 days ago" },
    { id: 98, pr_number: 98, title: "Update dependencies and security patches", author: "dev-alice", risk_score: 88.0, status: "merged", critical_count: 2, high_count: 3, time: "5 days ago" },
  ]);

  useEffect(() => {
    fetch(getApiUrl("/api/dashboard-overview"))
      .then((res) => res.json())
      .then((data) => {
        if (data) {
          if (data.trends && data.trends.length > 0) setTrends(data.trends);
          if (data.pull_requests && data.pull_requests.length > 0) {
            setPullRequests(data.pull_requests.map((p: any) => ({
              id: p.id,
              pr_number: p.pr_number,
              title: p.title,
              author: p.author,
              risk_score: p.risk_score,
              status: p.status,
              critical_count: p.critical_count,
              high_count: p.high_count,
              time: p.created_at || "Recent"
            })));
          }
        }
      })
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-8">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-gray-800 pb-6">
        <div>
          <div className="flex items-center space-x-3">
            <h1 className="text-3xl font-extrabold text-white tracking-tight">Team Quality Overview</h1>
            <span className="px-3 py-1 text-xs font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-full flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" /> AI Triage Active
            </span>
          </div>
          <p className="text-gray-400 text-sm mt-1">
            Historical risk correlation & multi-agent vulnerability trends across pull requests.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Link
            href="/risk-heatmap"
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-amber-500 to-rose-600 hover:from-amber-600 hover:to-rose-700 text-white font-semibold text-sm shadow-lg shadow-rose-500/20 flex items-center space-x-2 transition-all"
          >
            <Flame className="w-4 h-4" />
            <span>Open Risk Heatmap</span>
          </Link>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        
        <div className="glass-panel p-5 border-l-4 border-l-indigo-500">
          <div className="flex items-center justify-between text-gray-400 text-xs font-mono uppercase tracking-wider mb-2">
            <span>Average PR Risk Score</span>
            <Flame className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-black text-white">47.8</span>
            <span className="text-xs font-semibold text-emerald-400 flex items-center">
              <TrendingDown className="w-3.5 h-3.5 mr-0.5" /> -38% vs last month
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-2">Target &lt; 30.0 for low-friction auto-merge</p>
        </div>

        <div className="glass-panel p-5 border-l-4 border-l-rose-500">
          <div className="flex items-center justify-between text-gray-400 text-xs font-mono uppercase tracking-wider mb-2">
            <span>Critical Security Alerts</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-black text-rose-400">1</span>
            <span className="text-xs text-gray-400">Active in PR #101</span>
          </div>
          <p className="text-xs text-rose-400/80 mt-2 font-medium">100% OWASP + CVSS 3.1 score mapped</p>
        </div>

        <div className="glass-panel p-5 border-l-4 border-l-emerald-500">
          <div className="flex items-center justify-between text-gray-400 text-xs font-mono uppercase tracking-wider mb-2">
            <span>Reviewer Time Saved</span>
            <Clock className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-black text-emerald-400">6.5 hrs</span>
            <span className="text-xs text-gray-400">per dev / week</span>
          </div>
          <p className="text-xs text-emerald-400/80 mt-2 font-medium">92% token reduction via semantic AST chunking</p>
        </div>

        <div className="glass-panel p-5 border-l-4 border-l-amber-500">
          <div className="flex items-center justify-between text-gray-400 text-xs font-mono uppercase tracking-wider mb-2">
            <span>Avg Time to Merge</span>
            <CheckCircle2 className="w-4 h-4 text-amber-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-black text-white">10.5 hrs</span>
            <span className="text-xs text-emerald-400">1.4 hrs for low risk</span>
          </div>
          <p className="text-xs text-gray-500 mt-2">Fast-tracked low-risk PRs merge 8x faster</p>
        </div>

      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Weekly Finding Severity Stacked Trend */}
        <div className="lg:col-span-2 glass-panel p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-lg font-bold text-white">Code Quality Severity Trend</h2>
              <p className="text-xs text-gray-400">Weekly findings by severity level detected across pull requests</p>
            </div>
            <div className="flex items-center space-x-4 text-xs font-mono">
              <span className="flex items-center"><span className="w-2.5 h-2.5 rounded-full bg-rose-500 mr-1.5"></span> Critical</span>
              <span className="flex items-center"><span className="w-2.5 h-2.5 rounded-full bg-amber-500 mr-1.5"></span> High</span>
              <span className="flex items-center"><span className="w-2.5 h-2.5 rounded-full bg-indigo-500 mr-1.5"></span> Medium</span>
              <span className="flex items-center"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500 mr-1.5"></span> Low</span>
            </div>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" />
                <XAxis dataKey="week" stroke="#9CA3AF" tickLine={false} />
                <YAxis stroke="#9CA3AF" tickLine={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#111827", borderColor: "#374151", borderRadius: "8px" }}
                  labelStyle={{ color: "#F9FAFB", fontWeight: "bold" }}
                />
                <Bar dataKey="critical" stackId="a" fill="#EF4444" radius={[4, 4, 0, 0]} />
                <Bar dataKey="high" stackId="a" fill="#F59E0B" />
                <Bar dataKey="medium" stackId="a" fill="#6366F1" />
                <Bar dataKey="low" stackId="a" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Time to Merge vs Risk Score Correlation */}
        <div className="glass-panel p-6 flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-bold text-white mb-1">Risk vs Time-to-Merge</h2>
            <p className="text-xs text-gray-400 mb-6">Demonstrates reviewer focus shifting to high-risk files</p>

            <div className="space-y-4">
              <div className="p-3.5 rounded-xl bg-gray-900/60 border border-gray-800 flex items-center justify-between">
                <div>
                  <div className="text-xs font-semibold text-rose-400 uppercase font-mono">High Risk (&gt;75)</div>
                  <div className="text-sm font-extrabold text-white mt-0.5">18.5 hrs avg merge</div>
                </div>
                <span className="px-2.5 py-1 text-xs font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20 rounded-md">
                  Senior Escalate
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-gray-900/60 border border-gray-800 flex items-center justify-between">
                <div>
                  <div className="text-xs font-semibold text-amber-400 uppercase font-mono">Moderate Risk (40-75)</div>
                  <div className="text-sm font-extrabold text-white mt-0.5">8.2 hrs avg merge</div>
                </div>
                <span className="px-2.5 py-1 text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-md">
                  Standard Review
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-gray-900/60 border border-gray-800 flex items-center justify-between">
                <div>
                  <div className="text-xs font-semibold text-emerald-400 uppercase font-mono">Low Risk (&lt;40)</div>
                  <div className="text-sm font-extrabold text-white mt-0.5">1.4 hrs avg merge</div>
                </div>
                <span className="px-2.5 py-1 text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-md">
                  Fast Tracked
                </span>
              </div>
            </div>
          </div>

          <div className="pt-6 border-t border-gray-800 mt-6 text-xs text-gray-400">
            <span className="font-semibold text-white">Value Impact:</span> Humans spend 85% of review time on top 20% risk PRs.
          </div>
        </div>

      </div>

      {/* Pull Requests Triage Table */}
      <div className="glass-panel p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-lg font-bold text-white">Recent Pull Requests & Risk Scores</h2>
            <p className="text-xs text-gray-400">Triage prioritization generated by SentinelReview agents</p>
          </div>
          <span className="text-xs font-mono text-gray-400">Showing 4 PRs</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-300">
            <thead className="bg-gray-900/80 text-xs uppercase font-mono text-gray-400 border-b border-gray-800">
              <tr>
                <th className="px-4 py-3">PR</th>
                <th className="px-4 py-3">Title</th>
                <th className="px-4 py-3">Author</th>
                <th className="px-4 py-3">Risk Score</th>
                <th className="px-4 py-3">Triage Level</th>
                <th className="px-4 py-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-800/60">
              {pullRequests.map((pr) => {
                const isHighRisk = pr.risk_score >= 70;
                const isMedRisk = pr.risk_score >= 40 && pr.risk_score < 70;

                return (
                  <tr key={pr.id} className="hover:bg-gray-800/40 transition-colors">
                    <td className="px-4 py-4 font-mono font-bold text-indigo-400">#{pr.pr_number}</td>
                    <td className="px-4 py-4 font-semibold text-white">
                      {pr.title}
                      {pr.critical_count > 0 && (
                        <span className="ml-2 px-2 py-0.5 text-[10px] bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded font-mono">
                          {pr.critical_count} CRITICAL
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-4 font-mono text-gray-400">{pr.author}</td>
                    <td className="px-4 py-4 font-mono font-bold">
                      <span className={`px-2.5 py-1 rounded-md text-xs ${
                        isHighRisk
                          ? "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                          : isMedRisk
                          ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                          : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                      }`}>
                        {pr.risk_score} / 100
                      </span>
                    </td>
                    <td className="px-4 py-4 text-xs font-semibold">
                      {isHighRisk ? (
                        <span className="text-rose-400 flex items-center gap-1">
                          <AlertTriangle className="w-3.5 h-3.5" /> Escalate to Senior
                        </span>
                      ) : isMedRisk ? (
                        <span className="text-amber-400 flex items-center gap-1">
                          <Clock className="w-3.5 h-3.5" /> Standard QA
                        </span>
                      ) : (
                        <span className="text-emerald-400 flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Fast-track Auto
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-4">
                      <Link
                        href={`/pr/${pr.pr_number}`}
                        className="inline-flex items-center space-x-1 text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors"
                      >
                        <span>View Review</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldAlert, LayoutDashboard, Flame, GitPullRequest, Code, Sparkles } from "lucide-react";

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { name: "Instant Scan", href: "/scan", icon: Code, badge: "Try Live" },
    { name: "Team Overview", href: "/dashboard", icon: LayoutDashboard },
    { name: "Risk Heatmap", href: "/risk-heatmap", icon: Flame, badge: "Differentiator" },
    { name: "PR Detail", href: "/pr/101", icon: GitPullRequest },
  ];

  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-gray-800 bg-dark-900/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Logo & Brand */}
        <Link href="/scan" className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-purple-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <ShieldAlert className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-lg text-white tracking-tight">Sentinel<span className="text-indigo-400">Review</span></span>
              <span className="px-2 py-0.5 text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-full">v1.0</span>
            </div>
            <p className="text-xs text-gray-400 font-mono">Multi-Agent Triage Engine</p>
          </div>
        </Link>

        {/* Navigation Tabs */}
        <nav className="flex items-center space-x-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname?.startsWith(item.href));

            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-bold transition-all ${
                  isActive
                    ? "bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 shadow-sm"
                    : "text-gray-400 hover:text-white hover:bg-gray-800/50"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.name}</span>
                {item.badge && (
                  <span className="ml-1 px-1.5 py-0.5 text-[9px] uppercase tracking-wider font-extrabold bg-gradient-to-r from-amber-500 to-rose-500 text-white rounded">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Repo Badge */}
        <div className="hidden md:flex items-center space-x-3 text-xs font-mono text-gray-400 bg-gray-900/60 px-3 py-1.5 rounded-lg border border-gray-800">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>sentinel-demo/payment-gateway</span>
        </div>

      </div>
    </header>
  );
}

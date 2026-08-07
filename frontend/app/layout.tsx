import "./globals.css";
import Navbar from "./components/Navbar";

export const metadata = {
  title: "SentinelReview — Multi-Agent Code Review & Triage System",
  description: "Prioritizes developer pull request reviews using PyDriller git history mining and LLM multi-agent scans.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-dark-900 text-gray-100 min-h-screen flex flex-col antialiased">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
        <footer className="border-t border-gray-800 py-6 text-center text-xs text-gray-500 font-mono">
          SentinelReview Multi-Agent Triage Engine • LangGraph & PyDriller Integration
        </footer>
      </body>
    </html>
  );
}

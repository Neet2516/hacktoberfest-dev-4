export default function HomePage() {
  const agents = [
    {
      id: "coordinator",
      name: "Resurrection Coordinator",
      role: "Workflow Orchestration & Human Approval Gate",
      status: "Idle",
      badge: "Orchestrator",
    },
    {
      id: "archaeologist",
      name: "Repository Archaeologist",
      role: "AST Parsing & Historical Architecture Reconstruction",
      status: "Ready",
      badge: "Archaeology",
    },
    {
      id: "investigator",
      name: "Issue Investigator",
      role: "GitHub Issue Deduction & Repair Specifications",
      status: "Ready",
      badge: "Investigation",
    },
    {
      id: "repairer",
      name: "Ghost Repairer",
      role: "Minimal Git Patch Generation & Architecture Preservation",
      status: "Ready",
      badge: "Repair",
    },
    {
      id: "reviewer",
      name: "Adversarial Reviewer",
      role: "Independent Regression & Security Vulnerability Audit",
      status: "Ready",
      badge: "Review",
    },
    {
      id: "tester",
      name: "Test Engineer",
      role: "Isolated Rootless Docker Test Verification",
      status: "Ready",
      badge: "Testing",
    },
  ];

  return (
    <main className="max-w-6xl mx-auto px-6 py-12">
      <header className="mb-12 border-b border-slate-800 pb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-extrabold tracking-tight text-white mb-2">
              SPECTER <span className="text-blue-500">.</span>
            </h1>
            <p className="text-slate-400 text-lg">
              The Ghost Maintainer — Every abandoned repository deserves another life.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-950 text-blue-400 border border-blue-800">
              Hacktoberfest 2026
            </span>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-950 text-emerald-400 border border-emerald-800">
              System Online
            </span>
          </div>
        </div>
      </header>

      <section className="mb-12">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl">
          <h2 className="text-xl font-bold text-white mb-4">Ingest Repository</h2>
          <div className="flex gap-4">
            <input
              type="text"
              placeholder="https://github.com/owner/repository"
              className="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
              readOnly
            />
            <button
              disabled
              className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2 rounded-lg opacity-75 cursor-not-allowed"
            >
              Analyze Codebase
            </button>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            Repositories are cloned into isolated workspaces with network disabled during execution.
          </p>
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-bold text-white mb-6">Autonomous Maintenance Agents</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent) => (
            <div
              key={agent.id}
              className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition"
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-mono uppercase tracking-wider text-slate-400 bg-slate-800/80 px-2 py-0.5 rounded">
                  {agent.badge}
                </span>
                <span className="text-xs font-medium text-emerald-400 flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  {agent.status}
                </span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-1">{agent.name}</h3>
              <p className="text-sm text-slate-400">{agent.role}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

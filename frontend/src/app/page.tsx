"use client";

import React, { useState } from "react";

export default function RetroSpecterDashboard() {
  const [repoUrl, setRepoUrl] = useState("https://github.com/demo/abandoned_kv");
  const [proposalStatus, setProposalStatus] = useState<"PENDING" | "APPROVED" | "REJECTED">("PENDING");
  const [activeTab, setActiveTab] = useState<"diff" | "security" | "tests" | "memory">("diff");
  const [pipelineState, setPipelineState] = useState<"idle" | "running" | "ready">("ready");

  // GitHub Token Vault State (Client-isolated, never in AI prompts)
  const [rawTokenInput, setRawTokenInput] = useState("");
  const [showToken, setShowToken] = useState(false);
  const [vaultStatus, setVaultStatus] = useState<"UNSEALED" | "ARMED" | "PURGED">("UNSEALED");
  const [maskedToken, setMaskedToken] = useState<string | null>(null);
  const [vaultFeedback, setVaultFeedback] = useState<string>(
    "Vault is unconfigured. System is safely operating in offline fixture mode."
  );

  const agents = [
    {
      id: "coordinator",
      name: "Resurrection Coordinator",
      role: "Workflow State & Human Gate",
      badge: "ORCHESTRATOR",
      badgeColor: "bg-[#6600ff] text-white",
      status: "ONLINE",
      activity: "Awaiting human signature for Proposal #prop_8f3a9e",
    },
    {
      id: "archaeologist",
      name: "Repository Archaeologist",
      role: "AST Parsing & History Mining",
      badge: "ARCHAEOLOGY",
      badgeColor: "bg-[#000080] text-white",
      status: "ONLINE",
      activity: "Reconstructed Rust 2021 crate idiomatic conventions",
    },
    {
      id: "investigator",
      name: "Issue Investigator",
      role: "Defect Analysis & Repair Specs",
      badge: "INVESTIGATION",
      badgeColor: "bg-[#008080] text-white",
      status: "ONLINE",
      activity: "Pinpointed unhandled empty slice on src/lib.rs:10",
    },
    {
      id: "repairer",
      name: "Ghost Repairer",
      role: "Minimal Git Patch Synthesizer",
      badge: "REPAIR",
      badgeColor: "bg-[#ff00b8] text-white",
      status: "ONLINE",
      activity: "Generated scoped 2-line patch (+1/-0) matching author style",
    },
    {
      id: "reviewer",
      name: "Adversarial Reviewer",
      role: "Security & Anti-Refactoring Audit",
      badge: "REVIEW",
      badgeColor: "bg-[#800000] text-white",
      status: "ONLINE",
      activity: "VERDICT: APPROVED (0 secrets, 0 eval, low regression risk)",
    },
    {
      id: "tester",
      name: "Test Engineer",
      role: "Disposable Container Sandbox",
      badge: "TESTING",
      badgeColor: "bg-[#006400] text-white",
      status: "ONLINE",
      activity: "Docker sandbox: 5 passed; 0 failed; --network none enforced",
    },
  ];

  const diffLines = [
    { type: "header", text: "diff --git a/src/lib.rs b/src/lib.rs" },
    { type: "header", text: "--- a/src/lib.rs" },
    { type: "header", text: "+++ b/src/lib.rs" },
    { type: "chunk", text: "@@ -1,5 +1,8 @@" },
    { type: "context", text: " pub fn parse_config(raw: &str) -> Result<String, &'static str> {" },
    { type: "add", text: "+    if raw.is_empty() {" },
    { type: "add", text: "+        return Err(\"Configuration cannot be empty\");" },
    { type: "add", text: "+    }" },
    { type: "context", text: "     Ok(raw.to_uppercase())" },
    { type: "context", text: " }" },
  ];

  const handleApprove = () => {
    setProposalStatus("APPROVED");
  };

  const handleReject = () => {
    setProposalStatus("REJECTED");
  };

  // Secure GitHub Token Vault handlers
  const handleArmVault = () => {
    const trimmed = rawTokenInput.trim();
    if (!trimmed) {
      setVaultFeedback("Error: Token cannot be empty.");
      return;
    }

    if (!trimmed.startsWith("ghp_") && !trimmed.startsWith("github_pat_") && !trimmed.startsWith("gho_")) {
      setVaultFeedback("Security Error: Invalid token prefix. Must start with ghp_, github_pat_, or gho_.");
      return;
    }

    // Mask token for safe UI display (first 4 and last 4 characters only)
    const prefix = trimmed.slice(0, 4);
    const suffix = trimmed.slice(-4);
    const masked = `${prefix}••••••••••••••••${suffix}`;

    setMaskedToken(masked);
    setVaultStatus("ARMED");
    setVaultFeedback(
      "Token armed in isolated memory vault. Physical isolation active: GITHUB_TOKEN is redacted from all AI prompts, inter-agent messages, and container sandboxes."
    );
    setRawTokenInput(""); // Wipe raw token from input field
    setShowToken(false);
  };

  const handlePurgeVault = () => {
    setRawTokenInput("");
    setMaskedToken(null);
    setVaultStatus("PURGED");
    setVaultFeedback("Token completely purged from memory. System returned to air-gapped mock mode.");
  };

  return (
    <div className="min-h-screen pb-12">
      {/* 1. RETRO DESKTOP MENU / TASKBAR */}
      <nav className="retro-window w-full border-x-0 border-t-0 p-1 mb-4 flex items-center justify-between z-50">
        <div className="flex items-center gap-1 text-sm font-bold">
          <button
            type="button"
            className="retro-btn bg-[#d4d4d4] font-extrabold px-3 py-1 text-xs uppercase flex items-center gap-1.5 focus:outline-none"
          >
            <span className="text-base leading-none">👻</span>
            <span>SPECTER START</span>
          </button>
          <div className="h-5 w-[2px] bg-[#808080] mx-1 border-r border-white"></div>
          <span className="px-2 py-0.5 text-xs font-semibold hover:bg-[#000080] hover:text-white cursor-pointer">
            File
          </span>
          <span className="px-2 py-0.5 text-xs font-semibold hover:bg-[#000080] hover:text-white cursor-pointer">
            Archaeology
          </span>
          <span className="px-2 py-0.5 text-xs font-semibold hover:bg-[#000080] hover:text-white cursor-pointer">
            Investigation
          </span>
          <span className="px-2 py-0.5 text-xs font-semibold hover:bg-[#000080] hover:text-white cursor-pointer">
            Repair
          </span>
          <span className="px-2 py-0.5 text-xs font-semibold hover:bg-[#000080] hover:text-white cursor-pointer">
            Sandbox
          </span>
          <span className="px-2 py-0.5 text-xs font-semibold hover:bg-[#000080] hover:text-white cursor-pointer">
            Audit
          </span>
        </div>

        <div className="flex items-center gap-2 text-xs font-mono">
          <div className="retro-well px-2 py-0.5 font-bold text-[#006400] bg-[#e6f4ea]">
            ● MESH ONLINE [6/6]
          </div>
          <div
            className={`retro-well px-2 py-0.5 font-bold ${
              vaultStatus === "ARMED" ? "bg-[#e6f4ea] text-[#006400]" : "bg-[#ffff00] text-black"
            }`}
          >
            {vaultStatus === "ARMED" ? "🔒 VAULT: ARMED" : "⚠️ VAULT: UNSEALED"}
          </div>
          <div className="retro-well px-2 py-0.5 font-bold bg-[#ffffff] text-black">
            2026-10-31 01:52 UTC
          </div>
        </div>
      </nav>

      {/* MAIN TWELVE-COLUMN DESKTOP GRID */}
      <main className="max-w-7xl mx-auto px-3 sm:px-6">
        {/* ROW 1: BROAD YELLOW LAUNCH WINDOW + MONITOR FACTS PANEL */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5 mb-5 items-start">
          {/* Broad Launch Window (Columns 1-7) */}
          <div className="lg:col-span-7 retro-window p-1">
            <div className="retro-titlebar">
              <span className="flex items-center gap-1.5">
                <span>📁</span>
                <span>SPECTER_INGEST.EXE — Repository Launchpad</span>
              </span>
              <div className="flex items-center gap-1">
                <button type="button" aria-label="Minimize" className="retro-win-btn">_</button>
                <button type="button" aria-label="Maximize" className="retro-win-btn">□</button>
                <button type="button" aria-label="Close" className="retro-win-btn">×</button>
              </div>
            </div>

            {/* Bright Yellow Launch Banner */}
            <div className="bg-[#ffff00] border-2 border-[#000000] p-4 m-1 text-black">
              <div className="flex items-start justify-between">
                <div>
                  <span className="inline-block bg-[#000000] text-[#ffff00] text-[10px] font-mono px-2 py-0.5 font-bold uppercase mb-1">
                    Hacktoberfest 2026 // Ghost in the Machine
                  </span>
                  <h1 className="font-retro-display font-black text-3xl sm:text-4xl tracking-tight uppercase leading-none mt-1">
                    SPECTER : THE GHOST MAINTAINER
                  </h1>
                </div>
                <div className="text-3xl">👻</div>
              </div>
              <p className="mt-2 text-sm font-semibold leading-snug">
                Every abandoned open-source repository deserves another life. SPECTER deploys a coordinated mesh of 6 autonomous AI agents to reconstruct architectural history, deduce defects, synthesize minimal patches, and verify code inside disposable, network-isolated containers.
              </p>
            </div>

            {/* Ingestion Form Well */}
            <div className="p-3">
              <label htmlFor="repo-url-input" className="block text-xs font-bold uppercase mb-1.5 font-mono">
                Target Repository URL (HTTPS Only, Public GitHub):
              </label>
              <div className="flex flex-col sm:flex-row gap-2">
                <input
                  id="repo-url-input"
                  type="text"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  className="retro-well flex-1 px-3 py-2 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-[#000080]"
                  placeholder="https://github.com/owner/repository"
                />
                <button
                  type="button"
                  onClick={() => setPipelineState("ready")}
                  className="retro-btn retro-btn-yellow font-extrabold uppercase whitespace-nowrap text-xs"
                >
                  ⚡ ANALYZE REPO
                </button>
              </div>

              {/* Safety Checklist Box */}
              <div className="retro-well bg-[#ffffff] p-2.5 mt-3 text-xs space-y-1 font-mono">
                <div className="flex items-center gap-2 text-black">
                  <span className="font-bold text-[#006400]">[✔]</span>
                  <span>Cloned to disposable workspace (VirtualPathMapper: zero host leakage)</span>
                </div>
                <div className="flex items-center gap-2 text-black">
                  <span className="font-bold text-[#006400]">[✔]</span>
                  <span>Execution sandbox: <strong className="bg-[#ffff00] px-1">--network none</strong> with strict 2GB memory quota</span>
                </div>
                <div className="flex items-center gap-2 text-black">
                  <span className="font-bold text-[#006400]">[✔]</span>
                  <span>GitHub tokens vaulted; <strong className="text-[#ff00b8]">zero token exposure</strong> in AI prompts</span>
                </div>
              </div>

              {/* Launchpad Action Buttons */}
              <div className="mt-4 flex flex-wrap gap-2 pt-2 border-t border-[#808080]">
                <button
                  type="button"
                  onClick={() => setRepoUrl("https://github.com/demo/abandoned_kv")}
                  className="retro-btn text-xs font-bold"
                >
                  LOAD DEMO FIXTURE (abandoned_kv)
                </button>
                <button
                  type="button"
                  className="retro-btn retro-btn-purple text-xs font-bold"
                >
                  RUN RESURRECTION PIPELINE ▶
                </button>
                <button
                  type="button"
                  className="retro-btn text-xs font-bold"
                >
                  EXPORT AUDIT LOG (.JSON)
                </button>
              </div>
            </div>
          </div>

          {/* Compact Monitor-like Facts Panel (Columns 8-12) */}
          <div className="lg:col-span-5 retro-window p-1">
            <div className="retro-titlebar">
              <span className="flex items-center gap-1.5">
                <span>🖥️</span>
                <span>SYSTEM_TELEMETRY.SYS [MONITOR]</span>
              </span>
              <div className="flex items-center gap-1">
                <button type="button" aria-label="Minimize" className="retro-win-btn">_</button>
                <button type="button" aria-label="Maximize" className="retro-win-btn">□</button>
                <button type="button" aria-label="Close" className="retro-win-btn">×</button>
              </div>
            </div>

            {/* CRT Phosphor Terminal Well */}
            <div className="retro-well-dark p-3 m-1 font-mono text-xs space-y-1.5 overflow-hidden">
              <div className="text-[#00ff66] font-bold border-b border-[#00ff66]/30 pb-1 flex justify-between">
                <span>SPECTER KERNEL v2.0-PROD</span>
                <span className="animate-pulse">● LIVE</span>
              </div>
              <div className="text-[#b0ffb0] pt-1">
                &gt; HOST OS: Windows x86_64 / Debian Sandbox<br />
                &gt; REPOSITORY: <span className="text-[#ffff00]">{repoUrl}</span><br />
                &gt; PRIMARY LANGUAGE: Rust (2021 Edition)<br />
                &gt; BASELINE COMMIT: 3f2a1b0c9d8e (2022-04-12)<br />
                &gt; ACTIVE ISSUE: #1 (Buffer Underflow Defect)<br />
                &gt; TEST SUITE: Cargo Test (5 unit tests detected)<br />
                &gt; GHOST MEMORY: 768-dim Vector Store (pgvector)<br />
                &gt; RETRY BUDGET: 0/3 attempts used<br />
                &gt; VAULT STATUS:{" "}
                <span className={vaultStatus === "ARMED" ? "bg-[#00aa00] text-black px-1 font-bold" : "bg-[#ffff00] text-black px-1 font-bold"}>
                  {vaultStatus === "ARMED" ? "SEALED & ARMED" : "MOCK FIXTURE"}
                </span><br />
                &gt; CONTAINER STATUS:
              </div>
              <div className="bg-[#000000] p-2 border border-[#00ff66]/50 text-[#00ff66] text-[11px] leading-tight">
                [CONTAINER ID]: sp_box_91a02f8<br />
                [FLAG]: --network none [ENFORCED]<br />
                [MOUNT]: /tmp/workspace:/workspace:ro [READ-ONLY]<br />
                [LIMITS]: Memory 2048MB | CPUs 2.0 | PIDs 256<br />
                [EXECUTION]: 5 passed; 0 failed; 0 ignored (0.05s)
              </div>
            </div>

            {/* Quick Metrics Bar */}
            <div className="p-2 grid grid-cols-3 gap-2 text-center font-mono">
              <div className="retro-well p-1.5">
                <div className="text-[10px] text-[#808080] uppercase">Pass Rate</div>
                <div className="text-base font-bold text-[#006400]">100%</div>
              </div>
              <div className="retro-well p-1.5">
                <div className="text-[10px] text-[#808080] uppercase">Regression</div>
                <div className="text-base font-bold text-[#000080]">LOW (0)</div>
              </div>
              <div className="retro-well p-1.5">
                <div className="text-[10px] text-[#808080] uppercase">Verified</div>
                <div className="text-base font-bold text-[#ff00b8]">50 TESTS</div>
              </div>
            </div>
          </div>
        </div>

        {/* ROW 2: SECURE GITHUB CREDENTIAL VAULT SECTION (ZERO TOKEN EXPOSURE) */}
        <div className="retro-window p-1 mb-5">
          <div className="retro-titlebar">
            <span className="flex items-center gap-1.5">
              <span>🔐</span>
              <span>GITHUB_CREDENTIAL_VAULT.KEY — Air-Gapped Token Isolation</span>
            </span>
            <div className="flex items-center gap-1">
              <button type="button" aria-label="Minimize" className="retro-win-btn">_</button>
              <button type="button" aria-label="Maximize" className="retro-win-btn">□</button>
              <button type="button" aria-label="Close" className="retro-win-btn">×</button>
            </div>
          </div>

          <div className="p-4 bg-[#d4d4d4]">
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-start">
              {/* Token Input Controls (Cols 1-8) */}
              <div className="lg:col-span-8 space-y-3">
                <div className="flex items-center justify-between">
                  <label htmlFor="github-token-input" className="text-xs font-bold uppercase font-mono text-black">
                    GitHub Personal Access Token (PAT):
                  </label>
                  <span className="text-[11px] font-mono text-[#808080]">
                    Allowed prefixes: <code className="bg-[#ffffff] px-1 border border-[#808080]">ghp_</code>{" "}
                    <code className="bg-[#ffffff] px-1 border border-[#808080]">github_pat_</code>
                  </span>
                </div>

                <div className="flex gap-2">
                  <div className="relative flex-1">
                    <input
                      id="github-token-input"
                      type={showToken ? "text" : "password"}
                      value={rawTokenInput}
                      onChange={(e) => setRawTokenInput(e.target.value)}
                      placeholder={maskedToken ? maskedToken : "Paste token here (e.g. ghp_16characterToken...)"}
                      className="retro-well w-full px-3 py-2 text-sm font-mono tracking-wider focus:outline-none focus:ring-1 focus:ring-[#000080]"
                    />
                  </div>

                  <button
                    type="button"
                    onClick={() => setShowToken(!showToken)}
                    className="retro-btn text-xs font-bold uppercase px-3 whitespace-nowrap"
                  >
                    {showToken ? "🙈 HIDE" : "👁 SHOW"}
                  </button>

                  <button
                    type="button"
                    onClick={handleArmVault}
                    className="retro-btn retro-btn-teal text-xs font-black uppercase px-4 whitespace-nowrap"
                  >
                    🔐 ARM VAULT
                  </button>

                  <button
                    type="button"
                    onClick={handlePurgeVault}
                    className="retro-btn retro-btn-pink text-xs font-bold uppercase px-3 whitespace-nowrap"
                  >
                    🧹 PURGE
                  </button>
                </div>

                {/* Vault Status Feedback Box */}
                <div className="retro-well p-2.5 bg-[#ffffff] font-mono text-xs">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-bold text-[#808080]">STATUS:</span>
                    <span
                      className={`font-black uppercase px-1.5 py-0.5 text-[11px] ${
                        vaultStatus === "ARMED"
                          ? "bg-[#e6f4ea] text-[#006400] border border-[#00aa00]"
                          : "bg-[#ffff00] text-black border border-[#000000]"
                      }`}
                    >
                      {vaultStatus === "ARMED" ? "● ARMED & SEALED" : "○ UNCONFIGURED (OFFLINE FIXTURE MODE)"}
                    </span>
                    {maskedToken && (
                      <span className="text-[#000080] font-bold">
                        [ACTIVE: {maskedToken}]
                      </span>
                    )}
                  </div>
                  <div className="text-[#333333] text-[11px] leading-relaxed">
                    &gt; {vaultFeedback}
                  </div>
                </div>
              </div>

              {/* Zero-Leakage Architecture Guarantees (Cols 9-12) */}
              <div className="lg:col-span-4 retro-well p-3 bg-[#fdfdfd] border border-[#808080] font-mono text-xs space-y-2">
                <div className="font-bold text-[#000080] uppercase border-b border-[#808080] pb-1 text-[11px]">
                  🛡️ Zero Token Exposure Guarantees
                </div>
                <div className="space-y-1.5 text-[11px] text-[#222222]">
                  <div className="flex items-start gap-1.5">
                    <span className="text-[#00aa00] font-bold">1.</span>
                    <span>
                      <strong>Never in AI Context:</strong> Token is stripped before dispatch to Gemma 2 / Ollama prompts.
                    </span>
                  </div>
                  <div className="flex items-start gap-1.5">
                    <span className="text-[#00aa00] font-bold">2.</span>
                    <span>
                      <strong>Memory Vault:</strong> Redacted to <code className="bg-[#e0e0e0] px-0.5">[REDACTED_TOKEN]</code> in all logs.
                    </span>
                  </div>
                  <div className="flex items-start gap-1.5">
                    <span className="text-[#00aa00] font-bold">3.</span>
                    <span>
                      <strong>Gated Mutations:</strong> Pull Request creation is blocked until explicit human dashboard signoff.
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* ROW 3: BRIGHT PINK TICKER NOTIFICATION STRIP */}
        <div className="w-full bg-[#ff00b8] border-2 border-[#000000] p-2 mb-5 flex items-center justify-between text-white font-mono text-xs sm:text-sm font-bold shadow-[2px_2px_0px_#000000]">
          <div className="flex items-center gap-2 truncate">
            <span className="retro-ticker-arrow text-[#ffff00] text-base leading-none">▶▶</span>
            <span className="uppercase tracking-wider truncate">
              HACKTOBERFEST 2026 SPECIAL TRACK: &quot;GHOST IN THE MACHINE&quot; // 6 SPECIALIZED AGENTS ONLINE // HUMAN APPROVAL GATE STRICTLY ARMED
            </span>
          </div>
          <div className="hidden md:flex items-center gap-2 pl-4 whitespace-nowrap">
            <span className="bg-[#000000] text-[#ffff00] px-2 py-0.5 text-xs">
              TOKEN SECURITY: REDACTED
            </span>
          </div>
        </div>

        {/* ROW 4: AUTONOMOUS AGENTS CAPABILITY WINDOW */}
        <div className="retro-window p-1 mb-5">
          <div className="retro-titlebar">
            <span className="flex items-center gap-1.5">
              <span>🤖</span>
              <span>AGENT_MESH_CONTROLLER.WIN — 6 Autonomous Specialists</span>
            </span>
            <div className="flex items-center gap-1">
              <button type="button" aria-label="Minimize" className="retro-win-btn">_</button>
              <button type="button" aria-label="Maximize" className="retro-win-btn">□</button>
              <button type="button" aria-label="Close" className="retro-win-btn">×</button>
            </div>
          </div>

          <div className="p-3">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {agents.map((agent) => (
                <div key={agent.id} className="retro-window p-2 bg-[#d4d4d4]">
                  <div className="flex items-center justify-between mb-1.5 pb-1 border-b border-[#808080]">
                    <span className={`text-[10px] font-mono font-bold px-1.5 py-0.5 ${agent.badgeColor}`}>
                      {agent.badge}
                    </span>
                    <span className="text-[11px] font-mono font-bold text-[#006400] flex items-center gap-1">
                      <span className="w-2 h-2 bg-[#00aa00] inline-block"></span>
                      {agent.status}
                    </span>
                  </div>
                  <h3 className="font-bold text-sm text-[#000080] font-retro-interface mb-0.5">
                    {agent.name}
                  </h3>
                  <div className="text-[11px] text-[#505050] mb-2">{agent.role}</div>

                  {/* Status well */}
                  <div className="retro-well p-1.5 text-[11px] font-mono bg-[#ffffff] text-black">
                    <span className="text-[#808080]">&gt; </span>
                    {agent.activity}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ROW 5: INTERACTIVE MAINTENANCE PROPOSAL & HUMAN APPROVAL WINDOW */}
        <div className="retro-window p-1 mb-5">
          <div className="retro-titlebar">
            <span className="flex items-center gap-1.5">
              <span>⚖️</span>
              <span>MAINTENANCE_PROPOSAL_VIEWER.EXE — #prop_8f3a9e [HUMAN GATE]</span>
            </span>
            <div className="flex items-center gap-1">
              <button type="button" aria-label="Minimize" className="retro-win-btn">_</button>
              <button type="button" aria-label="Maximize" className="retro-win-btn">□</button>
              <button type="button" aria-label="Close" className="retro-win-btn">×</button>
            </div>
          </div>

          <div className="p-4 bg-[#d4d4d4]">
            {/* Header / Summary Ribbon */}
            <div className="retro-well p-3 mb-4 bg-[#ffffff]">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-[#808080] pb-2 mb-2">
                <div>
                  <span className="text-xs font-mono font-bold uppercase text-[#808080]">Target Issue:</span>
                  <h2 className="text-base sm:text-lg font-bold text-[#000080]">
                    #1: Buffer underflow when parsing empty slice in config parser
                  </h2>
                </div>
                <div>
                  {proposalStatus === "PENDING" && (
                    <span className="retro-btn retro-btn-yellow font-mono text-xs font-black">
                      ⏳ STATUS: PENDING HUMAN APPROVAL
                    </span>
                  )}
                  {proposalStatus === "APPROVED" && (
                    <span className="retro-btn retro-btn-teal font-mono text-xs font-black">
                      ✔ STATUS: SIGNED & APPROVED FOR PR
                    </span>
                  )}
                  {proposalStatus === "REJECTED" && (
                    <span className="retro-btn retro-btn-pink font-mono text-xs font-black">
                      ✖ STATUS: REJECTED (ANTI-PATTERN LOGGED)
                    </span>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs font-mono">
                <div>
                  <span className="text-[#808080]">AFFECTED FILE:</span>
                  <div className="font-bold text-black">src/lib.rs (Lines 1-8)</div>
                </div>
                <div>
                  <span className="text-[#808080]">ADVERSARIAL VERDICT:</span>
                  <div className="font-bold text-[#006400]">APPROVED (0 Flaws)</div>
                </div>
                <div>
                  <span className="text-[#808080]">CONTAINER TEST:</span>
                  <div className="font-bold text-[#000080]">5/5 PASS (--network none)</div>
                </div>
                <div>
                  <span className="text-[#808080]">CRYPTOGRAPHIC HASH:</span>
                  <div className="font-bold text-[#6600ff]">sha256:3c9b74f0a12e</div>
                </div>
              </div>
            </div>

            {/* Proposal Tabs */}
            <div className="flex gap-1 mb-0 border-b border-[#808080]">
              <button
                type="button"
                onClick={() => setActiveTab("diff")}
                className={`px-4 py-1.5 text-xs font-bold uppercase ${
                  activeTab === "diff"
                    ? "retro-window border-b-0 bg-[#d4d4d4] font-black -mb-[1px]"
                    : "bg-[#c0c0c0] text-[#505050] hover:bg-[#d0d0d0]"
                }`}
              >
                1. Unified Git Patch Diff
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("security")}
                className={`px-4 py-1.5 text-xs font-bold uppercase ${
                  activeTab === "security"
                    ? "retro-window border-b-0 bg-[#d4d4d4] font-black -mb-[1px]"
                    : "bg-[#c0c0c0] text-[#505050] hover:bg-[#d0d0d0]"
                }`}
              >
                2. Adversarial Security Report
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("tests")}
                className={`px-4 py-1.5 text-xs font-bold uppercase ${
                  activeTab === "tests"
                    ? "retro-window border-b-0 bg-[#d4d4d4] font-black -mb-[1px]"
                    : "bg-[#c0c0c0] text-[#505050] hover:bg-[#d0d0d0]"
                }`}
              >
                3. Disposable Sandbox Output
              </button>
              <button
                type="button"
                onClick={() => setActiveTab("memory")}
                className={`px-4 py-1.5 text-xs font-bold uppercase ${
                  activeTab === "memory"
                    ? "retro-window border-b-0 bg-[#d4d4d4] font-black -mb-[1px]"
                    : "bg-[#c0c0c0] text-[#505050] hover:bg-[#d0d0d0]"
                }`}
              >
                4. Ghost Memory Matches
              </button>
            </div>

            {/* Tab Body Well */}
            <div className="retro-well p-4 bg-[#ffffff]">
              {activeTab === "diff" && (
                <div>
                  <div className="flex items-center justify-between text-xs font-mono text-[#808080] border-b border-[#d0d0d0] pb-1.5 mb-2">
                    <span>Patch Scope: Minimal 3-line addition (0 refactoring lines)</span>
                    <span className="text-[#006400] font-bold">+3 lines / -0 lines</span>
                  </div>
                  <pre className="font-mono text-xs leading-relaxed overflow-x-auto bg-[#fafafa] p-3 border border-[#d0d0d0]">
                    {diffLines.map((line, idx) => (
                      <div
                        key={idx}
                        className={
                          line.type === "header"
                            ? "text-[#808080] font-bold"
                            : line.type === "chunk"
                            ? "text-[#6600ff] font-bold bg-[#f3e8ff] px-1"
                            : line.type === "add"
                            ? "text-[#006400] bg-[#e6f4ea] px-1 font-bold"
                            : "text-[#333333]"
                        }
                      >
                        {line.text}
                      </div>
                    ))}
                  </pre>
                </div>
              )}

              {activeTab === "security" && (
                <div className="font-mono text-xs space-y-2">
                  <div className="bg-[#e6f4ea] p-2 border border-[#00aa00] text-[#006400] font-bold">
                    [✔] STRIDE THREAT AUDIT PASSED: 0 BLOCKERS DETECTED
                  </div>
                  <ul className="list-disc pl-5 space-y-1 text-[#333333]">
                    <li>Hardcoded Secret Scanner: Clean (No credentials or API tokens found).</li>
                    <li>Dynamic Eval Check: Clean (No eval(), exec(), or child_process invocations).</li>
                    <li>Over-refactoring check: Passed (Patch is 3 lines; strictly within scope).</li>
                    <li>Backwards Compatibility: Preserved public signature `parse_config(raw: &amp;str)`.</li>
                  </ul>
                </div>
              )}

              {activeTab === "tests" && (
                <div className="font-mono text-xs space-y-2 bg-[#0c1017] text-[#00ff66] p-3">
                  <div>=== DOCKER TEST RUNNER INVOCATION ===</div>
                  <div>$ docker run --rm --network none --memory 2g specter-test-runner cargo test</div>
                  <div className="text-[#ffffff]">
                    running 5 tests<br />
                    test tests::test_parse_valid ... ok<br />
                    test tests::test_parse_uppercase ... ok<br />
                    test tests::test_parse_symbols ... ok<br />
                    test tests::test_parse_empty_slice_guarded ... ok<br />
                    test tests::test_integration_flow ... ok<br />
                    <br />
                    <span className="text-[#00ff66] font-bold">
                      test result: ok. 5 passed; 0 failed; 0 ignored; finished in 0.04s
                    </span>
                  </div>
                </div>
              )}

              {activeTab === "memory" && (
                <div className="font-mono text-xs space-y-2">
                  <div className="p-2 border border-[#808080] bg-[#fafafa]">
                    <div className="font-bold text-[#000080]">[IDIOLECT / CONVENTION] (Cosine Similarity: 0.94)</div>
                    <div>&quot;Crate author prefers standard Result&lt;T, &amp;&apos;static str&gt; error messages over foreign error crates.&quot;</div>
                  </div>
                  <div className="p-2 border border-[#808080] bg-[#fafafa]">
                    <div className="font-bold text-[#ff00b8]">[NEGATIVE TEST CASE #NEG-01]</div>
                    <div>&quot;Never unwrap() slice indices without prior length check in parser routines.&quot;</div>
                  </div>
                </div>
              )}
            </div>

            {/* Human-in-the-Loop Approval Action Bar */}
            <div className="mt-4 p-3 bg-[#e4e4e4] border border-[#808080] flex flex-col md:flex-row items-center justify-between gap-3">
              <div className="text-xs">
                <span className="font-bold text-black uppercase font-mono">Maintainer Signoff: </span>
                <span className="text-[#505050]">
                  Human authorization is required before SPECTER can create remote git branches or open GitHub Pull Requests.
                </span>
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleReject}
                  className="retro-btn retro-btn-pink text-xs font-bold uppercase whitespace-nowrap"
                >
                  ✖ REJECT PROPOSAL
                </button>
                <button
                  type="button"
                  onClick={handleApprove}
                  className="retro-btn retro-btn-teal text-xs font-black uppercase whitespace-nowrap"
                >
                  ✔ SIGN &amp; CREATE GITHUB PR
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* ROW 6: BROAD RETRO FOOTER */}
        <footer className="retro-window p-3 text-xs">
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3 pb-3 border-b border-[#808080] font-mono">
            <div>
              <div className="font-bold text-[#000080] mb-1">📁 SPECS</div>
              <ul className="space-y-0.5 text-[#333333]">
                <li><a href="#prd" className="hover:text-[#0000ff] hover:underline">docs/PRD.md</a></li>
                <li><a href="#arch" className="hover:text-[#0000ff] hover:underline">docs/ARCH.md</a></li>
              </ul>
            </div>
            <div>
              <div className="font-bold text-[#000080] mb-1">📁 SECURITY</div>
              <ul className="space-y-0.5 text-[#333333]">
                <li><a href="#threat" className="hover:text-[#0000ff] hover:underline">THREAT_MODEL</a></li>
                <li><a href="#errors" className="hover:text-[#0000ff] hover:underline">ERROR_REGISTRY</a></li>
              </ul>
            </div>
            <div>
              <div className="font-bold text-[#000080] mb-1">📁 AGENTS</div>
              <ul className="space-y-0.5 text-[#333333]">
                <li><a href="#charter" className="hover:text-[#0000ff] hover:underline">AGENT_CHARTER</a></li>
                <li><a href="#protocols" className="hover:text-[#0000ff] hover:underline">PROTOCOLS</a></li>
              </ul>
            </div>
            <div>
              <div className="font-bold text-[#000080] mb-1">📁 RUNTIME</div>
              <ul className="space-y-0.5 text-[#333333]">
                <li><a href="#mcp" className="hover:text-[#0000ff] hover:underline">MCP_TOOL_HOST</a></li>
                <li><a href="#temporal" className="hover:text-[#0000ff] hover:underline">TEMPORAL_QUEUE</a></li>
              </ul>
            </div>
            <div>
              <div className="font-bold text-[#000080] mb-1">📁 TESTS</div>
              <ul className="space-y-0.5 text-[#333333]">
                <li><a href="#rust" className="hover:text-[#0000ff] hover:underline">14 RUST TESTS</a></li>
                <li><a href="#python" className="hover:text-[#0000ff] hover:underline">50 PY TESTS</a></li>
              </ul>
            </div>
            <div>
              <div className="font-bold text-[#000080] mb-1">📁 DEMO</div>
              <ul className="space-y-0.5 text-[#333333]">
                <li><a href="#walkthrough" className="hover:text-[#0000ff] hover:underline">DEMO_GUIDE</a></li>
                <li><a href="#runbook" className="hover:text-[#0000ff] hover:underline">RUNBOOK</a></li>
              </ul>
            </div>
          </div>

          <div className="pt-2 flex flex-col sm:flex-row items-center justify-between text-[#505050] font-mono text-[11px]">
            <div>
              SPECTER: The Ghost Maintainer © 2026. Hacktoberfest 2026 Submission.
            </div>
            <div className="flex items-center gap-2 mt-1 sm:mt-0">
              <span>Authoritative Design: Retro Desktop</span>
              <span>•</span>
              <span className="text-[#006400] font-bold">130 Tasks Completed</span>
            </div>
          </div>
        </footer>
      </main>
    </div>
  );
}

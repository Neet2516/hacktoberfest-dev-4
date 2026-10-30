# SPECTER Dependency Graph

> Visual representation of all task dependencies, epic groupings, critical path, and parallel execution tracks.

---

## Legend

```
[SPECTER-NNN] ──► [SPECTER-MMM]   Task NNN must complete before MMM can start
════════════════                   Critical path segment
── ── ── ──                        Soft dependency (recommended order, not blocking)
```

---

## High-Level Epic Dependency Flow

```mermaid
flowchart TD
    E01["EPIC 01\nProject Foundation\n(001-010)"]
    E02["EPIC 02\nBackend Infrastructure\n(011-020)"]
    E03["EPIC 03\nRepository Ingestion\n(021-027)"]
    E04["EPIC 04\nRepository Archaeology\n(028-034)"]
    E05["EPIC 05\nGitHub Integration\n(035-041)"]
    E06["EPIC 06\nAI Agent Runtime\n(042-048)"]
    E07["EPIC 07\nAgent Communication\n(049-054)"]
    E08["EPIC 08\nGhost Memory\n(055-061)"]
    E09["EPIC 09\nIssue Investigation\n(062-067)"]
    E10["EPIC 10\nCode Repair\n(068-073)"]
    E11["EPIC 11\nAdversarial Review\n(074-079)"]
    E12["EPIC 12\nTest Execution\n(080-086)"]
    E13["EPIC 13\nWorkflow Orchestration\n(087-093)"]
    E14["EPIC 14\nHuman Approval\n(094-099)"]
    E15["EPIC 15\nFrontend Dashboard\n(100-110)"]
    E16["EPIC 16\nSecurity\n(111-117)"]
    E17["EPIC 17\nObservability\n(118-124)"]
    E18["EPIC 18\nDeployment\n(125-130)"]

    E01 --> E02
    E01 --> E03
    E01 --> E05
    E01 --> E06
    E01 --> E15
    E02 --> E03
    E02 --> E07
    E02 --> E08
    E03 --> E04
    E03 --> E16
    E05 --> E03
    E06 --> E04
    E06 --> E07
    E06 --> E09
    E04 --> E09
    E07 --> E09
    E08 --> E09
    E09 --> E10
    E10 --> E11
    E10 --> E12
    E11 --> E13
    E12 --> E13
    E13 --> E14
    E14 --> E15
    E01 --> E17
    E13 --> E17
    E14 --> E18
    E17 --> E18
```

---

## Critical Path

The **critical path** is the longest chain of sequential dependencies. Any delay on the critical path delays the entire project.

```
SPECTER-001 ──► SPECTER-005 ──► SPECTER-011 ──► SPECTER-012
    ──► SPECTER-013 ──► SPECTER-024 ──► SPECTER-023
    ──► SPECTER-028 ──► SPECTER-032 ──► SPECTER-033
    ──► SPECTER-042 ──► SPECTER-043 ──► SPECTER-062
    ──► SPECTER-065 ──► SPECTER-066 ──► SPECTER-068
    ──► SPECTER-069 ──► SPECTER-071 ──► SPECTER-072
    ──► SPECTER-074 ──► SPECTER-077 ──► SPECTER-087
    ──► SPECTER-088 ──► SPECTER-090 ──► SPECTER-094
    ──► SPECTER-096 ──► SPECTER-097 ──► SPECTER-098
```

**Estimated sequential depth:** 19 hops from project start to first GitHub PR.

---

## Parallel Execution Tracks

These tracks can proceed independently once EPIC 01 is complete:

### Track A — Backend + Database (sequential core)
```
001 → 005 → 011 → 012 → 013/014/015 → 016 → 017 → 018/019 → 020
```

### Track B — Frontend (parallel with backend)
```
003 → [wait for 016 API] → 100 → 101 → 102 → 103 → 104 → 105 → 106 → 107 → 108 → 109 → 110
```

### Track C — Agent Runtime + AI (parallel with backend)
```
002 → 042 → 043 → 044/045/046/047 → 048
                 ↓
              049 → 050/051/052/053 → 054
```

### Track D — Repository Pipeline (needs Track A + C)
```
021 → 022 → 023 → 024/025/026 → 027
028 → 029/030/031 → 032 → 033 → 034
```

### Track E — GitHub Integration (parallel, needs 009)
```
040 → 035 → 036/037 → 041
```

### Track F — Agent Pipeline (needs Track C + D)
```
062 → 063/064 → 065 → 066 → 067
068 → 069 → 070/071 → 072 → 073
074 → 075/076 → 077 → 078 → 079
080 → 081/082 → 083 → 084 → 085 → 086
```

### Track G — Orchestration (needs Track F)
```
087 → 088 → 089/090/091 → 092 → 093
094 → 095 → 096 → 097 → 098 → 099
```

### Track H — Security (runs alongside every track)
```
111 (with 021)
112 (with 042)
113 (with 080)
114 (with 082)
115 (with 043)
116 (with 040)
117 (final security gate)
```

### Track I — Ghost Memory (parallel with Track D)
```
055 → 056 → 057/058 → 059/060 → 061
```

### Track J — Observability (parallel with Track G)
```
007 → 118 → 119/120 → 121 → 122/123/124
```

### Track K — Deployment + Docs (last)
```
125 → 126/127/128 → 129 → 130
```

---

## Detailed Dependency Graph — EPIC 01–06

```mermaid
flowchart TD
    S001["SPECTER-001\nRust Axum skeleton"]
    S002["SPECTER-002\nPython agent runtime"]
    S003["SPECTER-003\nNext.js frontend"]
    S004["SPECTER-004\nDocker Compose dev"]
    S005["SPECTER-005\nPostgreSQL + pgvector"]
    S006["SPECTER-006\nTemporal server"]
    S007["SPECTER-007\nOpenTelemetry"]
    S008["SPECTER-008\nCI/CD pipeline"]
    S009["SPECTER-009\nEnv/secrets mgmt"]
    S010["SPECTER-010\nError code registry"]
    S011["SPECTER-011\nPG connection pool"]
    S012["SPECTER-012\nDB migrations"]
    S013["SPECTER-013\nRepo entity CRUD"]
    S014["SPECTER-014\nTask entity state machine"]
    S015["SPECTER-015\nAgent output storage"]
    S016["SPECTER-016\nHealth endpoints"]
    S017["SPECTER-017\nAuth middleware"]
    S018["SPECTER-018\nRate limiting"]
    S019["SPECTER-019\nAudit log"]
    S020["SPECTER-020\nBackend integration tests"]
    S042["SPECTER-042\nOllama/Gemma client"]
    S043["SPECTER-043\nAgent base class"]

    S001 --> S004
    S002 --> S004
    S003 --> S004
    S004 --> S005
    S004 --> S006
    S004 --> S009
    S001 --> S007
    S002 --> S007
    S001 --> S008
    S002 --> S008
    S003 --> S008
    S001 --> S010
    S002 --> S010
    S001 --> S011
    S005 --> S011
    S011 --> S012
    S012 --> S013
    S012 --> S014
    S012 --> S015
    S011 --> S016
    S009 --> S017
    S011 --> S017
    S016 --> S018
    S017 --> S018
    S012 --> S019
    S017 --> S019
    S013 --> S020
    S014 --> S020
    S015 --> S020
    S016 --> S020
    S004 --> S042
    S002 --> S042
    S042 --> S043
```

---

## Detailed Dependency Graph — EPIC 07–10

```mermaid
flowchart TD
    S043["SPECTER-043\nAgent base class"]
    S049["SPECTER-049\nMessage schema"]
    S050["SPECTER-050\nMessage router"]
    S051["SPECTER-051\nMessage validation"]
    S052["SPECTER-052\nMessage persistence"]
    S053["SPECTER-053\nDelivery ACK"]
    S054["SPECTER-054\nComm protocol tests"]
    S055["SPECTER-055\nGhost Memory schema"]
    S056["SPECTER-056\nMemory writer"]
    S057["SPECTER-057\nFact/hypothesis tagging"]
    S058["SPECTER-058\nVector similarity search"]
    S059["SPECTER-059\nMemory query API"]
    S060["SPECTER-060\nMemory expiry/decay"]
    S061["SPECTER-061\nGhost Memory tests"]
    S062["SPECTER-062\nIssue Investigator agent"]
    S063["SPECTER-063\nAffected file identifier"]
    S064["SPECTER-064\nRoot cause analysis"]
    S065["SPECTER-065\nRepair spec generator"]
    S066["SPECTER-066\nInvestigation Report"]
    S067["SPECTER-067\nInvestigator tests"]
    S068["SPECTER-068\nGhost Repairer agent"]
    S069["SPECTER-069\nPatch generator"]
    S070["SPECTER-070\nArchitecture constraint"]
    S071["SPECTER-071\nPatch serializer"]
    S072["SPECTER-072\nPatch application"]
    S073["SPECTER-073\nRepairer tests"]

    S043 --> S049
    S049 --> S050
    S049 --> S051
    S049 --> S052
    S052 --> S053
    S049 --> S054
    S050 --> S054
    S051 --> S054
    S052 --> S054
    S055 --> S056
    S056 --> S057
    S055 --> S058
    S058 --> S059
    S056 --> S060
    S057 --> S060
    S055 --> S061
    S056 --> S061
    S057 --> S061
    S058 --> S061
    S043 --> S062
    S062 --> S063
    S062 --> S064
    S064 --> S065
    S065 --> S066
    S062 --> S067
    S063 --> S067
    S064 --> S067
    S065 --> S067
    S066 --> S067
    S043 --> S068
    S066 --> S068
    S068 --> S069
    S068 --> S070
    S069 --> S071
    S071 --> S072
    S068 --> S073
    S069 --> S073
    S070 --> S073
    S071 --> S073
    S072 --> S073
```

---

## Detailed Dependency Graph — EPIC 11–14

```mermaid
flowchart TD
    S071["SPECTER-071\nPatch serializer"]
    S074["SPECTER-074\nAdversarial Reviewer"]
    S075["SPECTER-075\nRegression detection"]
    S076["SPECTER-076\nSecurity scanner"]
    S077["SPECTER-077\nReview verdict schema"]
    S078["SPECTER-078\nCorrection request msg"]
    S079["SPECTER-079\nReviewer tests"]
    S080["SPECTER-080\nDocker container launcher"]
    S081["SPECTER-081\nResource limits"]
    S082["SPECTER-082\nNetwork isolation"]
    S083["SPECTER-083\nTest result parser"]
    S084["SPECTER-084\nTest Engineer agent"]
    S085["SPECTER-085\nVerification Report"]
    S086["SPECTER-086\nTest Engineer tests"]
    S087["SPECTER-087\nTemporal workflow def"]
    S088["SPECTER-088\nTemporal activities"]
    S089["SPECTER-089\nWorkflow state persistence"]
    S090["SPECTER-090\nResurrection Coordinator"]
    S091["SPECTER-091\nRetry policy"]
    S092["SPECTER-092\nFailure handling"]
    S093["SPECTER-093\nTemporal tests"]
    S094["SPECTER-094\nApproval gate"]
    S095["SPECTER-095\nApproval notification"]
    S096["SPECTER-096\nApproval recording"]
    S097["SPECTER-097\nBranch creation"]
    S098["SPECTER-098\nPR creation"]
    S099["SPECTER-099\nApproval tests"]

    S071 --> S074
    S074 --> S075
    S074 --> S076
    S075 --> S077
    S076 --> S077
    S077 --> S078
    S074 --> S079
    S075 --> S079
    S076 --> S079
    S077 --> S079
    S078 --> S079
    S080 --> S081
    S080 --> S082
    S080 --> S083
    S080 --> S084
    S083 --> S084
    S084 --> S085
    S080 --> S086
    S081 --> S086
    S082 --> S086
    S083 --> S086
    S084 --> S086
    S087 --> S088
    S087 --> S089
    S088 --> S090
    S087 --> S090
    S088 --> S091
    S091 --> S092
    S087 --> S093
    S088 --> S093
    S089 --> S093
    S090 --> S093
    S091 --> S093
    S092 --> S093
    S087 --> S094
    S085 --> S094
    S094 --> S095
    S095 --> S096
    S096 --> S097
    S097 --> S098
    S094 --> S099
    S095 --> S099
    S096 --> S099
    S097 --> S099
    S098 --> S099
```

---

## Parallel Track Summary (Gantt-style ASCII)

```
WEEK →          W1      W2      W3      W4      W5      W6      W7      W8
Track A (BE)   [001-010][011-020]
Track B (FE)   [003    ]               [100-110................................]
Track C (AI)           [042-048][049-054]
Track D (Repo)                  [021-027][028-034]
Track E (GH)   [040    ][035-041]
Track F (Agts)                          [062-079][080-086]
Track G (Orch)                                          [087-093][094-099]
Track H (Sec)  [══════════════════ Security runs alongside all tracks ══════]
Track I (Mem)                  [055-061]
Track J (Obs)          [007    ]                                [118-124]
Track K (Doc)                                                           [125-130]
```

---

## P0 Task Cluster (Must Complete First)

These tasks form the **non-negotiable foundation**. No other work can begin safely without them:

```
SPECTER-001  Initialize Rust Axum API service skeleton
SPECTER-002  Initialize Python agent runtime package
SPECTER-003  Initialize Next.js + TypeScript frontend project
SPECTER-004  Configure Docker Compose for development environment
SPECTER-005  Set up PostgreSQL with pgvector extension
SPECTER-006  Configure Temporal server and worker connection
SPECTER-009  Configure environment variable management and secrets handling
SPECTER-011  Implement PostgreSQL connection pool in Rust
SPECTER-012  Implement database schema migrations
SPECTER-017  Implement API authentication middleware
SPECTER-025  Implement file system isolation
SPECTER-040  Implement GitHub token secure storage
SPECTER-076  Implement security issue scanner
SPECTER-082  Implement network isolation for test containers
SPECTER-111  Implement URL sanitization for repository inputs
SPECTER-112  Implement secret scanning before AI prompt injection
SPECTER-113  Implement Docker host mount restrictions
SPECTER-114  Implement container network isolation enforcement
SPECTER-116  Implement GitHub token vault integration
```

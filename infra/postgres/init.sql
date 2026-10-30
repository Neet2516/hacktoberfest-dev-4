-- Enable pgvector extension for Ghost Memory embeddings
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Repositories table
CREATE TABLE IF NOT EXISTS repositories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    url TEXT UNIQUE NOT NULL,
    owner TEXT NOT NULL,
    name TEXT NOT NULL,
    default_branch TEXT NOT NULL DEFAULT 'main',
    baseline_commit TEXT,
    primary_language TEXT,
    status TEXT NOT NULL DEFAULT 'ingested',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    epic TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'BACKLOG',
    assigned_agent TEXT,
    dependencies TEXT[] DEFAULT '{}',
    acceptance_criteria TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Inter-Agent Messages table
CREATE TABLE IF NOT EXISTS agent_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id TEXT UNIQUE NOT NULL,
    from_agent TEXT NOT NULL,
    to_agent TEXT NOT NULL,
    task_id TEXT NOT NULL,
    message_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    evidence_refs TEXT[] DEFAULT '{}',
    execution_status TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Ghost Memory table with vector embedding (768 dimensions for nomic-embed-text / Gemma)
CREATE TABLE IF NOT EXISTS ghost_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    category TEXT NOT NULL, -- 'architecture_decision', 'bug_fix', 'rejected_approach', etc.
    source_type TEXT NOT NULL, -- 'git_commit', 'issue', 'agent_hypothesis', 'test_run'
    source_reference TEXT NOT NULL,
    is_verified_fact BOOLEAN NOT NULL DEFAULT FALSE,
    content TEXT NOT NULL,
    embedding vector(768),
    confidence_score REAL DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for vector cosine similarity search
CREATE INDEX IF NOT EXISTS ghost_memory_embedding_idx 
ON ghost_memory 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Audit log table (append-only)
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    target_resource TEXT NOT NULL,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

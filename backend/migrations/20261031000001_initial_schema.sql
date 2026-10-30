-- Enable pgvector and uuid extensions
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

-- Ghost Memory table with vector embedding
CREATE TABLE IF NOT EXISTS ghost_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repository_id UUID REFERENCES repositories(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_reference TEXT NOT NULL,
    is_verified_fact BOOLEAN NOT NULL DEFAULT FALSE,
    content TEXT NOT NULL,
    embedding vector(768),
    confidence_score REAL DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGSERIAL PRIMARY KEY,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    target_resource TEXT NOT NULL,
    details JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- DOCURA — flattened PostgreSQL schema (Supabase-ready)
--
-- Paste this whole script into the Supabase SQL Editor and run it against a
-- fresh, empty database. It reproduces the FINAL schema at Alembic HEAD
-- e1f2a3b4c5d6, flattened from the migration chain:
--
--   40b969166f5a  sprint 2 users and sessions
--   cc40852cf63f  sprint 2 password reset tokens
--   b9e5ec480815  sprint 3 documents
--   f1a2b3c4d5e6  sprint 4 processing jobs
--   b2c3d4e5f6a7  sprint 4 extraction results
--   c3d4e5f6a7b8  sprint 4 attribute observations
--   d4e5f6a7b8c9  m1 form session and audit
--   e1f2a3b4c5d6  chatbot conversations and messages   <-- HEAD
--
-- Fidelity notes (nothing invented beyond the migrations):
--   * Primary/foreign key CONSTRAINT NAMES are left unnamed, exactly as the
--     migrations leave them, so PostgreSQL auto-names them the same way Alembic's
--     op.create_table would (e.g. documents_pkey, documents_user_id_fkey).
--   * `id` and other UUID columns have NO server DEFAULT. The migrations create
--     none — the application generates UUIDs (uuid.uuid4). Likewise `is_active`,
--     enum columns, `title`, `content`, and `message_type` have no server default
--     (their model-level defaults are applied in Python, not by the database).
--   * Enum types store their VALUES ("needs_review"), not member names, matching
--     the migrations' values_callable configuration.
--
-- Supabase notes:
--   * Objects are created in the `public` schema (Supabase's default). DOCURA
--     uses application-level authorization (every query is scoped by user_id in
--     its WHERE clause), so NO Row Level Security policies and NO Supabase Auth
--     tables are added here — the migrations define none, and the app does not
--     rely on them.
--   * All types used (uuid, timestamptz, bigint, native enums, jsonb, now()) are
--     stock PostgreSQL and run as-is in Supabase.
--
-- After running this, mark the DB as being at HEAD so Alembic will not re-run it:
--   INSERT INTO alembic_version (version_num) VALUES ('e1f2a3b4c5d6');
-- (The alembic_version table is created by Alembic on first run; the migrations
-- themselves do not create it, so it is intentionally omitted from this script.)
-- =============================================================================

BEGIN;

-- -----------------------------------------------------------------------------
-- Enum types (created before the tables that reference them)
-- -----------------------------------------------------------------------------
CREATE TYPE document_type AS ENUM ('unclassified');

CREATE TYPE document_status AS ENUM ('queued', 'processing', 'ready', 'needs_review', 'failed');

CREATE TYPE job_state AS ENUM ('pending', 'claimed', 'succeeded', 'failed');

CREATE TYPE form_session_state AS ENUM ('active', 'handed_back', 'stopped', 'expired');

CREATE TYPE form_action_type AS ENUM (
    'hand_back', 'stop', 'fill', 'select', 'attach',
    'ask', 'answer', 'approval_request', 'approval_decision', 'override'
);

CREATE TYPE form_action_outcome AS ENUM ('succeeded', 'failed', 'skipped');

CREATE TYPE conversation_message_role AS ENUM ('user', 'assistant', 'system');

CREATE TYPE conversation_message_type AS ENUM (
    'text', 'requirements', 'document_status', 'readiness',
    'question', 'approval', 'action', 'error'
);

-- -----------------------------------------------------------------------------
-- users  (40b969166f5a)
-- -----------------------------------------------------------------------------
CREATE TABLE users (
    id            uuid NOT NULL,
    email         varchar(254) NOT NULL,
    password_hash varchar(255) NOT NULL,
    is_active     boolean NOT NULL,
    created_at    timestamptz NOT NULL DEFAULT now(),
    updated_at    timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (id)
);
CREATE UNIQUE INDEX ix_users_email_unique ON users (email);

-- -----------------------------------------------------------------------------
-- sessions  (40b969166f5a)
-- -----------------------------------------------------------------------------
CREATE TABLE sessions (
    id                  uuid NOT NULL,
    user_id             uuid NOT NULL,
    token_hash          varchar(64) NOT NULL,
    created_at          timestamptz NOT NULL DEFAULT now(),
    expires_at          timestamptz NOT NULL,
    absolute_expires_at timestamptz NOT NULL,
    last_used_at        timestamptz NOT NULL DEFAULT now(),
    revoked_at          timestamptz,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX ix_sessions_token_hash_unique ON sessions (token_hash);
CREATE INDEX ix_sessions_user_id ON sessions (user_id);

-- -----------------------------------------------------------------------------
-- password_reset_tokens  (cc40852cf63f)
-- -----------------------------------------------------------------------------
CREATE TABLE password_reset_tokens (
    id         uuid NOT NULL,
    user_id    uuid NOT NULL,
    token_hash varchar(64) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    expires_at timestamptz NOT NULL,
    used_at    timestamptz,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX ix_password_reset_tokens_token_hash_unique ON password_reset_tokens (token_hash);
CREATE INDEX ix_password_reset_tokens_user_id ON password_reset_tokens (user_id);

-- -----------------------------------------------------------------------------
-- documents  (b9e5ec480815, + failure_reason from f1a2b3c4d5e6)
-- -----------------------------------------------------------------------------
CREATE TABLE documents (
    id                uuid NOT NULL,
    user_id           uuid NOT NULL,
    original_filename varchar(255) NOT NULL,
    storage_key       varchar(64) NOT NULL,
    content_type      varchar(128) NOT NULL,
    byte_size         bigint NOT NULL,
    checksum_sha256   varchar(64) NOT NULL,
    document_type     document_type NOT NULL,
    status            document_status NOT NULL,
    failure_reason    varchar(500),
    created_at        timestamptz NOT NULL DEFAULT now(),
    updated_at        timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX ix_documents_storage_key_unique ON documents (storage_key);
CREATE UNIQUE INDEX ix_documents_user_id_checksum_unique ON documents (user_id, checksum_sha256);
CREATE INDEX ix_documents_user_id_created_at ON documents (user_id, created_at);

-- -----------------------------------------------------------------------------
-- processing_jobs  (f1a2b3c4d5e6)
-- -----------------------------------------------------------------------------
CREATE TABLE processing_jobs (
    id           uuid NOT NULL,
    document_id  uuid NOT NULL,
    state        job_state NOT NULL,
    attempts     integer NOT NULL,
    max_attempts integer NOT NULL,
    claimed_at   timestamptz,
    last_error   varchar(500),
    created_at   timestamptz NOT NULL DEFAULT now(),
    updated_at   timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX ix_processing_jobs_document_id_unique ON processing_jobs (document_id);
CREATE INDEX ix_processing_jobs_state_created_at ON processing_jobs (state, created_at);

-- -----------------------------------------------------------------------------
-- extraction_runs  (b2c3d4e5f6a7)
-- -----------------------------------------------------------------------------
CREATE TABLE extraction_runs (
    id             uuid NOT NULL,
    document_id    uuid NOT NULL,
    engine         varchar(100) NOT NULL,
    engine_version varchar(100) NOT NULL,
    created_at     timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY (document_id) REFERENCES documents (id) ON DELETE CASCADE
);
CREATE INDEX ix_extraction_runs_document_id_created_at ON extraction_runs (document_id, created_at);

-- -----------------------------------------------------------------------------
-- extraction_run_metadata  (b2c3d4e5f6a7)
-- -----------------------------------------------------------------------------
CREATE TABLE extraction_run_metadata (
    id     uuid NOT NULL,
    run_id uuid NOT NULL,
    key    varchar(200) NOT NULL,
    value  text NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (run_id) REFERENCES extraction_runs (id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX ix_extraction_run_metadata_run_id_key_unique ON extraction_run_metadata (run_id, key);

-- -----------------------------------------------------------------------------
-- extraction_pages  (b2c3d4e5f6a7)
-- -----------------------------------------------------------------------------
CREATE TABLE extraction_pages (
    id         uuid NOT NULL,
    run_id     uuid NOT NULL,
    number     integer NOT NULL,
    text       text NOT NULL,
    confidence double precision,
    PRIMARY KEY (id),
    FOREIGN KEY (run_id) REFERENCES extraction_runs (id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX ix_extraction_pages_run_id_number_unique ON extraction_pages (run_id, number);

-- -----------------------------------------------------------------------------
-- extraction_blocks  (b2c3d4e5f6a7)
-- -----------------------------------------------------------------------------
CREATE TABLE extraction_blocks (
    id            uuid NOT NULL,
    page_id       uuid NOT NULL,
    sequence      integer NOT NULL,
    text          text NOT NULL,
    confidence    double precision,
    region_x      double precision,
    region_y      double precision,
    region_width  double precision,
    region_height double precision,
    PRIMARY KEY (id),
    FOREIGN KEY (page_id) REFERENCES extraction_pages (id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX ix_extraction_blocks_page_id_sequence_unique ON extraction_blocks (page_id, sequence);

-- -----------------------------------------------------------------------------
-- attribute_observations  (c3d4e5f6a7b8)
-- -----------------------------------------------------------------------------
CREATE TABLE attribute_observations (
    id                   uuid NOT NULL,
    run_id               uuid NOT NULL,
    source_block_id      uuid NOT NULL,
    canonical_identifier varchar(200) NOT NULL,
    value                text NOT NULL,
    confidence           double precision,
    created_at           timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY (run_id) REFERENCES extraction_runs (id) ON DELETE CASCADE,
    FOREIGN KEY (source_block_id) REFERENCES extraction_blocks (id) ON DELETE CASCADE
);
CREATE INDEX ix_attribute_observations_run_id ON attribute_observations (run_id);

-- -----------------------------------------------------------------------------
-- form_sessions  (d4e5f6a7b8c9)
-- -----------------------------------------------------------------------------
CREATE TABLE form_sessions (
    id         uuid NOT NULL,
    user_id    uuid NOT NULL,
    state      form_session_state NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    ended_at   timestamptz,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX ix_form_sessions_user_id_created_at ON form_sessions (user_id, created_at);

-- -----------------------------------------------------------------------------
-- form_actions  (d4e5f6a7b8c9)
-- -----------------------------------------------------------------------------
CREATE TABLE form_actions (
    id                    uuid NOT NULL,
    session_id            uuid NOT NULL,
    action_type           form_action_type NOT NULL,
    outcome               form_action_outcome NOT NULL,
    field_ref             varchar(200),
    source_document_id    uuid,
    source_observation_id uuid,
    reverses_action_id    uuid,
    detail                varchar(500),
    created_at            timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY (session_id) REFERENCES form_sessions (id) ON DELETE CASCADE,
    FOREIGN KEY (source_document_id) REFERENCES documents (id) ON DELETE SET NULL,
    FOREIGN KEY (source_observation_id) REFERENCES attribute_observations (id) ON DELETE SET NULL,
    FOREIGN KEY (reverses_action_id) REFERENCES form_actions (id) ON DELETE CASCADE
);
CREATE INDEX ix_form_actions_session_id_created_at ON form_actions (session_id, created_at);

-- -----------------------------------------------------------------------------
-- conversations  (e1f2a3b4c5d6)
-- -----------------------------------------------------------------------------
CREATE TABLE conversations (
    id         uuid NOT NULL,
    user_id    uuid NOT NULL,
    title      varchar(200) NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
CREATE INDEX ix_conversations_user_id_updated_at ON conversations (user_id, updated_at);

-- -----------------------------------------------------------------------------
-- conversation_messages  (e1f2a3b4c5d6)
-- -----------------------------------------------------------------------------
CREATE TABLE conversation_messages (
    id              uuid NOT NULL,
    conversation_id uuid NOT NULL,
    role            conversation_message_role NOT NULL,
    message_type    conversation_message_type NOT NULL,
    content         text NOT NULL,
    data            jsonb,
    created_at      timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
);
CREATE INDEX ix_conversation_messages_conversation_id_created_at ON conversation_messages (conversation_id, created_at);

COMMIT;

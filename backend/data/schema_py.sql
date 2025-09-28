-- PostgreSQL

-- If you want DB-side UUID generation (optional but handy)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

BEGIN;

-- Minimal users table (only if you don't already have one)
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  username TEXT UNIQUE NOT NULL,
  hashed_password TEXT NOT NULL,
  role_type TEXT NOT NULL DEFAULT 'patient',  -- "patient" | "doctor"
  user_metadata JSON NOT NULL DEFAULT '{}'::json,  -- use JSONB if you want indexing later
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  token_version INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Seed (example)
-- INSERT INTO users (id, email)
-- VALUES ('3f3c8b7e-6b1a-4dc1-9d7a-2e7a9a9d7b11', 'demo@example.com')
-- ON CONFLICT (id) DO NOTHING;

-- Shared trigger function to manage updated_at
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- === medical_records (from MedicalRecord) ===
CREATE TABLE IF NOT EXISTS medical_records (
  record_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),       -- app can still provide its own UUID
  user_id   UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  data      JSON NOT NULL DEFAULT '{}'::json,                 -- use JSONB if you want indexing later
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_medical_records_user_id ON medical_records(user_id);

-- Auto-bump updated_at on update
DROP TRIGGER IF EXISTS trg_medical_records_updated_at ON medical_records;
CREATE TRIGGER trg_medical_records_updated_at
BEFORE UPDATE ON medical_records
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- Do the same for users (optional)
DROP TRIGGER IF EXISTS trg_users_updated_at ON users;
CREATE TRIGGER trg_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

-- === chat_history (from ChatHistory) ===
-- Matches: id PK, record_id FK -> medical_records.record_id, user_id (indexed), role, content, created_at
CREATE TABLE IF NOT EXISTS chat_history (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  record_id  UUID NOT NULL REFERENCES medical_records(record_id) ON DELETE CASCADE,
  user_id    UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  role       TEXT NOT NULL,                  -- "user" | "AI" | "system" (enforce in app or add CHECK)
  content    TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_history_record_id ON chat_history(record_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id   ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_created   ON chat_history(created_at);

-- === ai_state (from AIState) ===
-- Composite PK (record_id, user_id), JSON data with default, FK on record_id only (as in model)
CREATE TABLE IF NOT EXISTS ai_state (
  record_id  UUID NOT NULL REFERENCES medical_records(record_id) ON DELETE CASCADE,
  user_id    UUID NOT NULL,
  data       JSON NOT NULL DEFAULT '{}'::json,
  PRIMARY KEY (record_id, user_id)
);

-- Helpful index if you often look up by user_id
CREATE INDEX IF NOT EXISTS idx_ai_state_user_id ON ai_state(user_id);

COMMIT;

-- === todos (from Todo) ===
-- Standalone TODO items, independent from AIState or MedicalRecord repos
BEGIN;
CREATE TABLE IF NOT EXISTS todos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  record_id UUID NOT NULL REFERENCES medical_records(record_id) ON DELETE CASCADE,
  text TEXT NOT NULL,
  is_check BOOLEAN NOT NULL DEFAULT FALSE,
  position INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_todos_user_id ON todos(user_id);
CREATE INDEX IF NOT EXISTS idx_todos_record_id ON todos(record_id);
COMMIT;

-- === diagnoses (from Diagnosis) ===
BEGIN;
CREATE TABLE IF NOT EXISTS diagnoses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  record_id UUID NOT NULL REFERENCES medical_records(record_id) ON DELETE CASCADE,
  reasoning_process TEXT NOT NULL,
  diagnosis JSON NOT NULL DEFAULT '{}'::json,
  further_test JSON NOT NULL DEFAULT '{}'::json,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_diagnoses_user_id ON diagnoses(user_id);
CREATE INDEX IF NOT EXISTS idx_diagnoses_record_id ON diagnoses(record_id);
CREATE INDEX IF NOT EXISTS idx_diagnoses_created ON diagnoses(created_at);
COMMIT;
-- === contacts (from Contact) ===
BEGIN;
CREATE TABLE IF NOT EXISTS contacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  patient_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  assigned_doctor_id UUID NULL REFERENCES users(id) ON DELETE SET NULL,
  record_id UUID NOT NULL REFERENCES medical_records(record_id) ON DELETE CASCADE,
  address TEXT NOT NULL,
  facility TEXT NOT NULL,
  include_conversation BOOLEAN NOT NULL DEFAULT FALSE,
  payload JSON NOT NULL DEFAULT '{}'::json,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_contacts_patient ON contacts(patient_id);
CREATE INDEX IF NOT EXISTS idx_contacts_doctor ON contacts(assigned_doctor_id);
CREATE INDEX IF NOT EXISTS idx_contacts_record ON contacts(record_id);
COMMIT;

-- === contact_messages (from ContactMessage) ===
BEGIN;
CREATE TABLE IF NOT EXISTS contact_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
  sender_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_contact_messages_contact ON contact_messages(contact_id);
CREATE INDEX IF NOT EXISTS idx_contact_messages_created ON contact_messages(created_at);
COMMIT;

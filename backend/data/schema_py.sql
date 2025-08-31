-- PostgreSQL

-- If you want DB-side UUID generation (optional but handy)
CREATE EXTENSION IF NOT EXISTS pgcrypto;

BEGIN;

-- Minimal users table (only if you don't already have one)
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY,                -- app can supply; no default needed
  email TEXT UNIQUE,                  -- optional
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO users (id, email) VALUES ('3f3c8b7e-6b1a-4dc1-9d7a-2e7a9a9d7b11', 'demo@example.com') RETURNING id, email;

-- Shared trigger function to manage updated_at
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE IF NOT EXISTS medical_records (
  record_id UUID PRIMARY KEY DEFAULT gen_random_uuid(), -- app can still provide its own UUID
  user_id   UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  data      JSON NOT NULL DEFAULT '{}'::json,           -- use JSONB if you want indexing later
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

COMMIT;

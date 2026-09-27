-- 🗄️ Plataforma Total WEB — esquema D1 (SQLite)
-- Aplicar: npx wrangler d1 execute plataforma --file=schema.sql

CREATE TABLE IF NOT EXISTS users (
  alias  TEXT PRIMARY KEY,
  hash   TEXT NOT NULL,          -- PBKDF2-SHA256 (100k iter) hex
  salt   TEXT NOT NULL,
  creado TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
  token  TEXT PRIMARY KEY,
  alias  TEXT NOT NULL REFERENCES users(alias),
  expira TEXT NOT NULL           -- ISO date; 30 días
);

CREATE TABLE IF NOT EXISTS progreso (
  alias       TEXT PRIMARY KEY REFERENCES users(alias),
  data        TEXT NOT NULL,     -- JSON: {xp, racha, ultima_leccion, completados[], quiz_ok}
  actualizado TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS certificados (
  codigo TEXT PRIMARY KEY,       -- PT-XXXXXX verificable
  alias  TEXT NOT NULL,
  curso  TEXT NOT NULL,
  fecha  TEXT NOT NULL
);

-- 💎 Monetización PRO (Lemon Squeezy webhooks)
CREATE TABLE IF NOT EXISTS pro (
  email TEXT PRIMARY KEY,
  estado INTEGER DEFAULT 1,           -- 1=activo, 0=refund/cancelado
  order_id TEXT,
  evento TEXT,
  actualizado TEXT
);
CREATE TABLE IF NOT EXISTS pro_alias ( -- vincula la sesión de la app (alias) con el email de compra
  alias TEXT PRIMARY KEY,
  email TEXT,
  actualizado TEXT
);

-- 🛡️ anti fuerza bruta login (5 fallos / 10 min)
CREATE TABLE IF NOT EXISTS intentos (
  alias TEXT PRIMARY KEY,
  n INTEGER DEFAULT 0,
  ts TEXT
);

CREATE INDEX IF NOT EXISTS idx_sessions_alias ON sessions(alias);
CREATE INDEX IF NOT EXISTS idx_sessions_expira ON sessions(expira);
CREATE INDEX IF NOT EXISTS idx_certificados_alias ON certificados(alias);
CREATE INDEX IF NOT EXISTS idx_pro_alias_email ON pro_alias(email);
CREATE TABLE IF NOT EXISTS projects (id TEXT PRIMARY KEY,alias TEXT NOT NULL,name TEXT NOT NULL,metadata TEXT,created TEXT NOT NULL,updated TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_projects_alias_updated ON projects(alias,updated DESC);

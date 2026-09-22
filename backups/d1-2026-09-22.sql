PRAGMA defer_foreign_keys=TRUE;
CREATE TABLE users (
  alias  TEXT PRIMARY KEY,
  hash   TEXT NOT NULL,          -- PBKDF2-SHA256 (100k iter) hex
  salt   TEXT NOT NULL,
  creado TEXT NOT NULL
);
INSERT INTO "users" ("alias","hash","salt","creado") VALUES('testuser1','9f91499012313f2ea0a71f8e133e9f91e48e5c26df3f5ec5820397f41aa92a21','5e75310afc995eb24afdcece8c42ea1e','2026-09-20T23:23:50.239Z');
INSERT INTO "users" ("alias","hash","salt","creado") VALUES('testuser2','a351c5549a7686071ab4a697ce58c238967c40d95f59dcfa1bbe294fc3ce3855','d077b74138a6731b0521cd218a4faab3','2026-09-21T01:20:26.396Z');
INSERT INTO "users" ("alias","hash","salt","creado") VALUES('lock1','c9b1f77071b426ffec13df334d291d298ac7a6bf166f783452c3d833272a6ab9','b1679b5ebee120d9a6ad9af8e524cce8','2026-09-21T05:03:24.856Z');
CREATE TABLE sessions (
  token  TEXT PRIMARY KEY,
  alias  TEXT NOT NULL REFERENCES users(alias),
  expira TEXT NOT NULL           -- ISO date; 30 días
);
INSERT INTO "sessions" ("token","alias","expira") VALUES('9c86699239c99b1353212a4d8c4cf38cb40e53c7ab86dc5e','testuser1','2026-10-20T23:23:50.308Z');
INSERT INTO "sessions" ("token","alias","expira") VALUES('41c5b1206da1c9c7265f9dd5b1122493b853288d4414e141','testuser1','2026-10-21T01:20:26.074Z');
INSERT INTO "sessions" ("token","alias","expira") VALUES('6d47a17c5e0d7047ff1589d43c9bb8e6059a4df52c86c74c','testuser2','2026-10-21T01:20:26.464Z');
INSERT INTO "sessions" ("token","alias","expira") VALUES('45955d8a7db42c8d553f91d9771b5563ac189a62f47dd562','testuser1','2026-10-21T01:20:58.229Z');
INSERT INTO "sessions" ("token","alias","expira") VALUES('f4565368110140eaa2627c0339697f03f34d4a6420c7c6d9','lock1','2026-10-21T05:03:24.917Z');
INSERT INTO "sessions" ("token","alias","expira") VALUES('0c134abb249e6d6435fa0abec2bb5ab6db855531a70c1fc6','testuser1','2026-10-21T05:03:26.393Z');
INSERT INTO "sessions" ("token","alias","expira") VALUES('c4443a5c2d137d33a060cc2e0c2b026eb0cb23c98b6aa525','testuser1','2026-10-21T05:11:07.626Z');
INSERT INTO "sessions" ("token","alias","expira") VALUES('d4e8f611ef0a0e44cbb35062c7e20fe8b22130f55b9baf9c','testuser1','2026-10-21T05:11:33.551Z');
INSERT INTO "sessions" ("token","alias","expira") VALUES('d7258601ad2ea149ded0f2635e7c0714e0ba1380e17b2f44','testuser1','2026-10-21T05:12:22.419Z');
CREATE TABLE progreso (
  alias       TEXT PRIMARY KEY REFERENCES users(alias),
  data        TEXT NOT NULL,     -- JSON: {xp, racha, ultima_leccion, completados[], quiz_ok}
  actualizado TEXT NOT NULL
);
INSERT INTO "progreso" ("alias","data","actualizado") VALUES('testuser1','{"xp":42,"tema":"prueba"}','2026-09-21T05:11:33.742Z');
CREATE TABLE certificados (
  codigo TEXT PRIMARY KEY,       -- PT-XXXXXX verificable
  alias  TEXT NOT NULL,
  curso  TEXT NOT NULL,
  fecha  TEXT NOT NULL
);
CREATE TABLE pro (
  email TEXT PRIMARY KEY,
  estado INTEGER DEFAULT 1,           -- 1=activo, 0=refund/cancelado
  order_id TEXT,
  evento TEXT,
  actualizado TEXT
);
CREATE TABLE pro_alias ( -- vincula la sesión de la app (alias) con el email de compra
  alias TEXT PRIMARY KEY,
  email TEXT,
  actualizado TEXT
);
INSERT INTO "pro_alias" ("alias","email","actualizado") VALUES('comprador1','comprador.mp@test.uy','2026-09-21T20:33:15.708Z');
CREATE TABLE intentos (alias TEXT PRIMARY KEY, n INTEGER DEFAULT 0, ts TEXT);
INSERT INTO "intentos" ("alias","n","ts") VALUES('lock1',5,'2026-09-21T05:03:25.946Z');

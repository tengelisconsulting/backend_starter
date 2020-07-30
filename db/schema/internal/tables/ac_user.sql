CREATE TABLE IF NOT EXISTS ac_user (
  user_id  UUID   NOT NULL  DEFAULT uuid_generate_v1mc(),
  created  TIMESTAMPTZ  NOT NULL  DEFAULT now(),
  updated  TIMESTAMPTZ  NOT NULL  DEFAULT now(),
  workdays  INTEGER[]  NOT NULL  DEFAULT ARRAY[1, 2, 3, 4, 5]
    CHECK ((0 <= ALL(workdays)) AND (7 > ALL(workdays))),
  email_lower  TEXT  NOT NULL,
  timezone  TEXT  NOT NULL
    CHECK (now() AT TIME ZONE timezone IS NOT NULL),
  pw_hash  TEXT,
  provider  JSON,
  adhoc  JSON  DEFAULT NULL,

  PRIMARY KEY (user_id),
  UNIQUE (email_lower)
);

COMMENT ON TABLE ac_user IS 'An app user';
COMMENT ON COLUMN ac_user.provider IS 'keys: ["type", "token"]';
COMMENT ON COLUMN ac_user.workdays IS '0 is Sunday';

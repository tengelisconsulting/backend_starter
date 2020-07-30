CREATE TABLE IF NOT EXISTS user_default (
  setting_id  UUID   NOT NULL  DEFAULT uuid_generate_v1mc(),
  created  TIMESTAMPTZ  NOT NULL  DEFAULT now(),
  updated  TIMESTAMPTZ  NOT NULL  DEFAULT now(),
  setting_name  TEXT  NOT NULL,
  setting_type  REGTYPE  NOT NULL,
  setting_value  TEXT  NOT NULL,

  PRIMARY KEY (setting_id),
  UNIQUE (setting_name)
);

COMMENT ON TABLE user_default IS 'Defaults to apply to a user account';

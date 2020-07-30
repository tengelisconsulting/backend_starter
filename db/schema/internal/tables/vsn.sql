CREATE TABLE IF NOT EXISTS vsn (
  installed  TIMESTAMPTZ  NOT NULL  DEFAULT now(),
  adhoc  JSON  DEFAULT NULL,
  git_rev  TEXT,

  PRIMARY KEY (installed)
);

COMMENT ON TABLE vsn IS 'Database version install history';

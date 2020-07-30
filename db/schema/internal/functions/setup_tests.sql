CREATE OR REPLACE FUNCTION setup_tests()
RETURNS BOOLEAN
AS $$
BEGIN
  DELETE FROM ac_user where  (adhoc->>'test')::BOOLEAN;

  DROP TABLE IF EXISTS api.perf_testing;
  CREATE TABLE api.perf_testing (
    data_id   UUID  NOT NULL
      DEFAULT uuid_generate_v1mc(),
    created  TIMESTAMPTZ  NOT NULL
      DEFAULT now(),
    datas  JSON
  );

  RETURN TRUE;
END;
$$
LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION new_uuid()
RETURNS UUID
AS $$
BEGIN
  RETURN uuid_generate_v1mc();
END;
$$
LANGUAGE plpgsql
;

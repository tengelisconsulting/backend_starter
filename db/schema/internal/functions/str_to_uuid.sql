CREATE OR REPLACE FUNCTION str_to_uuid(
  IN   p_str      TEXT
)
RETURNS UUID
AS $$
BEGIN
  RETURN p_str::uuid;
EXCEPTION WHEN invalid_text_representation THEN
  RETURN NULL;
END;
$$
LANGUAGE plpgsql
;

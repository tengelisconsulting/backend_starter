CREATE OR REPLACE FUNCTION json_merge(
  IN p_target  JSON,
  IN p_merge_in  JSON
)
RETURNS JSON
AS $$
DECLARE
  v_target  JSONB  := p_target::JSONB;
  v_merge_in  JSONB  := p_merge_in::JSONB;
BEGIN
  IF v_target IS NULL THEN
    v_target := '{}'::JSONB;
  END IF;
  IF v_merge_in IS NULL THEN
    v_merge_in := '{}'::JSONB;
  END IF;

  RETURN v_target || v_merge_in;
END;
$$
LANGUAGE plpgsql
;

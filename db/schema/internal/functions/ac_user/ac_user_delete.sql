CREATE OR REPLACE FUNCTION ac_user_delete(
  IN p_user_id  UUID
)
RETURNS INTEGER
AS $$
BEGIN
  IF (SELECT 1 FROM ac_user WHERE user_id = p_user_id) IS NULL THEN
    RETURN 0;
  END IF;

  DELETE FROM ac_user
        WHERE user_id = p_user_id
  ;
  RETURN 1;
END;
$$
LANGUAGE plpgsql
;

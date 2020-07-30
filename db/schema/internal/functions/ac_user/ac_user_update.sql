CREATE OR REPLACE FUNCTION ac_user_update(
  IN p_user_id  UUID,
  IN p_workdays  INTEGER[]  DEFAULT NULL,
  IN p_adhoc  JSON  DEFAULT NULL
)
RETURNS INTEGER
AS $$
DECLARE
  v_updated  INTEGER  := 0;
BEGIN
  IF (SELECT 1
        FROM ac_user
       WHERE user_id = p_user_id) IS NULL THEN
    RETURN 0;
  END IF;

  IF p_workdays IS NOT NULL THEN
    UPDATE ac_user
       SET workdays = p_workdays
     WHERE user_id = p_user_id
    ;
    v_updated := 1;
  END IF;

  IF p_adhoc IS NOT NULL THEN
    UPDATE ac_user
       SET adhoc = p_adhoc
     WHERE user_id = p_user_id
    ;
    v_updated := 1;
  END IF;

  RETURN v_updated;
END;
$$
LANGUAGE plpgsql
;

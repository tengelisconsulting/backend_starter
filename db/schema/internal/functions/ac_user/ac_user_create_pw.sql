CREATE OR REPLACE FUNCTION ac_user_create_pw(
  IN p_email  TEXT,
  IN p_pw_hash  TEXT,
  IN p_timezone  TEXT,
  IN p_adhoc  JSON  DEFAULT NULL
)
RETURNS UUID
AS $$
DECLARE
  v_user_id  UUID  := new_uuid();
BEGIN
  IF NOT verify_email(p_email) THEN
    RAISE EXCEPTION 'not a valid email address -> %', p_email;
  END IF;
  INSERT INTO ac_user (
                user_id,
                email_lower,
                pw_hash,
                timezone,
                adhoc
              )
       VALUES (
                v_user_id,
                lower(p_email),
                p_pw_hash,
                p_timezone,
                p_adhoc
              )
  ;
  RETURN v_user_id;
END;
$$
LANGUAGE plpgsql
;

CREATE OR REPLACE FUNCTION ac_user_create_provider(
  IN p_email  TEXT,
  IN p_provider_type  PROVIDER_T,
  IN p_provider_token  TEXT,
  IN p_timezone  TEXT,
  IN p_adhoc  JSON  DEFAULT NULL
)
RETURNS UUID
AS $$
DECLARE
  v_user_id  UUID  := new_uuid();
  v_provider_data  JSON  := json_build_object(
                              'type', p_provider_type::TEXT,
                              'token', p_provider_token
                            );
BEGIN
  IF NOT verify_email(p_email) THEN
    RAISE EXCEPTION 'not a valid email address -> %', p_email;
  END IF;
  INSERT INTO ac_user (
                user_id,
                email_lower,
                provider,
                timezone,
                adhoc
              )
       VALUES (
                v_user_id,
                lower(p_email),
                v_provider_data,
                p_timezone,
                p_adhoc
              )
  ;
  RETURN v_user_id;
END;
$$
LANGUAGE plpgsql
;

CREATE OR REPLACE FUNCTION user_default_set(
  IN p_setting_name  TEXT,
  IN p_setting_type  TEXT,
  IN p_setting_value  TEXT
)
RETURNS JSON
AS $$
DECLARE
  v_setting_id  UUID;
  v_setting_type  REGTYPE  := p_setting_type::REGTYPE;
  v_value_is_of_type  BOOLEAN;
BEGIN
  EXECUTE '
    SELECT TRUE
     WHERE $1::' || p_setting_type || ' IS NOT NULL
  '
   INTO v_value_is_of_type
  USING p_setting_value
  ;

  IF lower(pg_typeof(p_setting_value)::TEXT) != lower(p_setting_type) THEN
  END IF;

  SELECT setting_id
    INTO v_setting_id
    FROM user_default
   WHERE setting_name = p_setting_name
  ;

  IF v_setting_id IS NULL THEN
    INSERT INTO user_default (
                  setting_name,
                  setting_type,
                  setting_value
                )
         VALUES (
                  p_setting_name,
                  v_setting_type,
                  p_setting_value
                )
    ;
    RETURN json_build_object(
      'created', 1
    );
  ELSE
    UPDATE user_default
       SET setting_value = p_setting_value,
           setting_type = v_setting_type
     WHERE setting_id = v_setting_id
    ;
    RETURN json_build_object(
      'updated', 1
    );
  END IF;
END;
$$
LANGUAGE plpgsql
;

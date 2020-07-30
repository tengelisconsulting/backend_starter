CREATE OR REPLACE FUNCTION session_user_id()
RETURNS UUID
AS $$
BEGIN
  RETURN str_to_uuid(
           current_setting(
             'request.header.user-id',
             true
           )
         );
END;
$$
LANGUAGE plpgsql
;

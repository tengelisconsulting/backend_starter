DO $$
BEGIN
  UPDATE ac_user
     SET adhoc = json_merge(adhoc, json_build_object(
                                     'verified', TRUE
                                   ))
   WHERE adhoc->'verified' IS NULL
  ;
END;
$$ LANGUAGE plpgsql;

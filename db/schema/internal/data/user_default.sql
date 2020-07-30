DO $$
BEGIN
  PERFORM user_default_set(
    p_setting_name => 'DAY_START_SCHED_H',
    p_setting_type => 'INTEGER',
    p_setting_value => '8'
  );
  PERFORM user_default_set(
    p_setting_name => 'DAY_START_SCHED_M',
    p_setting_type => 'INTEGER',
    p_setting_value => '30'
  );
END;
$$ LANGUAGE plpgsql;

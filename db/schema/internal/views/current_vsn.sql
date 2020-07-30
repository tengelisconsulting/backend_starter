CREATE OR REPLACE VIEW current_vsn
AS
  WITH latest AS (
    SELECT max(installed) installed
      FROM vsn
  )
    SELECT vsn.installed,
           vsn.git_rev,
           vsn.adhoc
      FROM vsn
      JOIN latest
        ON vsn.installed = latest.installed
;

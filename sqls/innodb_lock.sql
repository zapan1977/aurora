# InnoDB transaction block query.
# https://dev.mysql.com/doc/refman/5.7/en/innodb-information-schema-examples.html
SELECT
  r.trx_id waiting_trx_id,
  r.trx_mysql_thread_id waiting_thread,
  r.trx_query waiting_query,
  b.trx_id blocking_trx_id,
  b.trx_mysql_thread_id blocking_thread,
  b.trx_query blocking_query
FROM       information_schema.INNODB_LOCK_WAITS w
INNER JOIN information_schema.INNODB_TRX b
  ON b.trx_id = w.blocking_trx_id
INNER JOIN information_schema.INNODB_TRX r
  ON r.trx_id = w.requesting_trx_id
;

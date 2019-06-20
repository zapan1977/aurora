CREATE TEMPORARY TABLE `information_schema`.`PROCESSLIST` (
  `ID` bigint(21) unsigned NOT NULL DEFAULT '0',
  `USER` varchar(32) NOT NULL DEFAULT '',
  `HOST` varchar(64) NOT NULL DEFAULT '',
  `DB` varchar(64) DEFAULT NULL,
  `COMMAND` varchar(16) NOT NULL DEFAULT '',
  `TIME` int(7) NOT NULL DEFAULT '0',
  `STATE` varchar(64) DEFAULT NULL,
  `INFO` longtext
) ENGINE=InnoDB DEFAULT CHARSET=utf8
;

-- Kill processlist `TIME` is seconds.
SELECT CONCAT("CALL mysql.rds_kill(",ID,");")
FROM `information_schema`.`PROCESSLIST`
WHERE `TIME` > 600 
;

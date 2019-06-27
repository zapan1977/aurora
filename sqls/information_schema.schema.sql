CREATE TEMPORARY TABLE `information_schema`.`SCHEMATA` (
  `CATALOG_NAME` varchar(512) NOT NULL DEFAULT '',
  `SCHEMA_NAME` varchar(64) NOT NULL DEFAULT '',
  `DEFAULT_CHARACTER_SET_NAME` varchar(32) NOT NULL DEFAULT '',
  `DEFAULT_COLLATION_NAME` varchar(32) NOT NULL DEFAULT '',
  `SQL_PATH` varchar(512) DEFAULT NULL
) ENGINE=MEMORY DEFAULT CHARSET=utf8
;

SELECT SCHEMA_NAME AS `Database`
FROM `information_schema`.SCHEMATA
WHERE `SCHEMA_NAME` NOT IN (
    'information_schema',
    'mysql',
    'performance_schema',
    'sys'
)
;

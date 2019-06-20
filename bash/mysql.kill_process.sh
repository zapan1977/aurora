#! /bin/bash

# MySQL Login Path
mysql --login-path=login -N --execute="SELECT CONCAT('CALL mysql.rds_kill(',ID,');') FROM information_schema.PROCESSLIST;"

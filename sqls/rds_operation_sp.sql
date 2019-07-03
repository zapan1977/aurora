-- Binary Log 보관 시간 확인.
Call mysql.rds_show_configuration;

-- Binary log 보관 시간 설정. Default: NULL(바이너리 미보관). DB 인스턴스 스토리지를 사용. 기간 증가시 모니터링 필요.
Call mysql.rds_set_configuration('binlog retention hours', 48);

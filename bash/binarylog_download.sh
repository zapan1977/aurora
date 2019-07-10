# Amazon RDS Binary Log 다운로드. mysqlbinlog Util을 사용해서 원격에서 Download.
# 
mysqlbinlog \
    --read-from-remote-server \
    --host=pfproductv2.cqhvl55yvzxw.ap-northeast-2.rds.amazonaws.com \
    --port=3306  \
    --user <User> \
    --password \
    --raw \
    --result-file=/tmp/ \
    binlog.00098

# 쿼리 확인을 위한 옵션
mysqlbinlog -vv --base64-output=DECODE-ROWS logfile

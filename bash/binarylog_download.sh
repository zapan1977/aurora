# Amazon RDS Binary Log 다운로드. mysqlbinlog Util을 사용해서 원격에서 Download.
# --login-path=name 지원 안함.
mysqlbinlog \
--read-from-remote-server \
--host=<MySQL Endpoint or Host> \
--port=3306  \
--user <User> \
--password \
--raw \
--result-file=<Local Path>/<binary log file name>

# Binary Log statement 파일로 변환.
mysqlbinlog \
-vv \
--base64-output=DECODE-ROWS \
<binary log file> >> file_name.sql or file_name.txt

#!/bin/sh

#실행시각
NOW_DATE=`date`

#백업날짜
BACKUP_DATE=`date +"%Y%m%d"`

#백업파일을 저장할 경로
BACKUP_DIR=/home/peoplefund/tableau-server-backup

# Tableua 서버 토폴로지 및 구성 데이터 백업
/opt/tableau/tableau_server/packages/customer-bin.20181.18.0404.1605/tsm \
settings export -f ${BACKUP_DIR}/pf_tableau_settings_${BACKUP_DATE}.json

# Tableua 리포지토리 데이터 백업
/opt/tableau/tableau_server/packages/customer-bin.20181.18.0404.1605/tsm \
maintenance backup -f pf_tableau_repo_${BACKUP_DATE}.tsbak
# Backup file 이동
mv /var/opt/tableau/tableau_server/data/tabsvc/files/backups/pf_tableau_repo_${BACKUP_DATE}.tsbak \
${BACKUP_DIR}/pf_tableau_repo_${BACKUP_DATE}.tsbak

# 변경된지 3일 이후 파일 삭제
find ${BACKUP_DIR}/ -mtime +3 -exec rm -f {} \;

# 완료시각
END_DATE=`date`
echo "시작: ${NOW_DATE} 완료: ${END_DATE}"

## Crontab
# 1 1 * * * /home/peoplefund/scripts/tableau-backup.sh >> /home/peoplefund/scripts/tableau-backup.txt 2>&1

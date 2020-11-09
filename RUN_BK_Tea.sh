# !/bin/bash
curDate=$(date +%Y%m%d)
# 以文件的形式备份当天数据，避免数据库太大，导致性能不行。
mysqldump -uroot -p123456 -t student_service person_teacher_body_status > ./sqls/person_teacher_body_status_$curDate.sql
# 清空当天数据
echo "root password" | sudo -S python /data model path/MainBKTea.py --dbhost localhost

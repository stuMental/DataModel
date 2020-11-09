# !/bin/bash
curDate=$(date +%Y%m%d)
# 以文件的形式备份当天数据，避免数据库太大，导致性能不行。
echo "123456" | mysqldump -uroot -p -t student_service person_body_status > ./sqls/person_body_status_$curDate.sql
# 清空当天数据
echo "mysql password" | sudo -S python /data model path/MainBK.py --dbhost localhost
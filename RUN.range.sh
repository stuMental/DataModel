# !/bin/bash
for i in `seq 248 -1 173`
do
    start_date=`date --date="-$i day" +%F`
    echo "Computing the date: $start_date"
    echo "root password" | sudo -S python /data model path/Main.py --dbhost $hostIP --date localhost
    sleep 1s
done
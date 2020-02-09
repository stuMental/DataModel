# !/bin/bash
# Get IP address
# please update 'eth0' or 'inet 地址' according your computer info. You can run 'ifconfig' to check.
hostIP=`ifconfig eth0 | grep "inet 地址" | cut -f 2 -d ":" | cut -f 1 -d " "`
echo "Get the IP address: $hostIP"
for i in `seq 248 -1 173`
do
    start_date=`date --date="-$i day" +%F`
    echo "Computing the date: $start_date"
    echo "root password" | sudo -S python /data model path/Main.py --dbhost $hostIP --date $start_date
    sleep 1s
done
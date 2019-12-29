# !/bin/bash
#Get IP address
hostIP=`ifconfig eth0 | grep "inet 地址" | cut -f 2 -d ":" | cut -f 1 -d " "`
echo "Get the IP address: $hostIP"
for ((i=0; i<=120; i++))
do
    start_date=date -d '2019-04-01' --date="+$i day"
    echo "Computing the date: $start_date"
    echo "123456" | sudo -S python /home/bojie/wenshuang/YunDie/DataModel/Main.py --dbhost $hostIP --date $start_date
done
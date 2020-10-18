# !/bin/bash
# Get IP address
# please update 'eth0' or 'inet 地址' according your computer info. You can run 'ifconfig' to check.
hostIP=`ifconfig eth0 | grep "inet 地址" | cut -f 2 -d ":" | cut -f 1 -d " "`
echo "Get the IP address: $hostIP"
echo "root password" | sudo -S python /data model path/MainRTL.py --dbhost $hostIP
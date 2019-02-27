# DataModel
Build a system to train data model

# Install Steps
1. Update package source: `sudo apt-get update`
1. Install mysql server: `sudo apt-get install mysql-server`. // 如果安装的是5.7的版本就不会再安装过程中提醒设置root密码 此时需要利用/etc/mysql/debian.cnf文件中的用户和密码登录 然后执行 `update mysql.user set authentication_string=password('your password') where user='root'and Host = 'localhost';`命令reset root的密码
1. Install python: `sudo apt-get install python2.7`
1. Install pip module: `sudo apt-get install python-pip`
1. Install MySQLdb module: `sudo apt-get install libmysqlclient-dev`, `sudo apt-get install mysqlclient`, and `sudo pip install mysql-python`
1. Create some tables. Please execute the file CreateTable.py: `python CreateTable.py`
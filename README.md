# DataModel
Build a system to train data model

# Necessary steps
1. 开启MySQL的binlog服务，方便数据的备份以及恢复等操作。
2. docker需要设置日志的大小限制等，避免占满磁盘的空间。

# Install Steps (已验证)
1. Update package source: `sudo apt-get update`
1. Install mysql server: `sudo apt-get install mysql-server`. // 如果安装的是5.7的版本就不会再安装过程中提醒设置root密码 此时需要利用/etc/mysql/debian.cnf文件中的用户和密码登录 然后执行 `update mysql.user set authentication_string=password('your password') where user='root'and Host = 'localhost';`命令reset root的密码
1. Install python: `sudo apt-get install python2.7`
1. Install pip module: `sudo apt-get install python-pip`
1. Install MySQLdb module: `sudo apt-get install libmysqlclient-dev`, and `sudo pip install mysql-python`
1. Create some tables. Please execute the file CreateTable.py: `python CreateTable.py`

# Update config before running the model
1. Modify Config.py to update Database's info.
2. If you want to run the specific date data, you can modify the function `get_range_times` and `get_date_day` in this file `CommonUtil.py`.
3. If you want to output debug info, you can update the **LOGGER_LEVEL** of Config.py to DEBUG.

# FQA
1. Issue 1: 'this is MySQLdb version (1, 2, 5, 'final', 1), but _mysql is version (1, 4, 1, 'final', 0)'.

   You can uninstall MySQLdb `sudo pip uninstall mysql-python`, and go to `/usr/local/lib/python2.7/dist-packages/`, then `sudo rm -rf MySQLdb`. Finally, you can re-install mysql-python. It should wrok.

1. Issue2: 'Can't connect to MySQL server on 'x.x.x.x''.

   需要更新 my.cnf of MySQL. 路径在 `/etc/mysql/mysql.conf.d/mysqld.cnf`, 然后注释掉 `bind-address = 127.0.0.1` 即可

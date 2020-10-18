# !/usr/bin/python
# -*- coding: utf-8 -*-

import csv
import os


out = open('../camera_sqls.sql', 'w+')
sql = '''INSERT INTO school_camera_room_info (camera_id, camera_addr, room_id, room_addr, dt) VALUES ('{0}', 'rtsp://{1}:554/ch2', {2}, '{3}', '2020-04-18');'''
with open('../camera_addr_20200418.csv', mode='r') as f:
    id = 1
    for line in f:
        arrs = line.split(',')
        out.write(sql.format(id, arrs[1], id, arrs[0]) + '\n')
        id += 1

out.close()
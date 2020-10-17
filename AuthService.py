# !/usr/bin/python
# -*- coding: utf-8 -*-

import hashlib
import requests
import argparse
import json
import uuid
from subprocess import Popen, PIPE


sn_file_path = '/home/.bole_version'
sn_salt_len = 4
sn_salt_pos = 32
sn_code_short_len = 72
sn_code_long_len = 73
first_number = 24
second_number = 68

class Information(object):
    """Get device fingerprint information"""
    def __init__(self):
        super(Information, self).__init__()

    @staticmethod
    def get_m_info():

        return uuid.UUID(int = uuid.getnode()).hex[-12:].lower()

    @staticmethod
    def get_d_info():
        command = 'dmidecode'
        info1_name = 'Processor Information'
        info2_name = 'BIOS Information'
        p = Popen([command], stdout=PIPE)
        data = [i for i in p.stdout.read().decode().split('\n') if i]
        parsed_data = []
        new_line = ''
        for line in data:
            if line[0].strip():
                parsed_data.append(new_line)
                new_line = line + '\n'
            else:
                new_line += line + '\n'
        parsed_data.append(new_line)
        parsed_data = [i for i in parsed_data if i]
        p_info = [i for i in parsed_data if i.startswith(info1_name)]
        p_results = Information.get_k_v(p_info)
        c_id = Information.unified_value(p_results['ID'])
        c_ver = Information.unified_value(p_results['Version'])
        b_info = [i for i in parsed_data if i.startswith(info2_name)]
        b_ver = Information.unified_value(Information.get_k_v(b_info)['Version'])

        return c_id, c_ver, b_ver

    @staticmethod
    def get_k_v(data):
        parsed_data = [i for i in data[0].split('\n')[1:] if i]
        return dict([i.strip().split(':') for i in parsed_data if ':' in i])

    @staticmethod
    def get_information():
        addr = Information.get_m_info()
        c_id, c_ver, b_ver = Information.get_d_info()
        return [addr, c_id, c_ver, b_ver]

    @staticmethod
    def unified_value(value):
        if value:
            return value.replace(' ', '').replace('-', '')

        return ''

class GetAuthCode(object):
    def __init__(self):
        super().__init__()
        self.__url = 'http://182.92.113.7:8080/AuthServer/AuthServer'
        self.__name = ''
        self.__num = 0
        self.__num_limit = 40

    def parse_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--name', type=str, help='输入账户名')
        parser.add_argument('--num', type=str, help="输入服务器处理的教室数")

        args = parser.parse_args()
        if not args.name or not args.num:
            print ("请输入账户名和服务器处理的教室数, 例如：sudo python3 GetAuthCode.py --name bole --num 10")
            exit(-1)

        if int(args.num) > self.__num_limit:
            print("输入的教室数超过限制(<=40)。")
            exit(-1)
        self.__name = args.name
        self.__num = args.num
        print("输入的账户名: {0}, 教室数: {1}".format(self.__name, self.__num))

    def get_fingers(self):

        try:
            return '_'.join(Information.get_information())
        except Exception as e:
            print('获取硬件信息失败，请使用sudo权限执行。')
            exit(-1)

    def post_auth(self, fingers):

        try:
            headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
            params = {"fingers": fingers, "name": self.__name, "num": self.__num}
            response = requests.post(url=self.__url, data=params, headers=headers)
            if response:
                return json.loads(response.text)
            else:
                return None
        except Exception as e:
            print('获取授权码失败，请确认网络是否连通。')
            exit(-1)

    def doer(self):
        try:
            self.parse_arguments()  # 获取授权需要的用户名
            fingers = hashlib.sha256(self.get_fingers().encode('utf-8')).hexdigest()  # '5a838d9d1c37c3601e2e133aaa72ef8c34623499eee0bb8b197fd1510dee3e93'
            data = self.post_auth(fingers=fingers)
            if data['code'] == '-1' or data is None:
                print('授权失败，错误原因[{0}], 请重试或联系工程师解决。'.format(data['message']))
            else:
                with open(sn_file_path, 'w') as out:
                    out.writelines(data['value'])
                    print('Auth successful~')
        except Exception as identifier:
            print('写授权文件失败，请使用sudo权限执行。')
            exit(-1)


class DoAuth(object):
    def __init__(self):
        super().__init__()

    @staticmethod
    def get_check_s(input_s):
        s = 0
        is_even = False
        for item in input_s:
            current = int(item, 16)
            if is_even:
                tmp = 2 * current
                while tmp >= 10:
                    tmp = tmp // 10 + tmp % 10
                s += tmp
            else:
                s += current

            is_even = not is_even

        return (10 - s % 10) % 10

    @staticmethod
    def check():
        first_pos = -3
        second_pos = -2
        third_pos = -1
        with open(sn_file_path, 'r') as fin:
            data = fin.readline().replace('\n', '')  # 读取第一行
            if len(data) != sn_code_short_len and len(data) != sn_code_long_len:
                print ('[-1000] 授权码无效，请先授权')
                return False, ''

            num_length = 1 if len(data) == sn_code_short_len else 2
            first = str(DoAuth.get_check_s(data[0:first_number]))
            second = str(DoAuth.get_check_s(data[first_number:(second_number + num_length)]))
            third = str(DoAuth.get_check_s(data[:third_pos]))
            if first == data[first_pos] and second == data[second_pos] and third == data[third_pos]:
                return True, data[0:(first_number - num_length)] + data[(first_number + num_length - 1):sn_salt_pos] + data[(sn_salt_pos + sn_salt_len):first_pos]

        return False, ''

    @staticmethod
    def auth():
        try:
            verify, code = DoAuth.check()
            if not verify:
                print ('[-1002] 授权码无效，请先授权')
                return False

            input_str = '_'.join(Information.get_information())
            if code != hashlib.sha256(hashlib.sha256(input_str.encode('utf-8')).hexdigest().encode('utf-8')).hexdigest():
                print ('[-1003] 授权码无效，请先授权')
                return False

        except Exception as e:
            print ('[-1001] 授权码无效，请先授权')
            return False

        print ('授权成功')
        return True

    @staticmethod
    def get_class_number():
        with open(sn_file_path, 'r') as fin:
            data = fin.readline().replace('\n', '')  # 读取第一行
            if len(data) != sn_code_short_len and len(data) != sn_code_long_len:
                print ('[-1000] 授权码无效，请先授权')
                return 0

            if len(data) == sn_code_short_len:
                return int(data[first_number - 1])
            elif len(data) == sn_code_long_len:
                return int(data[(first_number - 1) : (first_number + 1)])
            else:
                print ('[-1010] 授权码无效，请先授权')
                return 0

        print ('[-1010] 授权码无效，请先授权')
        return 0


if __name__ == "__main__":
    auth = GetAuthCode()
    print('======开始授权======')
    auth.doer()
    print('======结束授权======')
    
    print('======开始验证======')
    DoAuth.auth()
    print('======验证结束======')
    
    print('======获取班级数======')
    DoAuth.get_class_number()
    print('======获取结束======')
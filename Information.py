# !/usr/bin/python
# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE
import uuid

class Information(object):
    """Get some useful information"""
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


if __name__ == "__main__":
    print (Information.get_information())
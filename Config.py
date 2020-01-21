# !/usr/bin/python
# -*- coding: utf-8 -*-
# Define some constant variable.

import logging

# The config for Input Database 作为参数传递
# Database host
# INPUT_DB_HOST = 'ip_address'

# Database host for local test 仅local测试
INPUT_DB_HOST = '172.16.14.190'
# Database host for BiGuiYuan server
# INPUT_DB_HOST = 'localhost'

# Database username
INPUT_DB_USERNAME = 'root'

# Database password
INPUT_DB_PASSWORD = '123456'
# Database password for ALiYun server
# INPUT_DB_PASSWORD = '190608'

# Database dbname
INPUT_DB_DATABASE = 'dev_icampusdb'

# Database charset
INPUT_DB_CHARSET = 'utf8'

# The config of Output Database
# Database host
# OUTPUT_DB_HOST = 'ip_address'

# Database username
# OUTPUT_DB_USERNAME = 'username'

# Database password
# OUTPUT_DB_PASSWORD = 'password'

# Database dbname
# OUTPUT_DB_DATABASE = 'database_name'

# Database charset
# OUTPUT_DB_CHARSET = 'utf8'

# MAC Address
# MAC_ADDRESS = '6c0b846511a1'

# [Test] MAC Address
MAC_ADDRESS = '04ea5648c08c'

# Raw input table
RAW_INPUT_TABLE = 'person_body_status'

# UI daily status table
OUTPUT_UI_TABLE = 'student_mental_status_ld'

# UI course daily status table
OUTPUT_UI_COURSE_TABLE = 'student_mental_status_course_daily'

# UI Interest daily status table
OUTPUT_UI_INTEREST_TABLE = 'student_mental_status_interest_daily'

# Grade and Study 对比分析表
OUTPUT_UI_GRADE_STUDY_TABLE = 'student_mental_status_grade_study_daily'

#通过人脸track识别检测到的统一个track的人脸
INTERMEDIATE_TRACK_TABLE = 'person_body_status_face_track'

#在pose_stat_time内统计人体的各个姿态
INTERMEDIATE_TABLE = 'person_body_status_pose_stat_midlle'

#在face_pose_stat_time内统计用户的人脸姿态是否正常
INTERMEDIATE_RES_TABLE = 'person_body_status_face_pose_stat'

# 插入课程信息
INTERMEDIATE_COURSE_TABLE = 'person_body_status_course_info'

# 预处理完成后的数据表
INTERMEDIATE_TABLE_TRAIN = 'person_body_status_student_course_info'

# 班级学生对照表
SCHOOL_STUDENT_CLASS_TABLE = 'school_student_class_info'

# 摄像头班级对照表
SCHOOL_CAMERA_CLASS_TABLE = 'school_camera_class_info'

# 摄像头与教室对照表
SCHOOL_CAMERA_ROOM_TABLE = 'school_camera_room_info'

# 课程表
SCHOOL_COURSE_TABLE = 'school_course_info'
SCHOOL_STUDENT_COURSE_TABLE = 'school_student_course_info'

# 成绩表
SCHOOL_PERFORMANCE_TABLE = 'school_performance_info'

# 学生获奖信息表
SCHOOL_AWARD_TABLE = 'school_award_info'

# 学生考勤信息表
# 记录缺勤
STUDENT_ATTENDANCE='school_student_attendance_info'
# 记录签到
STUDENT_ATTENDANCE_EXIST='school_student_attendance_exist_info'

# The config for Metrics
# The threshold for Emotion
EMOTION_THRESHOLD_HAPPY = {
    'SMILE_FREQUENCY' : 0.2,
    'SMILE_RATIO' : 0.3 # >=
}

EMOTION_THRESHOLD_LOW = {
    'SAD_FREQUENCY' : 0.1,
    'SAD_RATIO' : 0.1 # >=
}

# The threshold for Relationship
RELATIONSHIP_THRESHOLD_GREAT = {
    'FACE_POSE_AROUND' : 0.3,
    'EMOTION_SMILE' : 0.1,
    'EMOTION_STATUS' : 0 # 开心
}

RELATIONSHIP_THRESHOLD_GOOD = {
    'FACE_POSE_AROUND' : 0.15,
    'EMOTION_SMILE' : 0.5,
    'EMOTION_STATUS' : [0, 1] # 开心, 正常
}

RELATIONSHIP_THRESHOLD_SOLITARY = {
    'FACE_POSE_LOW' : 0.6,
    'EMOTION_SMILE' : 0.99,
    'EMOTION_STATUS' : 2 # 低落
}

# The threshold for Mental
MENTAL_THRESHOLD_TIRED = {
    'BODY_STAT' : 0.1,
    'EMOTION_STATUS' : 2 # 低落
}

MENTAL_THRESHOLD_POSITIVE = {
    'BODY_STAT' : 0.05,
    'EMOTION_STATUS' : 0 # 积极
}

# The threshold for Study Status
STUDY_THREHOLD_BAD = {
    'MENTAL' : 2, # 疲惫
    'FACE_POSE_NORMAL' : 0.9, # <=
    'FACE_POSE_AROUND' : 0.9, # <=
    'FACE_POSE_AROUND_FEQ': 0.2, # >=
    'FACE_POSE_LOW' : 0.9, # <=
    'FACE_POSE_LOW_FEQ': 0.6 # >=
}

STUDY_THREHOLD_GREAT= {
    'MENTAL' : 0, # 积极
    'FACE_POSE_NORMAL' : 0.1, # >=
    'FACE_POSE_NORMAL_FEQ': 0.8 # >=
}

STUDY_THREHOLD_GOOD = {
    'MENTAL' : [0, 1], # 积极 正常
    'FACE_POSE_NORMAL' : 0.3, # >=
    'FACE_POSE_NORMAL_FEQ': 0.5 # >=
}

# The degree threshold for course interest
INTEREST_THRESHOLD = {
    'STUDY_STATUS_DAYS_RATIO': 0.6, # For demo, 考虑有即感兴趣
    'STUDY_STATUS_DAYS_LOWER': 3, # 感兴趣的天数最小值  一周一次课，45天应该有6次课程。50%的比例作为最低阈值
    'GTRADE' : 80
}

# The threshold of face_pose_stat
FACE_POSE_STAT_ABNORMAL = 0.4

# The level of Logger
# 0: FATAL 1: ERROR 2: WARNING 3: INFO 4: DEBUG
LOGGER_LEVEL = logging.DEBUG

# Lookbackwindow for Relationship and Interest
LOOKBACKWINDOW = -45 # Days

# Lookbackwindow for analysis course and study_status
ANALYSIS_LOOKBACKWINDOW = -60 # Days

# 过滤科目
FILTER_COURSES = ['体育', '班会']

# 学习与成绩四维评估中 study_stat的阈值
ANALYSIS_STUDY_STAT_THRESHOLD = 0.6  # 职教不同于K12，可以降低阈值。
ANALYSIS_STUDY_STAT_COURSE_THRESHOLD = 0.8  # 学生在课程出现的次数至少要大于等于课程总次数的80%

# The detected count threshold of each face_id
DETECTED_LOWEST_LIMIT = 500

# 批量插入的阈值
INSERT_BATCH_THRESHOLD = 10000

# 分隔计算时间的阈值
DATETIME_THRESHOLD = -1

# 保留INTERMEDIATE_TABLE_TRAIN表中历史数据的天数
DATA_RESERVED_WINDOW = -360 # 180 天

# 考勤表的数据保留历史天数。
DATA_RESERVED_ATTENDANCE_WINDOW = -360 # 默认保留最近180天

# raw 数据的保留天数
DATA_RESERVED_RAW_WINDOW = -360  # 90 默认保留90天数据

# Dynamic threshold
DYNAMIC_DELETE_PERCENTAGE = 0.2 # 计算动态阈值时，去掉高低各20%的数据

# The mininum limitation each face_track.
FACETRACK_MININUM_LIMITATION = 200 # 以face_track作为face_id的数据，要求face_track的数据量需要满足这个条件，才是有效的face_track.

# 嘉宾Id
PREFIX_GUEST = '嘉宾_' # 所有嘉宾的name都是以这个Prefix为前缀

# 教师模块的参数配置
INTERMEDIATE_TEACHER_TABLE_TRAIN = ''
INTERMEDIATE_TABLE_ONTIME = ''

OUTPUT_UI_TEA_DAILY_TABLE = ''
OUTPUT_UI_TEA_COURSE_TABLE = ''

TEACHER_EMOTION_THRESHOLD = {
    'EMOTION_ANGRY': 0.3, # >=
    'EMOTION_BAD': 0.3, # >=
    'EMOTION_HAPPY': 0.6 # >=
}

TEACHER_ETHICS_BAD_THRESHOLD = {
    "TEACHER_EMOTION": [2,3], # 愤怒 低落
    "CLOTHING_STATUS": 0.6 # >=
}

TEACHER_ETHICS_GOOD_THRESHOLD = {
    "TEACHER_EMOTION": [0,1], # 正常 开心
    "CLOTHING_STATUS": 0.6 # >=
}

TEACHER_ETHICS_GREAT_THRESHOLD = {
    "TEACHER_EMOTION": [1], # 开心
    "CLOTHING_STATUS": 0.6 # >=
}

TEACHER_TEACHING_BAD_THRESHOLD = {
    'TEACHER_EMOTION': [2,3], # 愤怒 低落
    'ONTIME': 1, # 不准时
    'ETHICS_STATUS': [3], # 不佳
    'SITTING_TIME': 0.5, # >
    'FACING_STUDENT_TIME': 0.5 # <
}

TEACHER_TEACHING_GREAT_THRESHOLD = {
    'TEACHER_EMOTION': [0], # 开心
    'ONTIME': 0, # 准时
    'ETHICS_STATUS': [1], # 良好
    'STANDING_TIME': 0.6, # >
    'FACING_STUDENT_TIME': 0.6 # >
}

TEACHER_TEACHING_GOOD_THRESHOLD = {
    'TEACHER_EMOTION': [0], # 开心
    'ONTIME': 0, # 准时
    'ETHICS_STATUS': [0], # 优秀
    'STANDING_TIME': 0.4, # >
    'FACING_STUDENT_TIME': 0.4 # >
}

# 课堂
CLASS_POSITIVITY_BAD_THRESHOLD = {
    'TEACHER_EMOTION': [2, 3], # 低落，愤怒
    'STUDENT_EMOTION_LOW': 0.5, # >
    'STUDENT_HAND_STAND': 0.05, # <
    'FACING_STUDENT_TIME': 0.2 # <
}

CLASS_POSITIVITY_GREAT_THRESHOLD = {
    'TEACHER_EMOTION': [0], # 开心
    'STUDENT_EMOTION_HAPPY': 0.6, # >
    'STUDENT_HAND_STAND': 0.2, # >
    'FACING_STUDENT_TIME': 0.5 # >
}

CLASS_CONCENTRATION_HIGH_THRESHOLD = {
    'TEACHER_ATTRITUDE': [0, 1], # 教师态度非常好 良好
    'STUDENT_STUDY': 0.5, # > 学习状态良好及以上占比超过50%
    'STUDENT_METAL': 0.5, # > 学生精神状态积极的占比超过50%
    'STUDENT_HEAD_POSE': 0.5, # > 学生平视次数超过60%
    'STUDENT_HAND_STAND': 0.2 # > 学生举手和站立的总次数超过20%
}

CLASS_CONCENTRATION_LOW_THRESHOLD = {
    'TEACHER_ATTRITUDE': [3], # 教师态度不佳
    'STUDENT_STUDY': 0.5, # > 学习状态不佳占比超过50%
    'STUDENT_METAL': 0.5, # > 学生精神状态疲惫的占比超过50%
    'STUDENT_HEAD_POSE': 0.3, # > 学生低头或左顾右盼的次数超过30%
    'STUDENT_TZTK_PZTK': 0.3 # > 学生手托着听课和趴着听课的总次数超过30%
}

CLASS_INTERACTIVITY_BAD_THRESHOLD = {
    'FACING_STUDENT_TIME': 0.2, # < 面向学生低于20%
    'STUDENT_HEAD_POSE': 0.9, # > 学生平视总次数占比超过90%
    'HEAD_POSE_AROUND': 0.1 # < 同时左顾右盼的学生人数低于 10%
}

CLASS_INTERACTIVITY_GOOD_THRESHOLD = {
    'FACING_STUDENT_TIME': 0.4, # > 面向学生超过40%
    'STUDENT_HAND_STAND': 0.3, # > 学生举手或站立总次数占比超过30%
    'HEAD_POSE_AROUND': 0.5 # > 同时左顾右盼的学生人数超过50%
}

CLASS_INTERACTIVITY_GREAT_THRESHOLD = {
    'FACING_STUDENT_TIME': 0.6, # > 面向学生超过60%
    'STUDENT_HAND_STAND': 0.2, # > 学生举手或站立总次数占比超过20%
    'HEAD_POSE_AROUND': 0.3 # > 同时左顾右盼的学生人数超过30%
}

STUDENT_STATUS_DEFAULT = {
    'student_emotion': '1',
    'student_mental_stat': '1',
    'student_study_stat': '2',
    'student_relationship': '2',
    'student_interest': ''
}
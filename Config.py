# !/usr/bin/python
# -*- coding: utf-8 -*-
# Define some constant variable.

import logging

# The config for Input Database
# Database host
INPUT_DB_HOST = '172.16.14.190'

# Database username
INPUT_DB_USERNAME = 'root'

# Database password
INPUT_DB_PASSWORD = '123456'

# Database dbname
INPUT_DB_DATABASE = 'dev_icampusdb'

# Database charset
INPUT_DB_CHARSET = 'utf8'

# The config of Output Database
# Database host
OUTPUT_DB_HOST = '172.16.14.190'

# Database username
OUTPUT_DB_USERNAME = 'root'

# Database password
OUTPUT_DB_PASSWORD = '123456'

# Database dbname
OUTPUT_DB_DATABASE = 'dev_icampusdb'

# Raw input table
RAW_INPUT_TABLE = 'person_body_status2'

# UI daily status table
OUTPUT_UI_TABLE = 'student_mental_status_ld'

# UI course daily status table
OUTPUT_UI_COURSE_TABLE = 'student_mental_status_course_daily'

# UI Interest daily status table
OUTPUT_UI_INTEREST_TABLE = 'student_mental_status_interest_daily'

# Grade and Study 对比分析表
OUTPUT_UI_GRADE_STUDY_TABLE = 'student_mental_status_grade_study_daily'

# Database charset
OUTPUT_DB_CHARSET = 'utf8'

#通过人脸track识别检测到的统一个track的人脸
INTERMEDIATE_TRACK_TABLE = 'person_body_status_face_track'

#在pose_stat_time内统计人体的各个姿态
INTERMEDIATE_TABLE = 'person_body_status_pose_stat_midlle'

#在face_pose_stat_time内统计用户的人脸姿态是否正常
INTERMEDIATE_RES_TABLE = 'person_body_status_face_pose_stat'

#预处理完成后的数据表
INTERMEDIATE_TABLE_TRAIN = 'person_body_status_course_info'

# 班级学生对照表
SCHOOL_STUDENT_CLASS_TABLE = 'school_student_class_info'

# 摄像头班级对照表
SCHOOL_CAMERA_CLASS_TABLE = 'school_camera_class_info'

# 课程表
SCHOOL_COURSE_TABLE = 'school_course_info'

# 成绩表
SCHOOL_PERFORMANCE_TABLE = 'school_performance_info'

# 学生获奖信息表
SCHOOL_AWARD_TABLE = 'school_award_info'

# The config for Metrics
# The threshold for Emotion
EMOTION_THRESHOLD_HAPPY = {
    'SMILE_FREQUENCY' : 50,
    'SMILE_RATIO' : 0.3 # >=
}

EMOTION_THRESHOLD_LOW = {
    'SAD_FREQUENCY' : 50,
    'SAD_RATIO' : 0.1 # >=
}

# The threshold for Relationship
RELATIONSHIP_THRESHOLD_GREAT = {
    'FACE_POSE_AROUND' : 0.3,
    'EMOTION_SMILE' : 0.1
}

RELATIONSHIP_THRESHOLD_GOOD = {
    'FACE_POSE_AROUND' : 0.15,
    'EMOTION_SMILE' : 0.5
}

RELATIONSHIP_THRESHOLD_SOLITARY = {
    'FACE_POSE_LOW' : 0.6,
    'EMOTION_SMILE' : 0.99
}

# The threshold for Mental
MENTAL_THRESHOLD_TIRED = {
    'BODY_STAT' : 10,
    'EMOTION_SMILE' : 3,
    'EMOTION_LOW' : 10
}

MENTAL_THRESHOLD_POSITIVE = {
    'BODY_STAT' : 2,
    'EMOTION_SMILE' : 10
}

# The threshold for Study Status
STUDY_THREHOLD_BAD = {
    'MENTAL' : 2, # 疲惫
    'FACE_POSE_NORMAL' : 0.9 # <=
}

STUDY_THREHOLD_GREAT= {
    'MENTAL' : 0, # 积极
    'FACE_POSE_NORMAL' : 0.1 # >=
}

STUDY_THREHOLD_GOOD = {
    'MENTAL' : [0, 1], # 积极 正常
    'FACE_POSE_NORMAL' : 0.4 # >=
}

# The degree threshold for course interest
INTEREST_THRESHOLD = {
    'STUDY_STATUS_DAYS': 18, # 30 * 0.6 = 18
    'GTRADE' : 80
}

# The threshold of face_pose_stat
FACE_POSE_STAT_ABNORMAL = 0.4

# The level of Logger
# 0: FATAL 1: ERROR 2: WARNING 3: INFO 4: DEBUG
LOGGER_LEVEL = logging.INFO

# Lookbackwindow for Relationship and Interest
LOOKBACKWINDOW = -30 # Days

# Lookbackwindow for analysis course and study_status
ANALYSIS_LOOKBACKWINDOW = 30 # Days

# 学习与成绩思维评估中 study_stat的阈值
ANALYSIS_STUDY_STAT_THRESHOLD = 20 # Days

# The detected count threshold of each face_id
DETECTED_LOWEST_LIMIT = 500

# 批量插入的阈值
INSERT_BATCH_THRESHOLD = 10000
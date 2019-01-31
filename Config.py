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
OUTPUT_DN_HOST = '172.16.14.190'

# Database username
OUTPUT_DB_USERNAME = 'root'

# Database password
OUTPUT_DB_PASSWORD = '123456'

# Database dbname
OUTPUT_DB_DATABASE = 'iMental'

# Intermediate result table
INTERMEDIATE_TABLE = 'im_person_data'
INTERMEDIATE_TABLE_TRAIN = 'im_train_data'

# Raw input table
RAW_INPUT_TABLE = 'person_body_status'

# UI daily status table
OUTPUT_UI_TABLE = 'student_mental_status_ld'

# UI course daily status table
OUTPUT_UI_COURSE_TABLE = 'student_mental_status_course_daily'

# Database charset
OUTPUT_DB_CHARSET = 'utf8'

# The config for Metrics
# The threshold for Emotion
EMOTION_THRESHOLD_HAPPY = {
    'SMILE_FREQUENCY' : 50,
    'SMILE_RATIO' : 0.3 # >
}

EMOTION_THRESHOLD_LOW = {
    'SAD_FREQUENCY' : 50,
    'SAD_RATIO' : 0.1 # >
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
    'EMOTION_HAPPY' : 10
}

# The threshold for Study Status
STUDY_THREHOLD_BAD = {
    'MENTAL' : 2, # 疲惫
    'FACE_POSE_NORMAL' : 0.9 # <
}

STUDY_THREHOLD_GREAT= {
    'MENTAL' : 0, # 积极
    'FACE_POSE_NORMAL' : 0.1 # >
}

STUDY_THREHOLD_GOOD = {
    'MENTAL' : [0, 1], # 积极 正常
    'FACE_POSE_NORMAL' : 0.4 # >
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
LOGGER_LEVEL = logging.DEBUG

# Lookbackwindow for Relationship and Interest
LOOKBACKWINDOW = -30 # Days

# The detected count threshold of each face_id
DETECTED_LOWEST_LIMIT = 500
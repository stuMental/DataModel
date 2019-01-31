# !/usr/bin/python
# -*- coding: utf8 -*-

class ClassAPI(object):
    """ Call some APIs of School """
    def __init__(self):
        super(ClassInfo, self).__init__()

    @staticmethod
    def get_class_info(self, student_number):
        ''' Get GradeNumber and ClassNumber according to student number （face_id） by API '''
        return ['grade_number', 'class_number', 'people_number', 'head_teacher']

    @staticmethod
    def get_course_name(self, camera_id, timespan):
        ''' Get course number according to camera_id and timespan by API '''
        return ['course_name', 'teacher_name']

    @staticmethod
    def get_grade(self, student_number, course_name):
        '''
            Get the grade of the course_name for this student_number
            grade: the student's grade
            grade_level: the distribution of the grade
        '''
        return ['grade', 'grade_level ']

    @staticmethod
    def get_award_course(self, student_number):
        '''
            Get the student's award according to the student number (face_id)
            course_name: the course name of award, such as: Math, English
            award_level: the level of award, such as First-prize.
        '''
        return ['course_name', 'award_level']
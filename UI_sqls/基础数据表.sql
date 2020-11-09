-- 根据年级和班级获取class_id
SELECT class_id FROM school_camera_class_info WHERE grade_name = '2017' AND class_name = '17动漫' LIMIT 1;

-- 按天统计课程中学生的头部姿态情况
-- 0：平视
-- 1: 左顾右盼
-- 2: 低头
SELECT
    t.course_name,
    t.face_pose,
    ROUND(t.cnt / s.total * 100, 2) as score
FROM (
    SELECT
        course_name,
        face_pose,
        SUM(total) AS cnt
    FROM student_action_course_face_pose_result
    WHERE face_pose != '-1' AND face_pose != 'unknown' AND dt = '2019-06-28' AND course_name != 'rest' AND class_id = '19'
    GROUP BY course_name, face_pose
) t join (
    SELECT
        course_name,
        SUM(total) AS total
    FROM student_action_course_face_pose_result
    WHERE face_pose != '-1' AND face_pose != 'unknown' AND dt = '2019-06-28' AND course_name != 'rest' AND class_id = '19'
    GROUP BY course_name
) s ON t.course_name = s.course_name
ORDER BY t.course_name ASC, t.face_pose ASC;


-- 按天统计课程中学生的表情情况
-- 0：正常
-- 1: 开心
-- 2: 低落
SELECT
    t.course_name,
    t.face_emotion,
    ROUND(t.cnt / s.total * 100, 2) as score
FROM (
    SELECT
        course_name,
        face_emotion,
        SUM(total)AS cnt
    FROM student_action_course_face_emotion_result
    WHERE face_emotion != '-1' AND face_emotion != 'unknown' AND dt = '2019-06-28' AND course_name != 'rest' AND class_id = '19'
    GROUP BY course_name, face_emotion
) t join (
    SELECT
        course_name,
        SUM(total) AS total
    FROM student_action_course_face_emotion_result
    WHERE face_emotion != '-1' AND face_emotion != 'unknown' AND dt = '2019-06-28' AND course_name != 'rest' AND class_id = '19'
    GROUP BY course_name
) s ON t.course_name = s.course_name
ORDER BY t.course_name ASC, t.face_emotion ASC;


-- 按天统计课程中学生的身体姿态
-- 0：正常姿态
-- 1: 站立
-- 2: 举手
-- 3：睡觉
-- 4：手托头听课
-- 5：趴着听课
SELECT
    t.course_name,
    t.body_stat,
    ROUND(t.cnt / s.total * 100, 2) as score
FROM (
    SELECT
        course_name,
        body_stat,
        SUM(total) AS cnt
    FROM student_action_course_body_stat_result
    WHERE body_stat != '-1' AND body_stat != 'unknowm' AND dt = '2019-06-28' AND course_name != 'rest' AND class_id = '19'
    GROUP BY course_name, body_stat
) t join (
    SELECT
        course_name,
        SUM(total) AS total
    FROM student_action_course_body_stat_result
    WHERE body_stat != '-1' AND body_stat != 'unknowm' AND dt = '2019-06-28' AND course_name != 'rest' AND class_id = '19'
    GROUP BY course_name
) s ON t.course_name = s.course_name
ORDER BY t.course_name ASC, t.body_stat ASC;
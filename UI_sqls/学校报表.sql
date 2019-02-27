--今日考勤
    SELECT t1.time_gap, t1.grade_name, IF(t2.num IS NULL, 0, t2.num)
    FROM (
        SELECT CONCAT(from_unixtime(start_time,'%H:%i'),'_',from_unixtime(end_time,'%H:%i')) as time_gap,grade_name
        FROM school_course_info
        WHERE dt={day}
        GROUP BY start_time,end_time,grade_name
    )t1 LEFT JOIN (
        SELECT CONCAT(from_unixtime(start_time,'%H:%i'),'_',from_unixtime(end_time,'%H:%i')) as time_gap, grade_name, count(*) AS num
        FROM school_student_attendance_info
        WHERE dt={day}
        GROUP BY start_time,end_time,grade_name
    )t2 ON t1.time_gap=t2.time_gap AND t1.grade_name=t2.grade_name

--校园安全预警 
    --情绪不佳
    SELECT grade_name, GROUP_CONCAT(student_name separator ',')
    FROM (
        SELECT student_number, student_name, grade_name, count(*) as num
        FROM student_mental_status_ld
        WHERE dt>=date_format(date_add({day}, interval -15 day), '%Y%m%d') AND dt<={day} AND face_emotion='2'
        GROUP BY student_number, student_name, grade_name
        HAVING num>=6
    )t1 
    GROUP BY grade_name

    --精神状态不佳
    SELECT grade_name, GROUP_CONCAT(student_name separator ',')
    FROM (
        SELECT student_number, student_name, grade_name, count(*) as num
        FROM student_mental_status_ld
        WHERE dt>=date_format(date_add({day}, interval -15 day), '%Y%m%d') AND dt<={day} AND student_mental_stat='2'
        GROUP BY student_number, student_name, grade_name
        HAVING num>=6
    )t1 
    GROUP BY grade_name

    --学习状态不佳
    SELECT grade_name, GROUP_CONCAT(student_name separator ',')
    FROM (
        SELECT student_number, student_name, count(*) as num
        FROM student_mental_status_ld
        WHERE dt>=date_format(date_add({day}, interval -15 day), '%Y%m%d') AND dt<={day} AND student_study_stat='3'
        GROUP BY student_number, student_name, grade_name
        HAVING num>=6
    )t1 
    GROUP BY grade_name

-- 今日心理健康状态分布
    -- 情绪状态
    SELECT
        t1.student_emotion, ROUND(1.0 * t1.num / t2.total * 100, 2) AS percentage
    FROM
    (
        SELECT
            student_emotion, COUNT(*) AS num
        FROM student_mental_status_ld
        WHERE dt = select_time_param
        GROUP BY student_emotion
    ) t1 JOIN
    (
        SELECT
            COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE dt = select_time_param
    ) t2;
    
    -- 人际关系
    SELECT
        t1.student_relationship, ROUND(1.0 * t1.num / t2.total * 100, 2) AS percentage
    FROM
    (
        SELECT
            student_relationship, COUNT(*) AS num
        FROM student_mental_status_ld
        WHERE dt = select_time_param
        GROUP BY student_relationship
    ) t1 JOIN
    (
        SELECT
            COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE dt = select_time_param
    ) t2;
    
-- 今日学业自律性分布
    -- 学习状态
    SELECT
        t1.student_study_stat, ROUND(1.0 * t1.num / t2.total * 100, 2) AS percentage
    FROM
    (
        SELECT
            student_study_stat, COUNT(*) AS num
        FROM student_mental_status_ld
        WHERE dt = select_time_param
        GROUP BY student_study_stat
    ) t1 JOIN
    (
        SELECT
            COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE dt = select_time_param
    ) t2;
    
    -- 精神状态
    SELECT
        t1.student_mental_stat, ROUND(1.0 * t1.num / t2.total * 100, 2) AS percentage
    FROM
    (
        SELECT
            student_mental_stat, COUNT(*) AS num
        FROM student_mental_status_ld
        WHERE dt = select_time_param
        GROUP BY student_mental_stat
    ) t1 JOIN
    (
        SELECT
            COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE dt = select_time_param
    ) t2;
    
-- 学科兴趣分布
    SELECT
        student_interest, COUNT(*) AS total
    FROM student_mental_status_interest_daily
    WHERE dt = select_time_param
    GROUP BY student_interest
    ORDER BY student_interest ASC;
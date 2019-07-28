-- 班级报表
    -- 今日考勤
    SELECT t1.time_gap, t1.course_name, IF(t2.num IS NULL, 0, t2.num), IF(t2.name IS NULL, '', t2.name)
    FROM (
        SELECT CONCAT(SUBSTR(start_time,1,5),'_',SUBSTR(end_time,1,5)) as time_gap, course_name
        FROM school_course_info
        WHERE weekday=dayofweek(date_format({day}, "%y-%m-%d")) AND grade_name={grade_name} AND class_name={class_name}
    )t1 LEFT JOIN (
        SELECT CONCAT(SUBSTR(start_time,1,5),'_',SUBSTR(end_time,1,5)) as time_gap, course_name, count(*) AS num, GROUP_CONCAT(student_name separator ',') as name
        FROM school_student_attendance_info
        WHERE dt={day} AND grade_name={grade_name} AND class_name={class_name}
        GROUP BY start_time,end_time,course_name
    )t2 ON t1.time_gap=t2.time_gap AND t1.course_name=t2.course_name

-- 校园安全预警
    --情绪状态不佳
    SELECT IF(names IS NULL, '无', names) as names
    FROM (
        SELECT GROUP_CONCAT(student_name separator ',') as names
        FROM (
            SELECT student_number, student_name, count(*) as num
            FROM student_mental_status_ld
            WHERE dt>=date_add({day}, interval -15 day) AND dt<={day} AND student_emotion='2' AND grade_name={grade_name} AND class_name={class_name}
            GROUP BY student_number, student_name
            HAVING num>=6
        )t1
    )t2;

    --精神状态不佳
    SELECT IF(names IS NULL, '无', names) as names
    FROM (
        SELECT GROUP_CONCAT(student_name separator ',') as names
        FROM (
            SELECT student_number, student_name, count(*) as num
            FROM student_mental_status_ld
            WHERE dt>=date_add({day}, interval -15 day) AND dt<={day} AND student_mental_stat='2' AND grade_name={grade_name} AND class_name={class_name}
            GROUP BY student_number, student_name
            HAVING num>=6
        )t1
    )t2 

    --学习状态不佳
    SELECT IF(names IS NULL, '无', names) as names
    FROM (
        SELECT GROUP_CONCAT(student_name separator ',') as names
        FROM (
            SELECT student_number, student_name, count(*) as num
            FROM student_mental_status_ld
            WHERE dt>=date_add({day}, interval -15 day) AND dt<={day} AND student_study_stat='3' AND grade_name={grade_name} AND class_name={class_name}
            GROUP BY student_number, student_name
            HAVING num>=6
        )t1
    )t2 
-- 今日心理状态分布
    -- 情绪状态
    SELECT
        t1.student_emotion, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
    FROM
    (
        SELECT
            student_emotion, COUNT(*) AS num
        FROM student_mental_status_ld
        WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
        GROUP BY student_emotion
    ) t1 JOIN
    (
        SELECT
            COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
    ) t2;
    
    -- 学生名单
    SELECT
        DISTINCT student_number, student_name
    FROM student_mental_status_ld
    WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
    ORDER BY student_emotion DESC;

    -- 人际关系
    SELECT
        t1.student_relationship, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
    FROM
    (
        SELECT
            student_relationship, COUNT(*) AS num
        FROM student_mental_status_ld
        WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
        GROUP BY student_relationship
    ) t1 JOIN
    (
        SELECT
            COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
    ) t2;
    
    -- 学生名单
    SELECT
        DISTINCT student_number, student_name
    FROM student_mental_status_ld
    WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
    ORDER BY student_relationship DESC;
    
-- 今日学业自律性分布
    -- 学习状态
    SELECT
        t1.student_study_stat, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
    FROM
    (
        SELECT
            student_study_stat, COUNT(*) AS num
        FROM student_mental_status_ld
        WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
        GROUP BY student_study_stat
    ) t1 JOIN
    (
        SELECT
            COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
    ) t2;
    
    -- 学生名单
    SELECT
        DISTINCT student_number, student_name
    FROM student_mental_status_ld
    WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
    ORDER BY student_study_stat DESC;
    
    -- 精神状态
    SELECT
        t1.student_mental_stat, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
    FROM
    (
        SELECT
            student_mental_stat, COUNT(*) AS num
        FROM student_mental_status_ld
        WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
        GROUP BY student_mental_stat
    ) t1 JOIN
    (
        SELECT
            COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
    ) t2;
    
    -- 学生名单
    SELECT
        DISTINCT student_number, student_name
    FROM student_mental_status_ld
    WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
    ORDER BY student_mental_stat DESC;
    
-- 历史状态信息
    -- 情绪状态
    SELECT
        t1.dt, t1.student_emotion, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
    FROM
    (
        SELECT
            dt, student_emotion, COUNT(*) AS num
        FROM student_mental_status_ld
        WHERE grade_name = 'param' and class_name = 'param' AND dt >= date_add(end_time_param, interval -15 day) AND dt <= end_time_param
        GROUP BY dt, student_emotion
    ) t1 JOIN
    (
        SELECT
            dt, COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE grade_name = 'param' and class_name = 'param' AND dt >= date_add(end_time_param, interval -15 day) AND dt <= end_time_param
        GROUP BY dt
    ) t2 ON t1.dt = t2.dt
    ORDER BY dt ASC;
    
    -- 精神状态
    SELECT
        t1.dt, t1.student_mental_stat, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
    FROM
    (
        SELECT
            dt, student_mental_stat, COUNT(*) AS num
        FROM student_mental_status_ld
        WHERE grade_name = 'param' and class_name = 'param' AND dt >= date_add(end_time_param, interval -15 day) AND dt <= end_time_param
        GROUP BY dt, student_mental_stat
    ) t1 JOIN
    (
        SELECT
            dt, COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE grade_name = 'param' and class_name = 'param' AND dt >= date_add(end_time_param, interval -15 day) AND dt <= end_time_param
        GROUP BY dt
    ) t2 ON t1.dt = t2.dt
    ORDER BY dt ASC;
    
    -- 学习状态
    SELECT
        t1.dt, t1.student_study_stat, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
    FROM
    (
        SELECT
            dt, student_study_stat, COUNT(*) AS num
        FROM student_mental_status_ld
        WHERE grade_name = 'param' and class_name = 'param' AND dt >= date_add(end_time_param, interval -15 day) AND dt <= end_time_param
        GROUP BY dt, student_study_stat
    ) t1 JOIN
    (
        SELECT
            dt, COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE grade_name = 'param' and class_name = 'param' AND dt >= date_add(end_time_param, interval -15 day) AND dt <= end_time_param
        GROUP BY dt
    ) t2 ON t1.dt = t2.dt
    ORDER BY dt ASC;
    -- 学科兴趣分布
    SELECT
        student_interest, COUNT(*) AS total
    FROM student_mental_status_interest_daily
    WHERE grade_name = 'param' AND class_name = 'param' AND dt = select_time_param
    GROUP BY student_interest
    ORDER BY student_interest ASC;
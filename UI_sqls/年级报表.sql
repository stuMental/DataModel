--今日考勤
    SELECT CONCAT(SUBSTR(start_time,1,5),'_',SUBSTR(end_time,1,5)) as time_gap, class_name, count(*) AS num
    FROM school_student_attendance_info
    WHERE dt={day} AND college_name = 'param' AND grade_name={grade_name}
    GROUP BY start_time,end_time,class_name
    ORDER BY time_gap ASC;

--校园安全预警
    --情绪状态不佳
    SELECT class_name, GROUP_CONCAT(student_name separator ',')
    FROM (
        SELECT student_number, student_name, class_name, count(*) as num
        FROM student_mental_status_ld
        WHERE dt>=date_add({day}, interval -15 day) AND dt<={day} AND student_emotion='2' AND college_name = 'param' AND grade_name={grade_name}
        GROUP BY student_number, student_name, class_name
        HAVING num>=6
    )t1
    GROUP BY class_name

    --精神状态不佳
    SELECT class_name, GROUP_CONCAT(student_name separator ',')
    FROM (
        SELECT student_number, student_name, class_name, count(*) as num
        FROM student_mental_status_ld
        WHERE dt>=date_add({day}, interval -15 day) AND dt<={day} AND student_mental_stat='2' AND college_name = 'param' AND grade_name={grade_name}
        GROUP BY student_number, student_name, class_name
        HAVING num>=6
    )t1
    GROUP BY class_name

    --学习状态不佳
    SELECT class_name, GROUP_CONCAT(student_name separator ',')
    FROM (
        SELECT student_number, student_name, class_name, count(*) as num
        FROM student_mental_status_ld
        WHERE dt>=date_add({day}, interval -15 day) AND dt<={day} AND student_study_stat='3' AND college_name = 'param' AND grade_name={grade_name}
        GROUP BY student_number, student_name, class_name
        HAVING num>=6
    )t1
    GROUP BY class_name

-- 今日心理健康状态分布
    -- 情绪状态
    SELECT
        t1.student_emotion, ROUND(1.0 * t1.num / t2.total * 100, 2) AS percentage
    FROM
    (
        SELECT
            student_emotion, COUNT(*) AS num
        FROM student_mental_status_ld
        WHERE college_name = 'param' AND grade_name = 'param' AND dt = select_time_param
        GROUP BY student_emotion
    ) t1 JOIN
    (
        SELECT
            COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE college_name = 'param' AND grade_name = 'param' AND dt = select_time_param
    ) t2;

    -- 人际关系
    SELECT
        t1.student_relationship, ROUND(1.0 * t1.num / t2.total * 100, 2) AS percentage
    FROM
    (
        SELECT
            student_relationship, COUNT(*) AS num
        FROM student_mental_status_ld
        WHERE college_name = 'param' AND grade_name = 'param' AND dt = select_time_param
        GROUP BY student_relationship
    ) t1 JOIN
    (
        SELECT
            COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE college_name = 'param' AND grade_name = 'param' AND dt = select_time_param
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
        WHERE college_name = 'param' AND grade_name = 'param' AND dt = select_time_param
        GROUP BY student_study_stat
    ) t1 JOIN
    (
        SELECT
            COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE college_name = 'param' AND grade_name = 'param' AND dt = select_time_param
    ) t2;

    -- 精神状态
    SELECT
        t1.student_mental_stat, ROUND(1.0 * t1.num / t2.total * 100, 2) AS percentage
    FROM
    (
        SELECT
            student_mental_stat, COUNT(*) AS num
        FROM student_mental_status_ld
        WHERE college_name = 'param' AND grade_name = 'param' AND dt = select_time_param
        GROUP BY student_mental_stat
    ) t1 JOIN
    (
        SELECT
            COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE college_name = 'param' AND grade_name = 'param' AND dt = select_time_param
    ) t2;

-- 学科兴趣分布
    SELECT
        student_interest, COUNT(*) AS total
    FROM student_mental_status_interest_daily
    WHERE college_name = 'param' AND grade_name = 'param' AND dt = select_time_param
    GROUP BY student_interest
    ORDER BY student_interest ASC;
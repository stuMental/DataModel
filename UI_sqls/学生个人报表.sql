-- 个性发展
    -- 学科兴趣
    SELECT
        CONCAT('- ', student_interest) AS student_interest
    FROM student_mental_status_interest_daily
    WHERE student_number = 'param' AND dt >= start_time_param AND dt <= end_time_param
    GROUP BY student_interest
    ORDER BY student_interest ASC;

    -- 体艺发展
    SELECT
        CONCAT('- ', award_type) AS award_type
    FROM school_award_info
    WHERE student_number = 'param' AND dt >= start_time_param AND dt <= end_time_param
    GROUP BY award_type
    ORDER BY award_type ASC;

-- 心理健康状态
    -- 人际关系
    SELECT
        t.student_relationship
    FROM
    (
        SELECT
            student_relationship, COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE student_number = 'param'  AND student_relationship != '' AND dt >= start_time_param AND dt <= end_time_param
        GROUP BY student_relationship
    ) t
    ORDER BY t.student_relationship ASC, t.total DESC
    LIMIT 0, 1;

    -- 情绪状态
    SELECT
        t1.student_emotion, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
    FROM
    (
        SELECT
            student_emotion, COUNT(*) AS num
        FROM student_mental_status_ld
        WHERE student_number = 'param' AND dt >= start_time_param AND dt <= end_time_param
        GROUP BY student_emotion
    ) t1 JOIN
    (
        SELECT
            COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE student_number = 'param' AND dt >= start_time_param AND dt <= end_time_param
    ) t2;

    -- 情绪状态历史趋势图
    SELECT
        dt, student_emotion
    FROM student_mental_status_ld
    WHERE student_number = 'param' AND dt >= start_time_param AND dt <= end_time_param
    ORDER BY dt ASC;

-- 学业自律性
    -- 精神状态
    SELECT
        t1.student_mental_stat, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
    FROM
    (
        SELECT
            student_mental_stat, COUNT(*) AS num
        FROM student_mental_status_ld
        WHERE student_number = 'param' AND dt >= start_time_param AND dt <= end_time_param
        GROUP BY student_mental_stat
    ) t1 JOIN
    (
        SELECT
            COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE student_number = 'param' AND dt >= start_time_param AND dt <= end_time_param
    ) t2;

    -- 精神状态历史趋势图
    SELECT
        dt, student_mental_stat
    FROM student_mental_status_ld
    WHERE student_number = 'param' AND dt >= start_time_param AND dt <= end_time_param
    ORDER BY dt ASC;

    -- 学习状态
    SELECT
        t1.student_study_stat, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
    FROM
    (
        SELECT
            student_study_stat, COUNT(*) AS num
        FROM student_mental_status_ld
        WHERE student_number = 'param' AND dt >= start_time_param AND dt <= end_time_param
        GROUP BY student_study_stat
    ) t1 JOIN
    (
        SELECT
            COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE student_number = 'param' AND dt >= start_time_param AND dt <= end_time_param
    ) t2;

    -- 学习状态历史趋势图
    SELECT
        dt, student_study_stat
    FROM student_mental_status_ld
    WHERE student_number = 'param' AND dt >= start_time_param AND dt <= end_time_param
    ORDER BY dt ASC;

-- 学生综合状态
    SELECT
        ROUND((1.0 * IFNULL(t5.emotion_count, 0)) / t1.total, 2) AS emotion, ROUND((1.0 * IFNULL(t2.study_count, 0)) / t1.total, 2) AS study, ROUND((1.0 * IFNULL(t3.mental_count, 0)) / t1.total, 2) AS mental, ROUND((1.0 * IFNULL(t4.relationship_count, 0)) / t1.total, 2) AS relationship
    FROM
    (
        SELECT
            COUNT(*) AS total
        FROM student_mental_status_ld
        WHERE student_number = 'param' AND dt >= start_time_param AND dt <= end_time_param
    ) t1 JOIN
    (
        SELECT
            COUNT(*) AS study_count
        FROM student_mental_status_ld
        WHERE student_number = 'param' AND dt >= start_time_param AND dt <= end_time_param AND student_study_stat != '3'
    ) t2 JOIN
    (
        SELECT
            COUNT(*) AS mental_count
        FROM student_mental_status_ld
        WHERE student_number = 'param' AND dt >= start_time_param AND dt <= end_time_param AND student_mental_stat != '2'
    ) t3 JOIN
    (
        SELECT
            COUNT(*) AS relationship_count
        FROM student_mental_status_ld
        WHERE student_number = 'param' AND dt >= start_time_param AND dt <= end_time_param AND student_relationship != '3' AND student_relationship != ''
    ) t4 JOIN
    (
        SELECT
            COUNT(*) AS emotion_count
        FROM student_mental_status_ld
        WHERE student_number = 'param' AND dt >= start_time_param AND dt <= end_time_param AND student_emotion != '2'
    ) t5;

-- 学习状态分析
    SELECT
        course_name, grade_level, study_level
    FROM student_mental_status_grade_study_daily
    WHERE student_number = 'param' AND dt >= start_time_param AND dt <= end_time_param
    ORDER BY course_name ASC;
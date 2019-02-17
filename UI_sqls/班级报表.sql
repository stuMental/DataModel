-- 班级报表
    -- 今日心理状态分布
        -- 情绪状态
        SELECT
            t1.student_emotion, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
        FROM
        (
            SELECT
                class_id, student_emotion, COUNT(*) AS num
            FROM student_mental_status_ld
            WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
            GROUP BY class_id, student_emotion
        ) t1 JOIN
        (
            SELECT
                class_id, COUNT(*) AS total
            FROM student_mental_status_ld
            WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
            GROUP BY class_id
        ) t2 ON t1.class_id = t2.class_id;
        
        -- 学生名单
        SELECT
            DISTINCT student_number, student_name
        FROM student_mental_status_ld
        WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param AND student_emotion = 'param';

        -- 人际关系
        SELECT
            t1.student_relationship, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
        FROM
        (
            SELECT
                class_id, student_relationship, COUNT(*) AS num
            FROM student_mental_status_ld
            WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
            GROUP BY class_id, student_relationship
        ) t1 JOIN
        (
            SELECT
                class_id, COUNT(*) AS total
            FROM student_mental_status_ld
            WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
            GROUP BY class_id
        ) t2 ON t1.class_id = t2.class_id;
        
        -- 学生名单
        SELECT
            DISTINCT student_number, student_name
        FROM student_mental_status_ld
        WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param AND student_relationship = 'param';
    
    -- 今日学业自律性分布
        -- 学习状态
        SELECT
            t1.student_study_stat, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
        FROM
        (
            SELECT
                class_id, student_study_stat, COUNT(*) AS num
            FROM student_mental_status_ld
            WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
            GROUP BY class_id, student_study_stat
        ) t1 JOIN
        (
            SELECT
                class_id, COUNT(*) AS total
            FROM student_mental_status_ld
            WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
            GROUP BY class_id
        ) t2 ON t1.class_id = t2.class_id;
        
        -- 学生名单
        SELECT
            DISTINCT student_number, student_name
        FROM student_mental_status_ld
        WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param AND student_study_stat = 'param';
        
        -- 精神状态
        SELECT
            t1.student_mental_stat, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
        FROM
        (
            SELECT
                class_id, student_mental_stat, COUNT(*) AS num
            FROM student_mental_status_ld
            WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
            GROUP BY class_id, student_mental_stat
        ) t1 JOIN
        (
            SELECT
                class_id, COUNT(*) AS total
            FROM student_mental_status_ld
            WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param
            GROUP BY class_id
        ) t2 ON t1.class_id = t2.class_id;
        
        -- 学生名单
        SELECT
            DISTINCT student_number, student_name
        FROM student_mental_status_ld
        WHERE grade_name = 'param' and class_name = 'param' AND dt = selected_time_param AND student_mental_stat = 'param';
        
    -- 历史状态信息
        -- 情绪状态
        SELECT
            t1.dt, t1.student_emotion, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
        FROM
        (
            SELECT
                dt, student_emotion, COUNT(*) AS num
            FROM student_mental_status_ld
            WHERE grade_name = 'param' and class_name = 'param' AND dt >= start_time_param AND dt <= end_time_param
            GROUP BY dt, student_emotion
        ) t1 JOIN
        (
            SELECT
                dt, COUNT(*) AS total
            FROM student_mental_status_ld
            WHERE grade_name = 'param' and class_name = 'param' AND dt >= start_time_param AND dt <= end_time_param
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
            WHERE grade_name = 'param' and class_name = 'param' AND dt >= start_time_param AND dt <= end_time_param
            GROUP BY dt, student_mental_stat
        ) t1 JOIN
        (
            SELECT
                dt, COUNT(*) AS total
            FROM student_mental_status_ld
            WHERE grade_name = 'param' and class_name = 'param' AND dt >= start_time_param AND dt <= end_time_param
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
            WHERE grade_name = 'param' and class_name = 'param' AND dt >= start_time_param AND dt <= end_time_param
            GROUP BY dt, student_study_stat
        ) t1 JOIN
        (
            SELECT
                dt, COUNT(*) AS total
            FROM student_mental_status_ld
            WHERE grade_name = 'param' and class_name = 'param' AND dt >= start_time_param AND dt <= end_time_param
            GROUP BY dt
        ) t2 ON t1.dt = t2.dt
        ORDER BY dt ASC;
        
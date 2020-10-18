-- 如果数据结果中，缺少的维度均显示为0.
-- 除了type的过滤条件意外，其余条件均需要从前端输入。


-- 教师课堂互动类型
SELECT
    ROUND(AVG(rt), 2) AS rt, ROUND(AVG(ch), 2) AS ch
FROM teacher_course_type_daily
WHERE teacher_id = '202001' AND course_id = '语文' AND college_name = '某职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND dt >= '2020-06-04' AND dt <= '2020-06-07';

-- 师生行为序列
SELECT
    `type`
FROM teacher_student_behavior_result
WHERE teacher_id = '202001' AND course_id = '语文' AND college_name = '某职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND dt >= '2020-06-04' AND dt <= '2020-06-07'
ORDER BY unix_timestamp ASC;

-- 学生行为分析
-- type:0 为教师行为
-- type:1 为学生行为
-- 所以where条件中type的过滤条件不用变
SELECT
    stu.`action` AS `action`,
    ROUND(stu.action_cnt / tmp.total, 4) AS percentage
FROM (
    SELECT
        `action`,
        count(1) AS action_cnt
    FROM teacher_student_behavior_result
    WHERE `type` = 1 AND teacher_id = '202001' AND course_id = '语文' AND college_name = '某职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND dt >= '2020-06-04' AND dt <= '2020-06-07'
    GROUP BY `action`
) AS stu JOIN (
    SELECT
        COUNT(1) AS total
    FROM teacher_student_behavior_result
    WHERE teacher_id = '202001' AND course_id = '语文' AND college_name = '某职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND dt >= '2020-06-04' AND dt <= '2020-06-07'
) AS tmp;


-- 教师行为分析
-- type:0 为教师行为
-- type:1 为学生行为
-- 所以where条件中type的过滤条件不用变
SELECT
    tea.`action` AS `action`,
    ROUND(tea.action_cnt / tmp.total, 4) AS percentage
FROM (
    SELECT
        `action`,
        count(1) AS action_cnt
    FROM teacher_student_behavior_result
    WHERE `type` = 0 AND teacher_id = '202001' AND course_id = '语文' AND college_name = '某职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND dt >= '2020-06-04' AND dt <= '2020-06-07'
    GROUP BY `action`
) AS tea JOIN (
    SELECT
        COUNT(1) AS total
    FROM teacher_student_behavior_result
    WHERE teacher_id = '202001' AND course_id = '语文' AND college_name = '某职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND dt >= '2020-06-04' AND dt <= '2020-06-07'
) AS tmp;

----------------------------------------
-- 0：开心
-- 1：正常
-- 2：愤怒
----------------------------------------
-- 教学情绪
SELECT
    ROUND(emotion.happy_cnt / tmp.total, 4) AS happy_rate,
    ROUND(emotion.normal_cnt / tmp.total, 4) AS normal_rate,
    ROUND(emotion.angry_cnt / tmp.total, 4) AS angry_rate
FROM (
    SELECT
        SUM(happy) AS happy_cnt,
        SUM(normal) AS normal_cnt,
        SUM(angry) AS angry_cnt
    FROM teacher_emotion_daily
    WHERE teacher_id = '202001' AND course_id = '语文' AND college_name = '某职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND dt >= '2020-06-04' AND dt <= '2020-06-07'
) AS emotion JOIN (
    SELECT
        SUM(happy + normal + angry) AS total
    FROM teacher_emotion_daily
    WHERE teacher_id = '202001' AND course_id = '语文' AND college_name = '某职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND dt >= '2020-06-04' AND dt <= '2020-06-07'
) tmp;


----------------------------------------
-- 0：开心
-- 1：正常
-- 2：愤怒
----------------------------------------
-- 教学情绪状态趋势
SELECT
    emotion.dt AS dt,
    ROUND(emotion.happy / tmp.total, 4) AS happy_rate,
    ROUND(emotion.normal / tmp.total, 4) AS normal_rate,
    ROUND(emotion.angry / tmp.total, 4) AS angry_rate
FROM (
    SELECT
        dt,
        happy,
        normal,
        angry
    FROM teacher_emotion_daily
    WHERE teacher_id = '202001' AND course_id = '语文' AND college_name = '某职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND dt >= '2020-06-04' AND dt <= '2020-06-07'
) AS emotion JOIN (
    SELECT
        dt,
        happy + normal + angry AS total
    FROM teacher_emotion_daily
    WHERE teacher_id = '202001' AND course_id = '语文' AND college_name = '某职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND dt >= '2020-06-04' AND dt <= '2020-06-07'
    GROUP BY dt
) tmp ON emotion.dt = tmp.dt
ORDER BY dt ASC;


----------------------------------------
-- 教师教学状态
-- 总评得分
-- 教学表情
-- 教学行为
-- 上课准时
SELECT
    ROUND(AVG(score), 2) AS score,
    ROUND(AVG(emotion), 2) AS emotion,
    ROUND(AVG(behavior), 2) AS behavior,
    ROUND(AVG(ontime), 2) AS ontime
FROM teacher_status_daily
WHERE teacher_id = '202001' AND course_id = '语文' AND college_name = '某职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND dt >= '2020-06-04' AND dt <= '2020-06-07'
;

-- 教师教学状态趋势
SELECT
    dt,
    score
FROM teacher_status_daily
WHERE teacher_id = '202001' AND course_id = '语文' AND college_name = '某职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND dt >= '2020-06-04' AND dt <= '2020-06-07'
ORDER BY dt ASC;
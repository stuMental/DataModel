-- 如果数据结果中，缺少的维度均显示为0.

-- 教学效果综合状态
SELECT
    student_study_score, student_emotion_score, student_mental_score, class_concentration_score, class_interactivity_score, class_positivity_score
FROM class_status_scores
WHERE college_name = '求实职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND course_name = '语文' AND dt = '2019-07-16';

----------------------------------------
-- 0：开心
-- 1：正常
-- 2：低落
----------------------------------------
-- 学生情绪状态
SELECT
       action_status AS student_emotion, ROUND(rate * 100, 2) AS percentage
FROM class_status_student_daily
WHERE action_type = 3 AND college_name = '求实职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND course_name = '语文' AND dt = '2019-07-16';

-- 学生情绪状态趋势

SELECT
       dt, action_status AS student_emotion, ROUND(rate * 100, 2) AS percentage
FROM class_status_student_daily
WHERE action_type = 3 AND college_name = '求实职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND course_name = '语文' AND dt >= date_add('2019-07-16', interval -15 day) AND dt <= '2019-07-16'
ORDER BY dt ASC;


----------------------------------------
-- 0：非常好
-- 1：良好
-- 2：正常
-- 3: 不佳
----------------------------------------
-- 学生学习状态
SELECT
       action_status AS student_study_stat, ROUND(rate * 100, 2) AS percentage
FROM class_status_student_daily
WHERE action_type = 5 AND college_name = '求实职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND course_name = '语文' AND dt = '2019-07-16';

-- 学生学习状态趋势
SELECT
       dt, action_status AS student_study_stat, ROUND(rate * 100, 2) AS percentage
FROM class_status_student_daily
WHERE action_type = 5 AND college_name = '求实职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND course_name = '语文' AND dt >= date_add('2019-07-16', interval -15 day) AND dt <= '2019-07-16'
ORDER BY dt ASC;


----------------------------------------
-- 0：积极
-- 1：正常
-- 2：疲惫
----------------------------------------
-- 学生精神状态
SELECT
       action_status AS student_mental_stat, ROUND(rate * 100, 2) AS percentage
FROM class_status_student_daily
WHERE action_type = 4 AND college_name = '求实职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND course_name = '语文' AND dt = '2019-07-16';

-- 学生精神状态趋势
SELECT
       dt, action_status AS student_mental_stat, ROUND(rate * 100, 2) AS percentage
FROM class_status_student_daily
WHERE action_type = 4 AND college_name = '求实职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND course_name = '语文' AND dt >= date_add('2019-07-16', interval -15 day) AND dt <= '2019-07-16'
ORDER BY dt ASC;

----------------------------------------
-- 0：非常好
-- 1：良好
-- 2：正常
-- 3: 不佳
----------------------------------------
-- 课堂积极性
SELECT
    class_positivity
FROM class_status_daily
WHERE college_name = '求实职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND course_name = '语文' AND dt = '2019-07-16';

-- 课堂积极性趋势
SELECT
    dt, class_positivity
FROM class_status_daily
WHERE college_name = '求实职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND course_name = '语文' AND dt >= date_add('2019-07-16', interval -15 day) AND dt <= '2019-07-16'
ORDER BY dt ASC;

----------------------------------------
-- 0：高
-- 1：正常
-- 2：低
----------------------------------------
-- 课堂专注度
SELECT
    class_concentration
FROM class_status_daily
WHERE college_name = '求实职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND course_name = '语文' AND dt = '2019-07-16';

-- 课堂专注度趋势
SELECT
    dt, class_concentration
FROM class_status_daily
WHERE college_name = '求实职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND course_name = '语文' AND dt >= date_add('2019-07-16', interval -15 day) AND dt <= '2019-07-16'
ORDER BY dt ASC;


----------------------------------------
-- 0：高
-- 1：正常
-- 2：低
----------------------------------------
-- 课堂互动性
SELECT
    class_interactivity
FROM class_status_daily
WHERE college_name = '求实职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND course_name = '语文' AND dt = '2019-07-16';

-- 课堂互动性趋势
SELECT
    dt, class_interactivity
FROM class_status_daily
WHERE college_name = '求实职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND course_name = '语文' AND dt >= date_add('2019-07-16', interval -15 day) AND dt <= '2019-07-16'
ORDER BY dt ASC;


----------------------------------------
-- 课堂整体学习分析
SELECT
    dt, course_name, study_level, grade_level
FROM class_status_grade_study_daily
WHERE college_name = '求实职业学校' AND grade_name = '2017' AND class_name = '17动漫' AND course_name = '语文' AND dt >= '2019-07-16' AND dt <= date_add('2019-07-16', interval 60 day);

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
WHERE grade_name = '2017' AND class_name = '17动漫' AND course_name = '德育' AND dt = '2019-06-28';

-- 课堂积极性趋势
SELECT
    dt, class_positivity
FROM class_status_daily
WHERE grade_name = '2017' AND class_name = '17动漫' AND course_name = '德育' AND dt >= date_add('2019-06-28', interval -15 day) AND dt <= '2019-06-28'
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
WHERE grade_name = '2017' AND class_name = '17动漫' AND course_name = '德育' AND dt = '2019-06-28';

-- 课堂专注度趋势
SELECT
    dt, class_concentration
FROM class_status_daily
WHERE grade_name = '2017' AND class_name = '17动漫' AND course_name = '德育' AND dt >= date_add('2019-06-28', interval -15 day) AND dt <= '2019-06-28'
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
WHERE grade_name = '2017' AND class_name = '17动漫' AND course_name = '德育' AND dt = '2019-06-28';

-- 课堂互动性趋势
SELECT
    dt, class_interactivity
FROM class_status_daily
WHERE grade_name = '2017' AND class_name = '17动漫' AND course_name = '德育' AND dt >= date_add('2019-06-28', interval -15 day) AND dt <= '2019-06-28'
ORDER BY dt ASC;


----------------------------------------
-- 课堂整体学习分析
SELECT
    course_name, study_level, grade_level
FROM class_status_grade_study_daily
WHERE grade_name = '2017' AND class_name = '17动漫' AND course_name = '德育' AND dt >= '2019-06-28' AND dt <= date_add('2019-06-28', interval 30 day);
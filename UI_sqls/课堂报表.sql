-- 如果数据结果中，缺少的维度均显示为0.

----------------------------------------
-- 0：开心
-- 1：正常
-- 2：低落
----------------------------------------
-- 学生情绪状态
SELECT
       t1.student_emotion, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
FROM
(
	SELECT
		student_emotion, COUNT(*) AS num
    FROM student_mental_status_course_daily
    WHERE grade_name = '2019' AND class_name = '2班' AND course_id = '1' AND dt = '2019-09-29'
    GROUP BY student_emotion
) t1 JOIN
(
	SELECT
		COUNT(*) as total
	FROM student_mental_status_course_daily
	WHERE grade_name = '2019' AND class_name = '2班' AND course_id = '1' AND dt = '2019-09-29'
) t2;

-- 学生情绪状态趋势
SELECT
	t1.dt, t1.student_emotion, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
FROM
(
	SELECT
		dt, student_emotion, COUNT(*) AS num
    FROM student_mental_status_course_daily
    WHERE grade_name = '2019' AND class_name = '2班' AND course_id = '1' AND dt >= date_add('2019-09-29', interval -15 day) AND dt <= '2019-09-29'
    GROUP BY dt, student_emotion
) t1 JOIN
(
    SELECT
		dt, COUNT(*) AS total
    FROM student_mental_status_course_daily
	WHERE grade_name = '2019' AND class_name = '2班' AND course_id = '1' AND dt >= date_add('2019-09-29', interval -15 day) AND dt <= '2019-09-29'
    GROUP BY dt
) t2 ON t1.dt = t2.dt
ORDER BY dt ASC;


----------------------------------------
-- 0：非常好
-- 1：良好
-- 2：正常
-- 3: 不佳
----------------------------------------
-- 学生学习状态
SELECT
       t1.student_study_stat, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
FROM
(
	SELECT
		student_study_stat, COUNT(*) AS num
    FROM student_mental_status_course_daily
    WHERE grade_name = '2019' AND class_name = '2班' AND course_id = '1' AND dt = '2019-09-29'
    GROUP BY student_study_stat
) t1 JOIN
(
	SELECT
		COUNT(*) as total
	FROM student_mental_status_course_daily
	WHERE grade_name = '2019' AND class_name = '2班' AND course_id = '1' AND dt = '2019-09-29'
) t2;

-- 学生学习状态趋势
SELECT
	t1.dt, t1.student_study_stat, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
FROM
(
	SELECT
		dt, student_study_stat, COUNT(*) AS num
    FROM student_mental_status_course_daily
    WHERE grade_name = '2019' AND class_name = '2班' AND course_id = '1' AND dt >= date_add('2019-09-29', interval -15 day) AND dt <= '2019-09-29'
    GROUP BY dt, student_study_stat
) t1 JOIN
(
    SELECT
		dt, COUNT(*) AS total
    FROM student_mental_status_course_daily
	WHERE grade_name = '2019' AND class_name = '2班' AND course_id = '1' AND dt >= date_add('2019-09-29', interval -15 day) AND dt <= '2019-09-29'
    GROUP BY dt
) t2 ON t1.dt = t2.dt
ORDER BY dt ASC;

----------------------------------------
-- 0：开心
-- 1：正常
-- 2：低落
-- 3: 愤怒
----------------------------------------
-- 教师情绪状态
SELECT
	teacher_emotion
FROM teacher_status_course_daily
WHERE grade_name = '2019' AND class_name = '2班' AND course_id = '1' AND dt = '2019-09-29';

-- 教师情绪状态趋势
SELECT
	dt, teacher_emotion
FROM teacher_status_course_daily
WHERE grade_name = '2019' AND class_name = '2班' AND course_id = '1' AND dt >= date_add('2019-09-29', interval -15 day) AND dt <= '2019-09-29'
ORDER BY dt ASC;

----------------------------------------
-- 0：非常好
-- 1：良好
-- 2：正常
-- 3: 不佳
----------------------------------------
-- 教师教学态度
SELECT
	teacher_attitude
FROM teacher_status_course_daily
WHERE grade_name = '2019' AND class_name = '2班' AND course_id = '1' AND dt = '2019-09-29';

-- 教师教学态度趋势
SELECT
	dt, teacher_attitude
FROM teacher_status_course_daily
WHERE grade_name = '2019' AND class_name = '2班' AND course_id = '1' AND dt >= date_add('2019-09-29', interval -15 day) AND dt <= '2019-09-29'
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
WHERE grade_name = '2019' AND class_name = '2班' AND course_id = '1' AND dt = '2019-09-29';

-- 课堂积极性趋势
SELECT
	dt, class_positivity
FROM class_status_daily
WHERE grade_name = '2019' AND class_name = '2班' AND course_id = '1' AND dt >= date_add('2019-09-29', interval -15 day) AND dt <= '2019-09-29'
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
WHERE grade_name = '2019' AND class_name = '2班' AND course_id = '1' AND dt = '2019-09-29';

-- 课堂专注度趋势
SELECT
	dt, class_concentration
FROM class_status_daily
WHERE grade_name = '2019' AND class_name = '2班' AND course_id = '1' AND dt >= date_add('2019-09-29', interval -15 day) AND dt <= '2019-09-29'
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
WHERE grade_name = '2019' AND class_name = '2班' AND course_id = '1' AND dt = '2019-09-29';

-- 课堂互动性趋势
SELECT
	dt, class_interactivity
FROM class_status_daily
WHERE grade_name = '2019' AND class_name = '2班' AND course_id = '1' AND dt >= date_add('2019-09-29', interval -15 day) AND dt <= '2019-09-29'
ORDER BY dt ASC;


----------------------------------------
-- 课堂整体学习分析
SELECT
	course_name, study_level, grade_level
FROM class_status_grade_study_daily
WHERE grade_name = '2019' AND class_name = '2班' AND course_id = '1' AND dt >= '2019-09-29' AND dt <= date_add('2019-09-29', interval 30 day);
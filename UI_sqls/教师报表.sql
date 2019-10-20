-- 如果数据结果中，缺少的维度均显示为0.

----------------------------------------
-- 0：开心
-- 1：正常
-- 2：低落
-- 3：愤怒
----------------------------------------
-- 教师情绪状态
SELECT
       t1.teacher_emotion, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
FROM
(
	SELECT
		teacher_emotion, COUNT(*) AS num
    FROM teacher_status_daily
    WHERE teacher_number = '1' AND dt >= '2019-09-01' AND dt <= '2019-09-29'
    GROUP BY teacher_emotion
) t1 JOIN
(
	SELECT
		COUNT(*) as total
	FROM teacher_status_daily
	WHERE teacher_number = '1' AND dt >= '2019-09-01' AND dt <= '2019-09-29'
) t2;

-- 教师情绪状态趋势
SELECT
    dt, teacher_emotion
FROM teacher_status_daily
WHERE teacher_number = '1' AND dt >= '2019-09-01' AND dt <= '2019-09-29'
ORDER BY dt ASC;

----------------------------------------
-- 0：优秀
-- 1：良好
-- 2：正常
-- 3：不佳
----------------------------------------
-- 师德修养
SELECT
       t1.teacher_ethics, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
FROM
(
	SELECT
		teacher_ethics, COUNT(*) AS num
    FROM teacher_status_daily
    WHERE teacher_number = '1' AND dt >= '2019-09-01' AND dt <= '2019-09-29'
    GROUP BY teacher_ethics
) t1 JOIN
(
	SELECT
		COUNT(*) as total
	FROM teacher_status_daily
	WHERE teacher_number = '1' AND dt >= '2019-09-01' AND dt <= '2019-09-29'
) t2;

-- 师德修养趋势
SELECT
    dt, teacher_ethics
FROM teacher_status_daily
WHERE teacher_number = '1' AND dt >= '2019-09-01' AND dt <= '2019-09-29'
ORDER BY dt ASC;

----------------------------------------
-- 0：非常好
-- 1：良好
-- 2：正常
-- 3：不佳
----------------------------------------
-- 教师教学态度
SELECT
       t1.teacher_attitude, ROUND((1.0 * t1.num) / t2.total * 100, 2) AS percentage
FROM
(
	SELECT
		teacher_attitude, COUNT(*) AS num
    FROM teacher_status_daily
    WHERE teacher_number = '1' AND dt >= '2019-09-01' AND dt <= '2019-09-29'
    GROUP BY teacher_attitude
) t1 JOIN
(
	SELECT
		COUNT(*) as total
	FROM teacher_status_daily
	WHERE teacher_number = '1' AND dt >= '2019-09-01' AND dt <= '2019-09-29'
) t2;

-- 教师教学态度趋势
SELECT
    dt, teacher_attitude
FROM teacher_status_daily
WHERE teacher_number = '1' AND dt >= '2019-09-01' AND dt <= '2019-09-29'
ORDER BY dt ASC;
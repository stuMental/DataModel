-- 今日心理健康状态分布
	-- 情绪状态
	SELECT
		t1.student_emotion, ROUND(1.0 * t1.num / t2.total * 100, 2) AS percentage
	FROM
	(
		SELECT
			dt, student_emotion, COUNT(*) AS num
		FROM student_mental_status_ld
		WHERE dt = select_time_param
		GROUP BY dt, student_emotion
	) t1 JOIN
	(
		SELECT
			dt, COUNT(*) AS total
		FROM student_mental_status_ld
		WHERE dt = select_time_param
		GROUP BY dt
	) t2 ON t1.dt = t2.dt;
	
	-- 人际关系
	SELECT
		t1.student_relationship, ROUND(1.0 * t1.num / t2.total * 100, 2) AS percentage
	FROM
	(
		SELECT
			dt, student_relationship, COUNT(*) AS num
		FROM student_mental_status_ld
		WHERE dt = select_time_param
		GROUP BY dt, student_relationship
	) t1 JOIN
	(
		SELECT
			dt, COUNT(*) AS total
		FROM student_mental_status_ld
		WHERE dt = select_time_param
		GROUP BY dt
	) t2 ON t1.dt = t2.dt;
	
-- 今日学业自律性分布
	-- 学习状态
	SELECT
		t1.student_study_stat, ROUND(1.0 * t1.num / t2.total * 100, 2) AS percentage
	FROM
	(
		SELECT
			dt, student_study_stat, COUNT(*) AS num
		FROM student_mental_status_ld
		WHERE dt = select_time_param
		GROUP BY dt, student_study_stat
	) t1 JOIN
	(
		SELECT
			dt, COUNT(*) AS total
		FROM student_mental_status_ld
		WHERE dt = select_time_param
		GROUP BY dt
	) t2 ON t1.dt = t2.dt;
	
	-- 精神状态
	SELECT
		t1.student_mental_stat, ROUND(1.0 * t1.num / t2.total * 100, 2) AS percentage
	FROM
	(
		SELECT
			dt, student_mental_stat, COUNT(*) AS num
		FROM student_mental_status_ld
		WHERE dt = select_time_param
		GROUP BY dt, student_mental_stat
	) t1 JOIN
	(
		SELECT
			dt, COUNT(*) AS total
		FROM student_mental_status_ld
		WHERE dt = select_time_param
		GROUP BY dt
	) t2 ON t1.dt = t2.dt;
	
-- 学科兴趣分布
	SELECT
		student_interest, COUNT(*) AS total
	FROM student_mental_status_interest_daily
	WHERE dt = select_time_param
	GROUP BY student_interest
	ORDER BY student_interest ASC;
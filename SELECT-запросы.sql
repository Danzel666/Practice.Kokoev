-- 1. Вывести сеансы связи, в которых хотя бы один параметр вышел за пределы нормы.
SELECT DISTINCT 
    s.id AS session_id,
    s.coil AS coil,
    s.sassion_date,
    s.sassion_time,
    o.full_name AS operator_name,
    wt.name AS work_type,
    sc.name AS spacecraft_name,
    COUNT(DISTINCT pv.id) AS deviation_count
FROM session s
JOIN operator o ON s.operator_id = o.id
JOIN work_type wt ON s.work_type_id = wt.id
JOIN spacecraft sc ON s.spacecraft_id = sc.id
JOIN formular f ON s.id = f.session_id
JOIN parameter_value pv ON f.id = pv.formular_id
WHERE pv.status = 'Отклонение'
GROUP BY s.id, o.full_name, wt.name, sc.name
ORDER BY s.sassion_date DESC, s.sassion_time DESC;

-- 2. Найти операторов, которые работали больше 10 сеансов за последний месяц.
SELECT 
    o.id,
    o.full_name,
    COUNT(s.id) AS sessions_count,
    MIN(s.sassion_date) AS first_session_date,
    MAX(s.sassion_date) AS last_session_date
FROM operator o
JOIN session s ON o.id = s.operator_id
WHERE s.sassion_date >= CURRENT_DATE - INTERVAL '1 month'
GROUP BY o.id, o.full_name
HAVING COUNT(s.id) > 10
ORDER BY sessions_count DESC;

-- 3. Вывести блоки, у которых чаще всего встречались отклонения параметров за последний месяц.
SELECT 
    b.id,
    b.name AS block_name,
    COUNT(pv.id) AS total_parameters,
    SUM(CASE WHEN pv.status = 'Отклонение' THEN 1 ELSE 0 END) AS deviation_count,
    ROUND(
        SUM(CASE WHEN pv.status = 'Отклонение' THEN 1 ELSE 0 END) * 100.0 / 
        NULLIF(COUNT(pv.id), 0), 2
    ) AS deviation_percentage
FROM block b
JOIN formular f ON b.id = f.block_id
JOIN parameter_value pv ON f.id = pv.formular_id
JOIN session s ON f.session_id = s.id
WHERE s.sassion_date >= CURRENT_DATE - INTERVAL '1 month'
GROUP BY b.id, b.name
HAVING COUNT(pv.id) > 0
ORDER BY deviation_count DESC
LIMIT 10;

-- 4. Подсчитать количество сеансов по каждому типу работы за последний квартал, отсортировать по убыванию
SELECT 
    wt.id,
    wt.name AS work_type_name,
    COUNT(s.id) AS sessions_count,
    MIN(s.sassion_date) AS first_session,
    MAX(s.sassion_date) AS last_session
FROM work_type wt
JOIN session s ON wt.id = s.work_type_id
WHERE s.sassion_date >= CURRENT_DATE - INTERVAL '3 months'
GROUP BY wt.id, wt.name
ORDER BY sessions_count DESC;

-- 5. Найти сеансы, где все параметры были в норме, и вывести дату, оператора и тип работы.
SELECT 
    s.id AS session_id,
    s.coil AS coil,
    s.sassion_date,
    s.sassion_time,
    o.full_name AS operator_name,
    wt.name AS work_type,
    sc.name AS spacecraft_name,
    COUNT(pv.id) AS total_parameters
FROM session s
JOIN operator o ON s.operator_id = o.id
JOIN work_type wt ON s.work_type_id = wt.id
JOIN spacecraft sc ON s.spacecraft_id = sc.id
JOIN formular f ON s.id = f.session_id
JOIN parameter_value pv ON f.id = pv.formular_id
GROUP BY s.id, o.full_name, wt.name, sc.name
HAVING COUNT(pv.id) > 0 
   AND SUM(CASE WHEN pv.status = 'Отклонение' THEN 1 ELSE 0 END) = 0
ORDER BY s.sassion_date DESC, s.sassion_time DESC;
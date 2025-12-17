-- 1. Процедура получения списка сеансов и формуляров с отклонениями за указанный период
CREATE OR REPLACE PROCEDURE get_sessions_with_deviations(
    start_date DATE,
    end_date DATE
)
LANGUAGE plpgsql AS $$
BEGIN
    CREATE TEMP TABLE IF NOT EXISTS temp_results AS
    SELECT 
        s.id AS session_id,
        s.sassion_date,
        s.sassion_time,
        o.full_name AS operator,
        f.name AS formular_name,
        COUNT(pv.id) AS deviation_count
    FROM session s
    JOIN operator o ON s.operator_id = o.id
    JOIN formular f ON s.id = f.session_id
    JOIN parameter_value pv ON f.id = pv.formular_id
    WHERE s.sassion_date BETWEEN start_date AND end_date
      AND pv.status = 'отклонение'
    GROUP BY s.id, s.sassion_date, s.sassion_time, o.full_name, f.name
    ORDER BY s.sassion_date DESC, s.sassion_time DESC;
    
    SELECT * FROM temp_results;
    DROP TABLE temp_results;
END;
$$;

-- 2. Процедура анализа сеанса: подсчёт процента параметров в норме и вывод итогового статуса
CREATE OR REPLACE PROCEDURE analyze_session(
    session_id INTEGER
)
LANGUAGE plpgsql AS $$
DECLARE
    total_params INTEGER;
    normal_params INTEGER;
    normal_percent DECIMAL(5,2);
    session_status VARCHAR(20);
BEGIN

    SELECT COUNT(*) INTO total_params
    FROM parameter_value pv
    JOIN formular f ON pv.formular_id = f.id
    WHERE f.session_id = analyze_session.session_id;
 
    SELECT COUNT(*) INTO normal_params
    FROM parameter_value pv
    JOIN formular f ON pv.formular_id = f.id
    WHERE f.session_id = analyze_session.session_id
      AND pv.status = 'норма';

    IF total_params > 0 THEN
        normal_percent := (normal_params::DECIMAL / total_params::DECIMAL) * 100;
    ELSE
        normal_percent := 0;
    END IF;
  
    IF normal_percent >= 95 THEN
        session_status := 'отлично';
    ELSIF normal_percent >= 80 THEN
        session_status := 'хорошо';
    ELSIF normal_percent >= 60 THEN
        session_status := 'удовлетворительно';
    ELSE
        session_status := 'требует внимания';
    END IF;
    
    RAISE NOTICE 'Сеанс ID: %, Всего параметров: %, В норме: %, Процент нормы: %%, Статус: %',
                 session_id, total_params, normal_params, normal_percent, session_status;
END;
$$;

-- 3. Процедура поиска аномалий: вывести все параметры, отклоняющиеся от нормы более чем на 20%
CREATE OR REPLACE PROCEDURE find_anomalies(
    start_date DATE DEFAULT NULL,
    end_date DATE DEFAULT NULL,
    target_session_id INTEGER DEFAULT NULL
)
LANGUAGE plpgsql AS $$
BEGIN
    CREATE TEMP TABLE IF NOT EXISTS temp_anomalies AS
    SELECT 
        s.id AS session_id,
        s.sassion_date,
        p.name AS parameter_name,
        pv.value,
        p.min_value,
        p.max_value,
        pv.status,
        CASE 
            WHEN pv.value < p.min_value THEN 
                ROUND(((p.min_value - pv.value)::DECIMAL / p.min_value) * 100, 2)
            WHEN pv.value > p.max_value THEN 
                ROUND(((pv.value - p.max_value)::DECIMAL / p.max_value) * 100, 2)
            ELSE 0
        END AS deviation_percent
    FROM session s
    JOIN formular f ON s.id = f.session_id
    JOIN parameter_value pv ON f.id = pv.formular_id
    JOIN parameter p ON pv.parameter_id = p.id
    WHERE pv.status = 'отклонение'
      AND (
        (start_date IS NULL OR s.sassion_date >= start_date) AND
        (end_date IS NULL OR s.sassion_date <= end_date) AND
        (target_session_id IS NULL OR s.id = target_session_id)
      )
      AND (
        (pv.value < p.min_value AND (p.min_value - pv.value)::DECIMAL / p.min_value > 0.2) OR
        (pv.value > p.max_value AND (pv.value - p.max_value)::DECIMAL / p.max_value > 0.2)
      )
    ORDER BY deviation_percent DESC;
    
    SELECT * FROM temp_anomalies;
    DROP TABLE temp_anomalies;
END;
$$;
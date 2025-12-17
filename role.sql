-- 1. Роль telemetry_operator — только INSERT в таблицы сеансов и параметров
CREATE ROLE telemetry_operator;
GRANT INSERT ON session, parameter_value TO telemetry_operator;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA "Архивация телеметрии" TO telemetry_operator;

-- 2. Роль analyst — SELECT, UPDATE (статуса анализа), но без удаления
CREATE ROLE analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA "Архивация телеметрии" TO analyst;
GRANT UPDATE(status) ON parameter_value TO analyst;
GRANT EXECUTE ON PROCEDURE get_sessions_with_deviations, analyze_session, find_anomalies TO analyst;

-- 3. Роль archive_admin — полные права на все таблицы, кроме удаления записей старше года
CREATE ROLE archive_admin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA "Архивация телеметрии" TO archive_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA "Архивация телеметрии" TO archive_admin;

-- Ограничение для archive_admin: нельзя удалять записи старше года
CREATE OR REPLACE FUNCTION prevent_old_data_deletion()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.sassion_date < CURRENT_DATE - INTERVAL '1 year' THEN
        RAISE EXCEPTION 'Нельзя удалять записи старше одного года';
    END IF;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_old_deletion
BEFORE DELETE ON session
FOR EACH ROW
EXECUTE FUNCTION prevent_old_data_deletion();
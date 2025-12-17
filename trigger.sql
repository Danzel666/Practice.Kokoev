-- 1. Триггер на добавление параметра: автоматически вычислять статус «норма/отклонение» на основе допустимых значений
CREATE OR REPLACE FUNCTION calculate_parameter_status()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.value >= (SELECT min_value FROM parameter WHERE id = NEW.parameter_id) 
       AND NEW.value <= (SELECT max_value FROM parameter WHERE id = NEW.parameter_id) THEN
        NEW.status := 'норма';
    ELSE
        NEW.status := 'отклонение';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_parameter_status
BEFORE INSERT OR UPDATE ON parameter_value
FOR EACH ROW
EXECUTE FUNCTION calculate_parameter_status();

-- 2. Триггер на удаление сеанса: удалять все связанные параметры и блоки (каскадное удаление)
CREATE OR REPLACE FUNCTION delete_session_cascade()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM formular WHERE session_id = OLD.id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_delete_session
BEFORE DELETE ON session
FOR EACH ROW
EXECUTE FUNCTION delete_session_cascade();

-- 3. Триггер на добавление нового блока: автоматически создавать набор параметров по умолчанию для этого типа блока
CREATE OR REPLACE FUNCTION create_default_parameters_for_block()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO parameter (name, measurement, min_value, max_value) 
    VALUES ('Температура', '°C', 20, 80),
           ('Напряжение', 'В', 12, 24);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_new_block
AFTER INSERT ON block
FOR EACH ROW
EXECUTE FUNCTION create_default_parameters_for_block();
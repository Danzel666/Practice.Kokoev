-- 1. Таблица Gender (Пол)
CREATE TABLE gender (
    id SERIAL PRIMARY KEY,
    name VARCHAR(10) NOT NULL
);

-- 2. Таблица Work_type (Тип работы)
CREATE TABLE work_type (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) NOT NULL
);

-- 3. Таблица Spacecraft (Космический аппарат)
CREATE TABLE spacecraft (
    id SERIAL PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    assembly_location VARCHAR(50)
);

-- 4. Таблица Operator (Оператор)
CREATE TABLE operator (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(50) NOT NULL,
    gender_id INTEGER NOT NULL REFERENCES gender(id),
    phone VARCHAR(15),
    birth_date DATE,
    login VARCHAR(20) NOT NULL
);

-- 5. Таблица Block (Блок аппаратуры)
CREATE TABLE block (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- 6. Таблица Parameter (Параметр)
CREATE TABLE parameter (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    measurement VARCHAR(5) NOT NULL,
    acceptable_value REAL NOT NULL
);

-- 7. Таблица Formular (Формуляр)
CREATE TABLE formular (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    block_id INTEGER NOT NULL REFERENCES block(id)
);

-- 8. Таблица Session (Сеанс связи)
CREATE TABLE session (
    id SERIAL PRIMARY KEY,
    operator_id INTEGER NOT NULL REFERENCES operator(id),
    work_type_id INTEGER NOT NULL REFERENCES work_type(id),
    spacecraft_id INTEGER NOT NULL REFERENCES spacecraft(id),
    formular_id INTEGER NOT NULL REFERENCES formular(id),
    code INTEGER NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL
);

-- 9. Таблица Parameter_value (Значение параметра)
CREATE TABLE parameter_value (
    id SERIAL PRIMARY KEY,
    parameter_id INTEGER NOT NULL REFERENCES parameter(id),
    formular_id INTEGER NOT NULL REFERENCES formular(id),
    value REAL NOT NULL,
    status VARCHAR(15) NOT NULL
);
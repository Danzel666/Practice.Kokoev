-- 1. Таблица gender
CREATE TABLE gender (
    id SERIAL PRIMARY KEY,
    name VARCHAR(10) NOT NULL
);

-- 2. Таблица work_type
CREATE TABLE work_type (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) NOT NULL
);

-- 3. Таблица spacecraft
CREATE TABLE spacecraft (
    id SERIAL PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    assembly_location VARCHAR(50)
);

-- 4. Таблица operator
CREATE TABLE operator (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(50) NOT NULL,
    gender_id INTEGER NOT NULL REFERENCES gender(id),
    phone VARCHAR(15),
    birth_date DATE,
    login VARCHAR(20) NOT NULL
);

-- 5. Таблица block
CREATE TABLE block (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

-- 6. Таблица session
CREATE TABLE session (
    id SERIAL PRIMARY KEY,
    operator_id INTEGER NOT NULL REFERENCES operator(id),
    work_type_id INTEGER NOT NULL REFERENCES work_type(id),
    spacecraft_id INTEGER NOT NULL REFERENCES spacecraft(id),
    coil INTEGER NOT NULL,
    sassion_date DATE NOT NULL,
    sassion_time TIME NOT NULL
);

-- 7. Таблица formular
CREATE TABLE formular (
    id SERIAL PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    block_id INTEGER NOT NULL REFERENCES block(id),
    session_id INTEGER REFERENCES session(id)
);

-- 8. Таблица parameter
CREATE TABLE parameter (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    measurement VARCHAR(5) NOT NULL,
    min_value INTEGER,
    max_value INTEGER
);

-- 9. Таблица parameter_value
CREATE TABLE parameter_value (
    id SERIAL PRIMARY KEY,
    parameter_id INTEGER NOT NULL REFERENCES parameter(id),
    formular_id INTEGER NOT NULL REFERENCES formular(id),
    value REAL NOT NULL,
    status VARCHAR(15) NOT NULL
);
-- ==========================================
-- Phase 1: PostgreSQL Fundamentals
-- Topic: Constraints
-- File: 04-constraints.sql
-- ==========================================


-- ==========================================
-- NOT NULL
-- ==========================================

CREATE TABLE employees (
    employee_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    age INT
);


-- This works
INSERT INTO employees (first_name, last_name, email, age)
VALUES ('Rahul', 'Sharma', 'rahul@company.com', 25);


-- This will fail because first_name is NOT NULL
-- INSERT INTO employees (last_name, email, age)
-- VALUES ('Verma', 'priya@company.com', 24);


-- ==========================================
-- UNIQUE
-- ==========================================

ALTER TABLE employees
ADD CONSTRAINT unique_employee_email UNIQUE (email);


-- First employee
INSERT INTO employees (first_name, last_name, email, age)
VALUES ('Priya', 'Verma', 'priya@company.com', 24);


-- This will fail because email must be unique
-- INSERT INTO employees (first_name, last_name, email, age)
-- VALUES ('Aman', 'Singh', 'priya@company.com', 26);


-- ==========================================
-- CHECK
-- ==========================================

ALTER TABLE employees
ADD CONSTRAINT check_employee_age
CHECK (age >= 18);


-- This works
INSERT INTO employees (first_name, last_name, email, age)
VALUES ('Neha', 'Gupta', 'neha@company.com', 22);


-- This will fail because age is less than 18
-- INSERT INTO employees (first_name, last_name, email, age)
-- VALUES ('Ravi', 'Kumar', 'ravi@company.com', 16);


-- ==========================================
-- DEFAULT
-- ==========================================

ALTER TABLE employees
ADD COLUMN department VARCHAR(50) DEFAULT 'General';


-- Insert employee without department
INSERT INTO employees (first_name, last_name, email, age)
VALUES ('Amit', 'Singh', 'amit@company.com', 28);


-- PostgreSQL automatically assigns:
-- department = 'General'


-- ==========================================
-- PRIMARY KEY
-- ==========================================

-- employee_id is already defined as:
-- employee_id SERIAL PRIMARY KEY

-- Therefore every employee gets a unique ID.


-- ==========================================
-- VIEW FINAL DATA
-- ==========================================

SELECT *
FROM employees;
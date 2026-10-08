-- ==========================================
-- Phase 1: PostgreSQL Fundamentals
-- Topic: CRUD Operations
-- File: 03-crud.sql
-- ==========================================


-- ==========================================
-- CREATE
-- Insert records into students table
-- ==========================================

INSERT INTO students (first_name, last_name, age, email)
VALUES
('Rahul', 'Sharma', 21, 'rahul@example.com'),
('Priya', 'Verma', 22, 'priya@example.com'),
('Aman', 'Singh', 20, 'aman@example.com'),
('Neha', 'Gupta', 23, 'neha@example.com');


-- ==========================================
-- READ
-- Retrieve all students
-- ==========================================

SELECT *
FROM students;


-- Retrieve specific columns
SELECT
    student_id,
    first_name,
    age
FROM students;


-- Retrieve students older than 21
SELECT *
FROM students
WHERE age > 21;


-- ==========================================
-- UPDATE
-- Update Aman Singh's age
-- ==========================================

UPDATE students
SET age = 21
WHERE first_name = 'Aman'
  AND last_name = 'Singh';


-- Verify the update
SELECT *
FROM students
WHERE first_name = 'Aman'
  AND last_name = 'Singh';


-- ==========================================
-- DELETE
-- Delete Aman Singh
-- ==========================================

DELETE FROM students
WHERE first_name = 'Aman'
  AND last_name = 'Singh';


-- Verify the deletion
SELECT *
FROM students;
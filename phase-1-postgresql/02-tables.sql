-- ==========================================
-- Phase 1: PostgreSQL Fundamentals
-- Topic: Tables
-- File: 02-tables.sql
-- ==========================================


-- Create students table
CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    age INT,
    email VARCHAR(100)
);
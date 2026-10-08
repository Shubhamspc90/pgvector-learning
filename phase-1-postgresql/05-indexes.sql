-- ==========================================
-- Phase 1: PostgreSQL Fundamentals
-- Topic: Indexes
-- File: 05-indexes.sql
-- ==========================================


-- ==========================================
-- Create a practice table
-- ==========================================

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    price DECIMAL(10, 2)
);


-- ==========================================
-- Insert sample data
-- ==========================================

INSERT INTO products (product_name, category, price)
VALUES
('Laptop', 'Electronics', 65000.00),
('Mouse', 'Electronics', 1200.00),
('Keyboard', 'Electronics', 2500.00),
('Chair', 'Furniture', 8500.00),
('Desk', 'Furniture', 15000.00),
('Monitor', 'Electronics', 18000.00),
('Headphones', 'Electronics', 3500.00),
('Notebook', 'Stationery', 100.00);


-- ==========================================
-- Create an index on category
-- ==========================================

CREATE INDEX idx_products_category
ON products(category);


-- ==========================================
-- Create an index on price
-- ==========================================

CREATE INDEX idx_products_price
ON products(price);


-- ==========================================
-- Search using indexed column
-- ==========================================

SELECT *
FROM products
WHERE category = 'Electronics';


-- Search using another indexed column

SELECT *
FROM products
WHERE price > 5000;


-- ==========================================
-- View indexes
-- ==========================================

SELECT
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'products';

-- EXPLAIN ANALYZE actually executes the query and reports execution information.
EXPLAIN ANALYZE
SELECT *
FROM products
WHERE category = 'Electronics';
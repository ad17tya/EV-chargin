-- schema.sql - Database schema for EV Charging System

-- Drop tables if they exist
DROP TABLE IF EXISTS bills;
DROP TABLE IF EXISTS usage_logs;
DROP TABLE IF EXISTS default_settings;
DROP TABLE IF EXISTS users;

-- Create users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    is_blocked INTEGER DEFAULT 0 -- 0 for false, 1 for true
);

-- Create default_settings table for monthly default km
CREATE TABLE default_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    default_km REAL NOT NULL,
    set_date DATE NOT NULL,
    valid_until DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create usage_logs table
CREATE TABLE usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    default_km REAL NOT NULL,
    extra_km REAL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Create bills table
CREATE TABLE bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    total_amount REAL NOT NULL,
    is_paid INTEGER DEFAULT 0, -- 0 for false, 1 for true
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Insert sample data
-- Default passwords are plain text as specified
INSERT INTO users (username, password, role, is_blocked) VALUES 
('user1', 'password1', 'vehicle_owner', 0),
('user2', 'password2', 'vehicle_owner', 0),
('admin', 'adminpass', 'management', 0);

-- Insert sample default settings (valid for 30 days from April 1, 2025)
INSERT INTO default_settings (user_id, default_km, set_date, valid_until) VALUES
(1, 25.0, '2025-04-01', '2025-05-01'),
(2, 15.0, '2025-04-01', '2025-05-01');

-- Insert sample usage logs
INSERT INTO usage_logs (user_id, date, default_km, extra_km) VALUES
(1, '2025-04-10', 25.0, 2.0),
(1, '2025-04-11', 25.0, 0.0),
(1, '2025-04-12', 25.0, 5.0),
(2, '2025-04-10', 15.0, 3.5),
(2, '2025-04-11', 15.0, 0.0);

-- Insert sample bills
INSERT INTO bills (user_id, month, total_amount, is_paid) VALUES
(1, '2025-01', 145.50, 1),
(1, '2025-02', 168.75, 1),
(1, '2025-03', 198.20, 0),
(2, '2025-01', 99.80, 1),
(2, '2025-02', 120.40, 0),
(2, '2025-03', 110.60, 0);
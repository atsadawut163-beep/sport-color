-- MySQL Raw SQL Script for Sport Color Dashboard System
-- Use this script to set up the database tables manually if desired.
-- SQLAlchemy will also attempt to create these tables automatically upon starting the backend.

CREATE DATABASE IF NOT EXISTS sport_color_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sport_color_db;

-- 1. Users table (for admin authentication)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Sports Events table (e.g., Football, Basketball, etc.)
CREATE TABLE IF NOT EXISTS sports_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL, -- e.g., 'Indoor', 'Outdoor', 'Track'
    status VARCHAR(50) DEFAULT 'scheduled', -- e.g., 'scheduled', 'ongoing', 'completed'
    schedule_time DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 3. Participants table (Athletes & Staff)
CREATE TABLE IF NOT EXISTS participants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL, -- 'student' or 'staff'
    color_team VARCHAR(50) NOT NULL, -- e.g., 'Red', 'Blue', 'Green', 'Yellow'
    sport_event_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sport_event_id) REFERENCES sports_events(id) ON DELETE SET NULL
) ENGINE=InnoDB;

-- 4. Transactions table (Finance)
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type VARCHAR(20) NOT NULL, -- 'income' or 'expense'
    category VARCHAR(50) NOT NULL, -- e.g., 'Equipment', 'Food', 'Uniform', 'Registration', 'Prizes', 'Donation'
    amount DECIMAL(10, 2) NOT NULL,
    description VARCHAR(255),
    date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 5. Results table (Match outcomes)
CREATE TABLE IF NOT EXISTS results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sport_event_id INT NOT NULL UNIQUE, -- One result per event
    winner VARCHAR(100) NOT NULL, -- Team or Participant name
    runner_up VARCHAR(100),
    second_runner_up VARCHAR(100),
    score VARCHAR(50), -- e.g., '3-2', '95-90'
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sport_event_id) REFERENCES sports_events(id) ON DELETE CASCADE
) ENGINE=InnoDB;

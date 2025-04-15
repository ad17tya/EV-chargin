CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL,
    is_blocked INTEGER DEFAULT 0
);

CREATE TABLE usage_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    date TEXT,
    default_km INTEGER,
    extra_km INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

INSERT INTO users (username, password, role) VALUES ('alice', 'pass123', 'vehicle_owner');
INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'management');

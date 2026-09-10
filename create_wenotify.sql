CREATE TABLE IF NOT EXISTS wenotify (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    user_id INT,
    email VARCHAR(150),
    phone VARCHAR(20),
    event_desc TEXT,
    file_upload VARCHAR(255),
    event_date DATE,
    county VARCHAR(100),
    location VARCHAR(255),
    contact_on VARCHAR(100),
    gender VARCHAR(20),
    status VARCHAR(20) NOT NULL DEFAULT 'Pending'
);

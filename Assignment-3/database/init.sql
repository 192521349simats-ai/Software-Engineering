
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS facilities (
    facility_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(150) NOT NULL,
    capacity INTEGER NOT NULL,
    category VARCHAR(50) NOT NULL,
    status VARCHAR(30) DEFAULT 'Available'
);

CREATE TABLE IF NOT EXISTS bookings (
    booking_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    facility_id INTEGER REFERENCES facilities(facility_id),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    purpose TEXT NOT NULL,
    status VARCHAR(30) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS maintenance_tickets (
    ticket_id SERIAL PRIMARY KEY,
    facility_id INTEGER REFERENCES facilities(facility_id),
    reported_by INTEGER REFERENCES users(user_id),
    assigned_to INTEGER REFERENCES users(user_id),
    issue TEXT NOT NULL,
    priority VARCHAR(20) DEFAULT 'Medium',
    status VARCHAR(30) DEFAULT 'Open',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (name, email, password, role) VALUES
('Campus Administrator', 'admin@campus.com', 'admin123', 'Administrator'),
('Facility Manager', 'manager@campus.com', 'manager123', 'Facility Manager'),
('Maintenance Technician', 'tech@campus.com', 'tech123', 'Technician'),
('Department Approver', 'approver@campus.com', 'approve123', 'Department Approver'),
('Faculty Member', 'faculty@campus.com', 'faculty123', 'Faculty'),
('Campus Student', 'student@campus.com', 'student123', 'Student')
ON CONFLICT (email) DO NOTHING;

INSERT INTO facilities (name, location, capacity, category, status) VALUES
('Innovation Hub', 'Block A - First Floor', 60, 'Collaboration', 'Available'),
('Smart Lecture Hall', 'Block B - Ground Floor', 120, 'Classroom', 'Available'),
('Computer Lab 01', 'Block C - Second Floor', 45, 'Laboratory', 'Available'),
('Research Studio', 'Block D - First Floor', 30, 'Research', 'Available'),
('Conference Suite', 'Admin Block - Third Floor', 20, 'Meeting', 'Available'),
('Auditorium', 'Main Campus - Central Wing', 300, 'Event Space', 'Available')
ON CONFLICT DO NOTHING;

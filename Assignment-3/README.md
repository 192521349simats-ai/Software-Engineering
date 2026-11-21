
# CampusFlow – Smart Campus Facility Booking & Maintenance

CampusFlow is a full-stack Smart Campus Facility Booking and Maintenance Management System designed to simplify campus operations.

## Features

- Role-based login
- Facility catalogue
- Facility booking requests
- Booking approval and rejection
- Maintenance issue reporting
- Technician assignment
- Ticket resolution
- Dashboard statistics
- PostgreSQL data storage
- Docker Compose deployment

## Technology Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Python Flask
- Database: PostgreSQL
- Containerization: Docker
- Version Control: Git and GitHub

## Project Structure

- app/: Flask application
- app/templates/: HTML templates
- app/static/: CSS and JavaScript
- database/: database initialization scripts
- tests/: test files
- Dockerfile: application container
- compose.yaml: multi-container configuration

## Demo Accounts

| Role | Email | Password |
|---|---|---|
| Administrator | admin@campus.com | admin123 |
| Facility Manager | manager@campus.com | manager123 |
| Technician | tech@campus.com | tech123 |
| Department Approver | approver@campus.com | approve123 |
| Faculty | faculty@campus.com | faculty123 |
| Student | student@campus.com | student123 |

## Deployment

Build containers:

    docker compose build

Start services:

    docker compose up -d

Check services:

    docker compose ps

Open the application:

    http://localhost:5000

View logs:

    docker compose logs

Stop services:

    docker compose down

The PostgreSQL database uses a persistent Docker volume.

\# Smart Campus Facility \& Maintenance Platform — Assignment 4



\## Project Overview

A Smart Campus Facility \& Maintenance Platform designed to manage facility bookings, sensor monitoring, maintenance tickets, and Service Level Agreement (SLA) tracking.



\## Features

\- Facility booking with time validation and conflict detection

\- Booking cancellation with role-based authorization

\- Sensor monitoring with threshold-based alerts

\- Maintenance ticket creation and status management

\- SLA tracking for unresolved tickets

\- Automated unit, integration, and regression testing

\- Docker containerization

\- GitHub Actions CI pipeline



\## Technology Stack

\- Python 3.14

\- Flask

\- SQLite

\- Pytest

\- Docker

\- GitHub Actions



\## Project Structure

```text

Assignment-4/

├── backend/

├── tests/

├── scripts/

├── Dockerfile

└── .gitignore

```



\## Testing

The automated test suite contains 14 tests covering booking validation, sensor threshold checks, ticket management, authorization, and regression scenarios.



\## CI Pipeline

The GitHub Actions workflow automatically installs dependencies, runs automated tests, and builds the Docker image.



\## Run Locally

```bash

cd backend

pip install -r requirements.txt

python app.py

```



\## Run Tests

```bash

python -m pytest -v tests

```



\## Docker Build

```bash

docker build -t smart-campus-app:1.0 .

```



\## Scope \& Limitations

Authentication is simulated through role headers. External calendar integration, production authentication, database migration automation, and advanced security/load validation are not fully implemented.



\## Academic Project

Software Engineering — CO4 Assignment 4: Create and Validate Testing and DevOps Pipeline for Smart Campus Facility Platform.


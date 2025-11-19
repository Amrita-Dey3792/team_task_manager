# Team Task Manager

A Django REST Framework application for managing teams and tasks within companies.

## Features

- User authentication with JWT
- Company management
- Team management
- Task management with assignments
- RESTful API with filtering and pagination
- API documentation with Swagger/OpenAPI

## Prerequisites

- Python 3.8+
- pip

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd team_task_manager
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv env
   env\Scripts\activate

   # Linux/Mac
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/`

## API Documentation

Once the server is running, access the interactive API documentation at:
- Swagger UI: `http://127.0.0.1:8000/swagger/`
- ReDoc: `http://127.0.0.1:8000/redoc/`

## Authentication

The API uses JWT (JSON Web Token) authentication. To authenticate:

1. Obtain tokens by making a POST request to the login endpoint
2. Include the access token in the Authorization header: `Bearer <access_token>`

## Project Structure

- `users/` - User management
- `companies/` - Company management
- `teams/` - Team management
- `tasks/` - Task management


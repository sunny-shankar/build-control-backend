# Build Control Backend

A FastAPI-based backend API for Build Control, a construction management platform. This backend provides authentication, user management, and project management capabilities.

## Features

- 🔐 **User Authentication**
  - Email/password login
  - Mobile OTP-based login
  - JWT token-based authentication
  - Secure password hashing with bcrypt

- 👥 **User Management**
  - User registration with company details
  - User profile management
  - Email and mobile number validation

- 📁 **Project Management**
  - Create, read, and manage projects
  - Project types: Residential, Commercial, Others
  - Project statuses: Not Started, Ongoing, On Hold, Completed
  - User-specific project access (users can only view their own projects)

- 🔒 **Security**
  - JWT-based authentication
  - Password hashing
  - CORS configuration
  - Input validation with Pydantic

- 📊 **Database**
  - PostgreSQL database
  - SQLModel ORM
  - Alembic migrations
  - Soft delete support
  - UUID primary keys

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLModel
- **Migrations**: Alembic
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Validation**: Pydantic
- **Package Manager**: uv

## Prerequisites

- Python >= 3.13
- PostgreSQL database
- uv (Python package manager)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd buildcontrol-backend
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment variables**

   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
   ENVIRONMENT=development
   CORS_ORIGINS=["http://localhost:3000"]
   CORS_HEADERS=["*"]
   JWT_SECRET_KEY=your-secret-key-here
   JWT_ALGORITHM=HS256
   JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
   OTP_LENGTH=6
   OTP_EXPIRE_MINUTES=10
   OTP_MAX_ATTEMPTS=3
   ```

4. **Run database migrations**
   ```bash
   uv run alembic upgrade head
   ```

## Running the Application

### Development Mode
```bash
fab dev
```
or
```bash
uv run fastapi dev
```

The API will be available at `http://localhost:8000`

### Production Mode
```bash
fab start
```
or
```bash
uv run fastapi run
```

### Using Fabric Tasks

The project includes Fabric tasks for common operations:

- `fab dev` - Run in development mode
- `fab start` - Run in production mode
- `fab commit` - Run commitizen for conventional commits
- `fab db_revision` - Generate a new database migration
- `fab db_upgrade` - Apply all database migrations

## API Documentation

Once the server is running, you can access:

- **Interactive API Docs (Swagger UI)**: `http://localhost:8000/docs`
- **Alternative API Docs (ReDoc)**: `http://localhost:8000/redoc`

```
buildcontrol-backend/
├── app/
│   ├── common/           # Shared utilities and base classes
│   │   ├── auth.py      # Authentication dependencies
│   │   ├── constants.py # Application constants
│   │   ├── exceptions.py # Exception handlers
│   │   ├── models.py     # Base SQLModel classes
│   │   ├── repository.py # Base repository pattern
│   │   └── schemas.py    # Base Pydantic schemas
│   ├── communication/    # Communication services (SMS, etc.)
│   ├── core/            # Core configuration
│   ├── db/              # Database session management
│   ├── otp/             # OTP management
│   ├── projects/        # Project management module
│   ├── router/          # API route definitions
│   ├── users/           # User management module
│   ├── utils/           # Utility functions
│   └── main.py          # FastAPI application entry point
├── migrations/          # Alembic database migrations
├── alembic.ini         # Alembic configuration
├── pyproject.toml      # Project dependencies and configuration
└── README.md           # This file
```

## Database Migrations

### Create a new migration
```bash
uv run alembic revision --autogenerate -m "migration message"
```

### Apply migrations
```bash
uv run alembic upgrade head
```

### Rollback migrations
```bash
uv run alembic downgrade -1
```

## Development

### Code Style

The project uses:
- **Ruff** for linting and formatting
- **Pre-commit hooks** for code quality checks
- **Commitizen** for conventional commits

### Pre-commit Hooks

Install pre-commit hooks:
```bash
uv run pre-commit install
```

### Making Commits

Use commitizen for conventional commits:
```bash
fab commit
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `ENVIRONMENT` | Application environment (development/staging/production) | development |
| `CORS_ORIGINS` | Allowed CORS origins | ["*"] |
| `CORS_HEADERS` | Allowed CORS headers | ["*"] |
| `JWT_SECRET_KEY` | Secret key for JWT tokens | Auto-generated |
| `JWT_ALGORITHM` | JWT algorithm | HS256 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration time | 30 |
| `OTP_LENGTH` | OTP code length | 6 |
| `OTP_EXPIRE_MINUTES` | OTP expiration time | 10 |
| `OTP_MAX_ATTEMPTS` | Maximum OTP verification attempts | 3 |

## Error Handling

The API uses a consistent error response format:
```json
{
  "success": false,
  "message": "Error message",
  "timestamp": "2025-12-10T00:00:00Z",
  "data": null
}
```

Common HTTP status codes:
- `200` - Success
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `500` - Internal Server Error

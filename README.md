# Organization Management Service

A multi-tenant organization management system built with FastAPI and MongoDB that supports creating and managing organizations with dynamic collection creation.

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Setup Instructions](#setup-instructions)
- [API Documentation](#api-documentation)
- [Environment Variables](#environment-variables)
- [Design Decisions](#design-decisions)
- [Scalability Considerations](#scalability-considerations)

## Features

- **Organization Management**: Create, read, update, and delete organizations
- **Dynamic Collection Creation**: Each organization gets its own MongoDB collection
- **Admin Authentication**: JWT-based authentication for admin users
- **Multi-tenant Architecture**: Isolated data storage per organization
- **Input Validation**: Email, password strength, and organization name validation
- **Security**: Password hashing with bcrypt, SQL injection prevention
- **Error Handling**: Custom exceptions with proper HTTP status codes
- **Data Migration**: Automatic data migration when updating organization names

## Tech Stack

**Required:**
- **Python**: ^3.9
- **FastAPI**: ^0.104.1 - Modern web framework
- **MongoDB**: Database for master data and dynamic collections
- **PyMongo**: ^4.6.0 - MongoDB driver
- **Pydantic**: ^2.5.0 - Data validation
- **JWT**: python-jose for token-based authentication
- **Bcrypt**: passlib for password hashing

**Development:**
- **Poetry**: Dependency management
- **Uvicorn**: ASGI server

## Architecture

### High Level Diagram

```
                                  (User Request)
                                          ⬇
+-----------------------------------------------------------------------------------+
|   PRESENTATION LAYER (src/routes & src/middleware)                                |
|                                                                                   |
|  [ Client ] ---> [ src/main.py ]                                                  |
|                        ⬇                                                          |
|                 [ Routing Engine ]                                                |
|                        ⬇                                                          |
|       +-----------------------------------+                                       |
|       | Middleware Check (auth_middleware)| <---- (Validate JWT Token)            |
|       +-----------------------------------+                                       |
|                        ⬇                                                          |
|       +-----------------------------------+                                       |
|       | Route Handler (organization_routes)| <---- (Validate Input w/ validators) |
|       +-----------------------------------+                                       |
+----------------------------------------|------------------------------------------+
                                         |
                                         ⬇
+-----------------------------------------------------------------------------------+
|   BUSINESS LOGIC LAYER (src/services)                                             |
|                                                                                   |
|   +-----------------------+      +-------------------------+                      |
|   | OrganizationService   | ---> |     AdminService        |                      |
|   | (Orchestrates Logic)  |      | (Creates User/Hashes PW)|                      |
|   +-----------|-----------+      +-------------------------+                      |
|               |                                                                   |
|               | (Request new DB resource)                                         |
|               ⬇                                                                   |
|   +-----------------------+                                                       |
|   |    DatabaseService    |                                                       |
|   | (Sanitizes Names &    |                                                       |
|   |  Creates Collections) |                                                       |
|   +-----------------------+                                                       |
+-----------------------|-----------------------------------------------------------+
                        |
                        ⬇
+-----------------------------------------------------------------------------------+
|   DATA LAYER (MongoDB)                                                            |
|                                                                                   |
|   [ MASTER DATABASE ]                                                             |
|   |                                                                               |
|   |-- [Collection: organizations] (Metadata: Org Name, CreatedAt)                 |
|   |-- [Collection: admin_users]   (Login Creds, Org_ID link)                      |
|   |                                                                               |
|   |   +-------------------------------------------------------+                   |
|   |   |  DYNAMIC TENANT COLLECTIONS (Created by DBService)    |                   |
|   +-- |  [Collection: org_google ]                            |                   |
|       |  [Collection: org_microsoft ]                         |                   |
|       |  [Collection: org_gdawg_tech ]                        |                   |
|       +-------------------------------------------------------+                   |
+-----------------------------------------------------------------------------------+
```

### Multi-Tenant Design

Each organization gets:
1. **Metadata entry** in `organizations` collection
2. **Admin user** in `admin_users` collection
3. **Dynamic collection** named `org_<sanitized_name>` for organization-specific data

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- MongoDB 4.0 or higher
- Poetry (for dependency management)

### Installation

1. **Clone the repository**
   ```bash
   git clone gauransh415/TWC-Assignment.git
   cd TWC-Assignment
   ```

2. **Install Poetry** (if not already installed)
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies**
   ```bash
   poetry install
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your configuration:
   ```env
   MONGODB_URL=
   DATABASE_NAME=
   JWT_SECRET_KEY=
   JWT_ALGORITHM=
   JWT_EXPIRATION_HOURS=
   ```

5. **Start MongoDB** (if running locally)
   ```bash
   mongod --dbpath /path/to/data/directory
   ```

6. **Run the application**
   ```bash
   poetry run python -m src.main
   ```

   Or using uvicorn directly:
   ```bash
   poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the API**
   - API Base URL: `http://localhost:8000`
   - Interactive Docs: `http://localhost:8000/docs`
   - Alternative Docs: `http://localhost:8000/redoc`

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### Health Check
```http
GET /
```
Returns service status.

---

### Organization Endpoints

#### 1. Create Organization
```http
POST /org/create
Content-Type: application/json

{
  "organization_name": "TWC Corp",
  "email": "admin@TWC.com",
  "password": "SecurePass123"
}
```

**Response (201 Created):**
```json
{
  "organization_id": "507f1f77bcf86cd799439011",
  "organization_name": "TWC Corp",
  "collection_name": "org_TWC_corp",
  "created_at": "2025-12-13T10:30:00Z",
  "admin_email": "admin@TWC.com"
}
```

**Validations:**
- Organization name: 3-50 characters, no SQL injection patterns
- Email: Valid email format
- Password: Minimum 8 characters, must contain uppercase, lowercase, and digit

---

#### 2. Get Organization
```http
GET /org/get?organization_name=TWC Corp
```

**Response (200 OK):**
```json
{
  "organization_id": "507f1f77bcf86cd799439011",
  "organization_name": "TWC Corp",
  "collection_name": "org_TWC_corp",
  "created_at": "2025-12-13T10:30:00Z",
  "admin_email": "admin@TWC.com"
}
```

---

#### 3. Update Organization
```http
PUT /org/update
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "organization_name": "TWC Corporation",
  "email": "new-admin@TWC.com",
  "password": "NewSecurePass456"
}
```

**Response (200 OK):**
```json
{
  "organization_id": "507f1f77bcf86cd799439011",
  "organization_name": "TWC Corporation",
  "collection_name": "org_TWC_corporation",
  "created_at": "2025-12-13T10:30:00Z",
  "admin_email": "new-admin@TWC.com"
}
```

**Notes:**
- Requires authentication
- Creates new collection and migrates data
- Updates admin credentials if provided

---

#### 4. Delete Organization
```http
DELETE /org/delete
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "organization_name": "TWC Corp"
}
```

**Response (200 OK):**
```json
{
  "message": "Organization deleted successfully"
}
```

**Notes:**
- Requires authentication
- Only organization's admin can delete
- Removes collection, admin users, and metadata

---

### Authentication Endpoints

#### Admin Login
```http
POST /admin/login
Content-Type: application/json

{
  "email": "admin@TWC.com",
  "password": "SecurePass123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "admin_id": "507f191e810c19729de860ea",
  "organization_id": "507f1f77bcf86cd799439011",
  "email": "admin@TWC.com",
  "expires_in": 86400
}
```

**JWT Token Usage:**
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### Error Responses

**400 Bad Request:**
```json
{
  "error": "Validation Error",
  "message": "Organization name must be at least 3 characters long"
}
```

**401 Unauthorized:**
```json
{
  "error": "Authentication Failed",
  "message": "Invalid credentials"
}
```

**403 Forbidden:**
```json
{
  "error": "Authorization Failed",
  "message": "Not authorized to delete this organization"
}
```

**404 Not Found:**
```json
{
  "error": "Organization Not Found",
  "message": "The requested organization does not exist"
}
```

**409 Conflict:**
```json
{
  "error": "Duplicate Organization",
  "message": "An organization with this name already exists"
}
```

**500 Internal Server Error:**
```json
{
  "error": "Database Operation Failed",
  "message": "A database operation failed"
}
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | Yes |
| `DATABASE_NAME` | Database name | Yes |
| `JWT_SECRET_KEY` | Secret key for JWT signing | Yes |
| `JWT_ALGORITHM` | JWT algorithm | Yes |
| `JWT_EXPIRATION_HOURS` | Token expiration time | Yes |

## Design Decisions

### 1. Collection-per-Tenant vs Database-per-Tenant

**Chosen: Collection-per-Tenant**

**Rationale:**
- Simpler management with single database connection
- Easier backup and maintenance
- Sufficient isolation for most use cases
- Lower operational overhead

**Trade-offs:**
- Less isolation than database-per-tenant
- All collections share database-level limits
- Suitable for small to medium-scale applications

### 2. Dynamic Collection Naming

Pattern: `org_<sanitized_organization_name>`

**Sanitization Rules:**
- Convert to lowercase
- Replace spaces and hyphens with underscores
- Remove special characters
- Remove consecutive underscores

**Example:** "TWC Corp!" → `org_TWC_corp`

### 3. Update Strategy with Data Migration

When updating organization name:
1. Create new collection with new name
2. Migrate all data from old collection
3. Update metadata in master database
4. Delete old collection

**Rationale:**
- Ensures data consistency
- Allows rollback on failure
- Maintains collection naming convention

### 4. Authentication & Authorization

**JWT-based Authentication:**
- Stateless authentication
- Token contains: admin_id, organization_id, email
- 24-hour expiration (configurable)

**Authorization Model:**
- Admin can only manage their own organization
- Ownership verified via JWT token
- Enforced at service layer

### 5. Password Security

- **Hashing**: Bcrypt with salt
- **Validation**: Minimum 8 characters, uppercase, lowercase, digit
- **Storage**: Only hashed passwords stored


## Scalability Considerations

### Current Architecture Limitations

1. **Single Database Bottleneck**
   - All collections in one database
   - Database-level resource limits shared
   - Potential connection pool exhaustion

2. **Update Operation Blocking**
   - Data migration is synchronous
   - Blocks API during large migrations
   - No progress tracking

3. **No Horizontal Scaling**
   - No sharding strategy
   - Single MongoDB instance
   - No read replicas

### Recommended Improvements

#### For Production Scale:

1. **Implement Database Sharding**
   ```
   - Shard key: organization_id
   - Distribute organizations across multiple databases
   - Use MongoDB sharding or manual partitioning
   ```

2. **Add Caching Layer**
   ```
   - Redis for organization metadata
   - Cache JWT token validations
   - Reduce database queries
   ```

3. **Async Background Jobs**
   ```
   - Use Celery or RQ for migrations
   - Background collection creation
   - Progress tracking for long operations
   ```

4. **Connection Pooling**
   ```
   - Configure optimal pool size
   - Monitor connection usage
   - Implement connection retry logic
   ```

5. **API Rate Limiting**
   ```
   - Prevent abuse
   - Per-organization limits
   - Token bucket algorithm
   ```

### Alternative Architecture

**Database-per-Tenant:**
- Better isolation
- Independent scaling per organization
- Higher operational complexity
- Suitable for enterprise customers

**Hybrid Approach:**
- Small organizations: Shared database
- Large organizations: Dedicated database
- Best of both worlds

## Testing

### Manual Testing with cURL

**Create Organization:**
```bash
curl -X POST http://localhost:8000/org/create \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "Test Corp",
    "email": "admin@test.com",
    "password": "TestPass123"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "TestPass123"
  }'
```

**Get Organization:**
```bash
curl http://localhost:8000/org/get?organization_name=Test%20Corp
```

**Update Organization:**
```bash
curl -X PUT http://localhost:8000/org/update \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "organization_name": "Updated Corp",
    "email": "newemail@test.com"
  }'
```

**Delete Organization:**
```bash
curl -X DELETE http://localhost:8000/org/delete \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "organization_name": "Test Corp"
  }'
```

## Project Structure

```
TWC-Assignment/
├── src/
│   ├── config/
│   │   ├── database.py          # MongoDB connection and indexes
│   │   └── settings.py          # Environment configuration
│   ├── models/
│   │   ├── organization.py      # Organization schemas
│   │   └── admin.py             # Admin user schemas
│   ├── services/
│   │   ├── auth_service.py      # JWT & password handling
│   │   ├── database_service.py  # Dynamic collection operations
│   │   ├── admin_service.py     # Admin user management
│   │   └── organization_service.py  # Organization CRUD
│   ├── routes/
│   │   ├── organization_routes.py  # Organization endpoints
│   │   └── admin_routes.py      # Authentication endpoints
│   ├── middleware/
│   │   ├── auth_middleware.py   # JWT authentication
│   │   └── error_handler.py     # Global error handlers
│   ├── utils/
│   │   ├── validators.py        # Input validation
│   │   └── exceptions.py        # Custom exceptions
│   └── main.py                  # FastAPI application
├── pyproject.toml               # Poetry dependencies
├── .env.example                 # Environment template
├── .gitignore
└── README.md
```

## Assumptions Made

1. **Single Admin per Organization**: Each organization has one admin user
2. **Organization Name Uniqueness**: Names are case-sensitive and must be unique
3. **No Multi-tenancy at DB Level**: All organizations share the same database
4. **JWT for All Protected Routes**: No alternative auth mechanisms
5. **Synchronous Operations**: All operations are blocking (no async jobs)
6. **No Audit Logging**: Changes are not logged for audit purposes
7. **No Soft Deletes**: Deletions are permanent
8. **English Language Only**: No internationalization support

## 👤 Author

Gauransh Sharma

## 📄 License

This project is part of an internship assignment.

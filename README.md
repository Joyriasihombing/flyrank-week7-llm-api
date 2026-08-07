# FlyRank Widget Platform API

A backend API for building and managing widgets, collecting submissions, and providing dashboard statistics.

This project is developed as a **FlyRank Capstone Project** using **FastAPI, SQLAlchemy, SQLite, Pydantic, and JWT authentication**.

The application provides user authentication, widget management, tenant isolation, public widget access, submission management, and dashboard statistics.

---

## 1. Project Overview

The FlyRank Widget Platform is a REST API that allows authenticated users to create and manage their own widgets.

Each widget belongs to a specific user through `user_id`. This ensures **tenant isolation**, meaning users can only access and manage resources that belong to them.

The platform also provides public endpoints so external users can view active widgets and submit data without requiring authentication.

---

## 2. Main Features

### Authentication

- User registration
- User login
- Password hashing
- JWT access token
- Get currently authenticated user
- Protected API endpoints

### Widget Management

Authenticated users can:

- Create widgets
- View their own widgets
- View a specific widget
- Update widgets
- Delete widgets

### Tenant Isolation

Each widget is associated with a `user_id`.

Users can only:

- View their own widgets
- Update their own widgets
- Delete their own widgets
- View submissions from their own widgets

### Public Widget

Public users can:

- View active widgets
- Submit data to widgets

Public widget endpoints do not require authentication.

### Submission

The system stores submissions associated with widgets.

Widget owners can retrieve submissions belonging to their own widgets.

### Dashboard

The platform provides dashboard statistics for authenticated users.

---

## 3. Technology Stack

| Technology | Purpose                         |
| ---------- | ------------------------------- |
| Python     | Programming language            |
| FastAPI    | Backend REST API framework      |
| SQLAlchemy | ORM and database interaction    |
| SQLite     | Database                        |
| Pydantic   | Request and response validation |
| JWT        | Authentication                  |
| Uvicorn    | ASGI server                     |
| Git        | Version control                 |
| GitHub     | Repository hosting              |
| Swagger UI | API testing and documentation   |

---

## 4. Project Structure

```text
flyrank-capstone-widgetplatform/
│
├── app/
│   ├── models/
│   │   ├── user.py
│   │   ├── widget.py
│   │   └── submission.py
│   │
│   ├── schemas/
│   │   ├── user.py
│   │   ├── widget.py
│   │   └── submission.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── widgets.py
│   │   └── public.py
│   │
│   ├── database.py
│   ├── dependencies.py
│   ├── security.py
│   └── main.py
│
├── widget_platform.db
├── requirements.txt
├── README.md
└── .gitignore
```

---

# 5. Installation

## Clone Repository

```bash
git clone https://github.com/Joyriasihombing/flyrank-capstone-widgetplatform.git
cd flyrank-capstone-widgetplatform
```

## Create Virtual Environment

```bash
python3 -m venv venv
```

## Activate Virtual Environment

### macOS / Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 6. Run the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

---

# 7. API Documentation

FastAPI automatically generates interactive API documentation.

### Swagger UI

```text
http://127.0.0.1:8000/docs
```

### OpenAPI JSON

```text
http://127.0.0.1:8000/openapi.json
```

Swagger UI can be used to test all available endpoints.

---

# 8. Authentication API

## Register

```http
POST /auth/register
```

Creates a new user.

### Request

```json
{
  "name": "Joy",
  "email": "joy@example.com",
  "password": "password123"
}
```

### Response

```json
{
  "id": 1,
  "name": "Joy",
  "email": "joy@example.com"
}
```

---

## Login

```http
POST /auth/login
```

Authenticates a user and returns a JWT access token.

### Request

```json
{
  "email": "joy@example.com",
  "password": "password123"
}
```

### Response

```json
{
  "access_token": "JWT_TOKEN",
  "token_type": "bearer"
}
```

The returned access token is used to access protected endpoints.

---

## Get Current User

```http
GET /auth/me
```

Returns information about the currently authenticated user.

### Authorization

```text
Authorization: Bearer <access_token>
```

### Response

```json
{
  "id": 1,
  "name": "Joy",
  "email": "joy@example.com"
}
```

---

# 9. Widget Management API

All widget management endpoints require authentication.

## Create Widget

```http
POST /widgets/
```

Creates a widget for the currently authenticated user.

### Request

```json
{
  "title": "Customer Feedback",
  "description": "Collect customer feedback",
  "widget_type": "form",
  "button_text": "Submit"
}
```

The API automatically assigns:

```text
user_id = current_user.id
```

---

## Get All My Widgets

```http
GET /widgets/
```

Returns only widgets owned by the authenticated user.

This implements tenant isolation.

Example query:

```python
widgets = db.query(Widget).filter(
    Widget.user_id == current_user.id
).all()
```

---

## Get Widget by ID

```http
GET /widgets/{widget_id}
```

Returns a specific widget belonging to the authenticated user.

The API checks both:

```text
widget.id
```

and:

```text
widget.user_id == current_user.id
```

If the widget does not belong to the user:

```http
404 Not Found
```

---

## Update Widget

```http
PUT /widgets/{widget_id}
```

Updates a widget owned by the authenticated user.

The API verifies ownership before updating the resource.

---

## Delete Widget

```http
DELETE /widgets/{widget_id}
```

Deletes a widget owned by the authenticated user.

The API verifies ownership before deleting the resource.

---

# 10. Public Widget API

Public endpoints allow external users to interact with active widgets without authentication.

## Get Public Widget

```http
GET /public/widgets/{widget_id}
```

Returns an active public widget.

---

## Submit to Widget

```http
POST /public/widgets/{widget_id}/submit
```

Creates a submission for a public widget.

Example:

```json
{
  "data": {
    "name": "John",
    "feedback": "Great experience!"
  }
}
```

A successful submission is stored in the database and associated with the corresponding widget.

---

# 11. Submission API

## Get Widget Submissions

```http
GET /widgets/{widget_id}/submissions
```

Returns submissions belonging to a widget.

The API first verifies that the widget belongs to the authenticated user.

Example ownership check:

```python
widget = db.query(Widget).filter(
    Widget.id == widget_id,
    Widget.user_id == current_user.id
).first()
```

If the widget does not belong to the user:

```http
404 Not Found
```

This prevents users from accessing submissions belonging to another user's widget.

---

# 12. Dashboard API

## Dashboard Statistics

```http
GET /widgets/dashboard/stats
```

Returns dashboard statistics for the authenticated user's widgets and submissions.

The endpoint requires authentication.

The statistics are calculated based on resources belonging to the current user.

---

# 13. Tenant Isolation

Tenant isolation is one of the important security requirements of this project.

Every widget contains a `user_id` that identifies its owner.

The authenticated user's ID is obtained from the JWT token.

Example:

```python
current_user: User = Depends(get_current_user)
```

When querying widgets, the API filters by the authenticated user's ID:

```python
db.query(Widget).filter(
    Widget.user_id == current_user.id
).all()
```

For individual resources:

```python
db.query(Widget).filter(
    Widget.id == widget_id,
    Widget.user_id == current_user.id
).first()
```

Therefore, a user cannot access, modify, or delete another user's widgets.

---

# 14. JWT Authentication Flow

The authentication process works as follows:

```text
User
 │
 ├── Register
 │
 ▼
User Account
 │
 ├── Login
 │
 ▼
JWT Access Token
 │
 ▼
Authorization: Bearer <token>
 │
 ▼
Protected Endpoint
 │
 ▼
get_current_user()
 │
 ▼
Authenticated User
```

The JWT token contains information used to identify the authenticated user.

Protected endpoints use the authentication dependency:

```python
current_user: User = Depends(get_current_user)
```

---

# 15. Response Models

The project uses Pydantic response models to provide consistent and validated API responses.

Example:

```python
from pydantic import BaseModel


class WidgetResponse(BaseModel):
    id: int
    title: str
    description: str
    widget_type: str
    button_text: str
    is_active: bool

    class Config:
        from_attributes = True
```

The response model is used by endpoints such as:

```python
@router.get("/", response_model=list[WidgetResponse])
```

Using response models ensures that API responses follow a defined structure.

---

# 16. Error Handling

The API uses HTTP status codes and FastAPI `HTTPException` for error handling.

Common status codes include:

| Status Code | Description        |
| ----------- | ------------------ |
| 200         | Request successful |
| 201         | Resource created   |
| 400         | Bad request        |
| 401         | Unauthorized       |
| 404         | Resource not found |
| 422         | Validation error   |

### Example: Duplicate Email

```python
raise HTTPException(
    status_code=400,
    detail="Email already registered"
)
```

### Example: Invalid Login

```python
raise HTTPException(
    status_code=401,
    detail="Invalid email or password"
)
```

### Example: Widget Not Found

```python
raise HTTPException(
    status_code=404,
    detail="Widget not found"
)
```

---

# 17. Database

The application uses SQLite with SQLAlchemy.

Main entities:

```text
User
 │
 └── Widget
       │
       └── Submission
```

### User

Stores user account information.

### Widget

Stores widget information and its owner through `user_id`.

### Submission

Stores data submitted through a widget and references the corresponding `widget_id`.

---

# 18. API Testing

The API can be tested using Swagger UI or Postman.

Recommended testing sequence:

### Step 1 — Register

```http
POST /auth/register
```

### Step 2 — Login

```http
POST /auth/login
```

Copy the returned:

```text
access_token
```

### Step 3 — Authorize

In Swagger UI, click:

```text
Authorize
```

Enter:

```text
Bearer <access_token>
```

### Step 4 — Test Current User

```http
GET /auth/me
```

### Step 5 — Create Widget

```http
POST /widgets/
```

### Step 6 — Get Widgets

```http
GET /widgets/
```

### Step 7 — Get Widget

```http
GET /widgets/{widget_id}
```

### Step 8 — Update Widget

```http
PUT /widgets/{widget_id}
```

### Step 9 — Submit Public Data

```http
POST /public/widgets/{widget_id}/submit
```

### Step 10 — Get Submissions

```http
GET /widgets/{widget_id}/submissions
```

### Step 11 — Check Dashboard

```http
GET /widgets/dashboard/stats
```

### Step 12 — Delete Widget

```http
DELETE /widgets/{widget_id}
```

---

# 19. Security Considerations

The project includes several basic security mechanisms:

- Passwords are hashed before being stored.
- JWT is used for authentication.
- Protected endpoints require authentication.
- Widget ownership is verified using `user_id`.
- Users cannot access another user's widgets.
- Submission access is restricted to the widget owner.
- Public endpoints are separated from authenticated endpoints.

---

# 20. Environment and Dependencies

Dependencies are stored in:

```text
requirements.txt
```

Install them using:

```bash
pip install -r requirements.txt
```

The virtual environment should not be committed to Git.

The `.gitignore` file should include:

```text
venv/
__pycache__/
*.pyc
.env
```

---

# 21. Git Workflow

The project uses Git for version control.

Check the current status:

```bash
git status
```

Add changes:

```bash
git add .
```

Create a commit:

```bash
git commit -m "Complete FlyRank widget platform"
```

Push to GitHub:

```bash
git push origin main
```

Repository:

https://github.com/Joyriasihombing/flyrank-capstone-widgetplatform

---

# 22. Project Validation Checklist

Before submitting the capstone, verify the following:

- [x] FastAPI application runs successfully
- [x] User registration works
- [x] User login works
- [x] JWT authentication works
- [x] `/auth/me` works
- [x] Widget CRUD works
- [x] Tenant isolation is implemented
- [x] Public widget endpoint works
- [x] Public submission endpoint works
- [x] Widget submission retrieval works
- [x] Dashboard statistics endpoint works
- [x] Response models are implemented
- [x] Error handling is implemented
- [x] SQLAlchemy models are used
- [x] SQLite database is configured
- [x] Swagger documentation is available
- [x] Project structure is organized
- [x] `requirements.txt` is included
- [x] `.gitignore` is configured
- [x] README documentation is included

---

# 23. How to Run

The complete application can be started with:

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

---

# Author

**Joy Ria Sihombing**

FlyRank Capstone Project

GitHub Repository:

https://github.com/Joyriasihombing/flyrank-capstone-widgetplatform

# API Design

## Authentication

POST /auth/register
POST /auth/login
GET /auth/me

---

## Widget Management

POST /widgets
GET /widgets
GET /widgets/{id}
PUT /widgets/{id}
DELETE /widgets/{id}

---

## Public Widget

GET /widget.js
GET /widgets/{id}/config

---

## Public Submission

POST /submissions

---

## Dashboard

GET /dashboard/submissions
GET /dashboard/stats
GET /dashboard/widgets
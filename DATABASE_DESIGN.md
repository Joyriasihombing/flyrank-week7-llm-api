# Database Design

## Users

- id
- name
- email
- password_hash
- created_at

## Widgets

- id
- user_id
- title
- description
- widget_type
- button_text
- is_active
- created_at

## Submissions

- id
- widget_id
- name
- email
- message
- country
- city
- ip_address
- created_at

## Relationships

User (1) ------ (*) Widget

Widget (1) ------ (*) Submission
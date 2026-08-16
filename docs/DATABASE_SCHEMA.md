# Database Schema Specification

This document details the SQLite database schema used for the Project Management MVP App.

## Entity Relationship Diagram

```
+----------------+        +-----------------+        +------------------+        +-----------------+
|     users      |        |     boards      |        |     columns      |        |      cards      |
+----------------+        +-----------------+        +------------------+        +-----------------+
| id (PK)        | 1    * | id (PK)         | 1    * | id (PK)          | 1    * | id (PK)         |
| username       |<-------| user_id (FK)    |<-------| board_id (FK)    |<-------| column_id (FK)  |
| password_hash  |        | title           |        | title            |        | title           |
| created_at     |        | created_at      |        | position         |        | details         |
+----------------+        +-----------------+        +------------------+        | position        |
                                                                                 | created_at      |
                                                                                 +-----------------+
```

## Table Specifications

### 1. `users`
Stores user credentials.
- `id` (VARCHAR(36), Primary Key): Unique user identifier.
- `username` (VARCHAR(64), Unique, Indexed): User sign-in name (Default: `user`).
- `password_hash` (VARCHAR(256)): Password hash (Default MVP password: `password`).
- `created_at` (DATETIME): Timestamp of creation.

### 2. `boards`
Stores Kanban board instances (1 per user for MVP).
- `id` (VARCHAR(36), Primary Key): Board ID.
- `user_id` (VARCHAR(36), Foreign Key -> `users.id`, Indexed): Owning user ID.
- `title` (VARCHAR(128)): Board title.
- `created_at` (DATETIME): Timestamp of creation.

### 3. `columns`
Stores fixed Kanban columns for a board.
- `id` (VARCHAR(36), Primary Key): Column ID (e.g. `col-backlog`).
- `board_id` (VARCHAR(36), Foreign Key -> `boards.id`, Indexed): Owning board ID.
- `title` (VARCHAR(128)): Display name of column (e.g. "Backlog").
- `position` (INTEGER): Left-to-right display index (0..4).

### 4. `cards`
Stores task cards within columns.
- `id` (VARCHAR(36), Primary Key): Card ID.
- `column_id` (VARCHAR(36), Foreign Key -> `columns.id`, Indexed): Owning column ID.
- `title` (VARCHAR(256)): Task title.
- `details` (TEXT): Detailed description of task.
- `position` (INTEGER): Top-to-bottom display index within column.
- `created_at` (DATETIME): Timestamp of creation.

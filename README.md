# 🏰 Project Dungeon — Backend

A **Django REST API + WebSocket server** powering the Project Dungeon project management platform. Built with Django Channels for real-time communication and integrated with Google Calendar OAuth.

---

## 🔧 Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 6.0 |
| API | Django REST Framework 3.16 |
| Real-Time | Django Channels 4.3 + Daphne (ASGI) |
| Auth | JWT (`djangorestframework_simplejwt`) + Google OAuth 2.0 |
| Database | PostgreSQL (via `psycopg2`) |
| CORS | `django-cors-headers` |
| Filtering | `django-filter` |

---

## 📁 Project Structure

```
project_dungeon_backend/
├── apps/
│   ├── account/          # Custom user model, registration & JWT login
│   ├── management/       # Projects, Tasks, Teams, Repos, Issues, Chat
│   └── google_calendar/  # Events + Google Calendar OAuth & sync
├── src/
│   ├── settings.py
│   ├── urls.py
│   └── asgi.py           # ASGI config (HTTP + WebSocket routing)
├── manage.py
├── requirements.txt
└── .env
```

---

## 🗃️ Data Models

### `account` app
- **User** — Extends `AbstractUser`. Login field: `email`. Extra fields: `phone`, `birth_date`, `role` (`user` / `admin`)

### `management` app
- **Project** — `title`, `description`, `owner` (FK), `collaborators` (M2M Users), `teams` (M2M), `repositories` (M2M)
- **Task** — `title`, `description`, `status` (`todo` / `in_progress` / `finished`), `priority` (`low` / `medium` / `high`), `task_type` (`feature` / `bug` / `documentation` / `other`), `project` (FK), `assignee` (FK), `deadline`
- **Team** — `name`, `description`, `owner` (FK), `collaborators` (M2M), `projects` (M2M)
- **Repository** — `name`, `description`, `link` (URL)
- **Issue** — `title`, `description`, `status` (`open` / `resolved` / `closed`), `task` (FK), `project` (FK), `created_by` (FK)
- **Message** — Project chat: `project` (FK), `sender` (FK), `content`, `created_at`

### `google_calendar` app
- **Event** — Project event with Google Calendar sync support

---

## 🌐 API Endpoints

### Auth — `/api/auth/`

| Method | Endpoint | Description |
|---|---|---|
| POST | `/register/` | Register a new user |
| POST | `/token/` | Obtain JWT access & refresh tokens |
| POST | `/token/refresh/` | Refresh the access token |
| GET | `/users/` | List all users |

### Management — `/api/management/`

| Method | Endpoint | Description |
|---|---|---|
| GET / POST | `/projects/` | List / create projects |
| GET / PATCH / DELETE | `/tasks/` | List / update / delete tasks |
| GET / PATCH / DELETE | `/tasks/<id>/` | Retrieve / update / delete a task |
| GET / POST | `/teams/` | List / create teams |
| GET / PATCH / DELETE | `/teams/<id>/` | Retrieve / update / delete a team |
| GET / POST / PATCH / DELETE | `/repositories/` | Manage repositories |
| GET / POST / PATCH / DELETE | `/issues/` | Manage issues |
| GET / PATCH / DELETE | `/issues/<id>/` | Retrieve / update / delete an issue |
| GET / POST | `/messages/` | Fetch / send project chat messages |

### WebSocket

| Path | Description |
|---|---|
| `ws://.../ws/chat/<project_id>/` | Real-time chat for a project |

### Google Calendar — `/api/google/`

| Method | Endpoint | Description |
|---|---|---|
| GET / POST | `/events/` | List / create local events |
| GET / PATCH / DELETE | `/events/<id>/` | Retrieve / update / delete an event |
| GET | `/auth-url/` | Get Google OAuth authorization URL |
| GET | `/callback/` | Handle Google OAuth callback |
| GET | `/status/` | Check Google connection status |
| POST | `/sync/` | Sync events with Google Calendar |
| POST | `/create/` | Create event directly on Google Calendar |

---

## ⚙️ Setup

### Prerequisites
- Python 3.11+
- PostgreSQL
- A Google Cloud project with the **Google Calendar API** enabled

### Steps

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file:**
   ```env
   DATABASE_ENGINE=django.db.backends.postgresql
   DATABASE_NAME=project_management
   DATABASE_USER=your_db_user
   DATABASE_PASSWORD=your_db_password
   DATABASE_HOST=localhost
   DATABASE_PORT=5432

   GOOGLE_CLIENT_ID=your_google_client_id
   GOOGLE_CLIENT_SECRET=your_google_client_secret
   GOOGLE_REDIRECT_URI=http://127.0.0.1:5173/google/callback
   ```

4. **Apply migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the ASGI server:**
   ```bash
   daphne -b 127.0.0.1 -p 8000 src.asgi:application
   ```

The API will be available at **http://127.0.0.1:8000**.

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_ENGINE` | Django DB backend |
| `DATABASE_NAME` | PostgreSQL database name |
| `DATABASE_USER` | PostgreSQL username |
| `DATABASE_PASSWORD` | PostgreSQL password |
| `DATABASE_HOST` | Database host |
| `DATABASE_PORT` | Database port |
| `GOOGLE_CLIENT_ID` | Google OAuth 2.0 Client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 2.0 Client Secret |
| `GOOGLE_REDIRECT_URI` | OAuth redirect URI (must match Google Console config) |

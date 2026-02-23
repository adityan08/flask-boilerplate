# Flask Boilerplate

A starting point for web application development using Python Flask. This boilerplate provides a structured project layout with common integrations already wired up, so you can focus on building application logic from the start.

## Project Structure

```
flask-boilerplate/
├── app/
│   ├── __init__.py          # Application factory (create_app)
│   ├── tasks.py             # Background job definitions (Celery tasks)
│   ├── api/
│   │   ├── __init__.py      # Blueprint registration
│   │   └── health.py        # Example endpoint
│   ├── core/
│   │   ├── config.py        # Environment-based configuration classes
│   │   ├── constants.py     # Application-wide constants
│   │   ├── crud.py          # Reusable database CRUD helpers
│   │   ├── aws.py           # AWS/S3 integration utilities
│   │   └── custom_errors.py # Custom exception definitions
│   ├── models/
│   │   ├── __init__.py      # Model imports (register models here)
│   │   └── base.py          # BaseModel with common columns
│   └── services/
│       └── __init__.py      # Service layer modules
├── runserver.py             # Entry point to run the development server
├── requirements.txt         # Python dependencies
├── env_example.txt          # Example environment variable file
└── migration_commands.txt   # Reference commands for database migrations
```

## Getting Started

**1. Clone and set up the environment**

```bash
git clone <repo-url>
cd flask-boilerplate
python -m venv venv
source venv/bin/activate
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure environment variables**

Copy `env_example.txt` to `.env` and fill in the values:

```bash
cp env_example.txt .env
```

**4. Run the development server**

```bash
python runserver.py
```

The server starts at `http://localhost:5000`. API documentation is available at `http://localhost:5000/docs/`.

## How to Use This Boilerplate

### Defining an Endpoint

All endpoints are defined inside `app/api/`. Create a new Python file for each resource group, define your route functions there, and import the file in `app/api/__init__.py` so Flask registers it.

```python
# app/api/user.py

from app.api import bp

@bp.route("/users", methods=["GET"])
def get_users():
    # your logic here
    return {"users": []}
```

```python
# app/api/__init__.py

from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import health, user  # add your new module here
```

### Writing Service Logic

Business logic should live in `app/services/`. Create a separate module for each logical domain (for example, `app/services/user_service.py`). Endpoints in `app/api/` call into these service modules rather than containing logic directly. This separation keeps route handlers thin and the logic testable.

```python
# app/services/user_service.py

def get_all_users():
    # query and return users
    pass
```

### Defining Database Models

Database table models go in `app/models/`. Each model should extend `BaseModel` from `app/models/base.py`, which provides common columns (`is_active`, `created_at`, `updated_at`) automatically.

```python
# app/models/user.py

from app import db
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
```

After creating a model, import it in `app/models/__init__.py` so Flask-Migrate can detect it:

```python
# app/models/__init__.py

from app.models.user import User
```

**Running migrations**

```bash
flask db migrate -m "describe your change"
flask db upgrade
```

### Defining Constants

Application-wide constants (string literals, numeric thresholds, status codes, etc.) belong in `app/core/constants.py`. Import from this file wherever needed to avoid magic values scattered across the codebase.

```python
# app/core/constants.py

DEFAULT_PAGE_SIZE = 20
USER_STATUS_ACTIVE = "active"
```

### Managing Environment Variables

All environment variables are read in `app/core/config.py`. The file defines three configuration classes: `Config` (production), `DevelopmentConfig`, and `TestConfig`. The active configuration is selected based on the `CONFIG` environment variable (`dev`, `prod`, or `test`).

To add a new environment variable:

1. Add it to `env_example.txt` with a placeholder value.
2. Add it to your `.env` file with the real value.
3. Read it in the appropriate config class in `app/core/config.py`.

```python
# app/core/config.py

class Config(object):
    MY_NEW_VAR = os.environ['MY_NEW_VAR']
```

You can then access it anywhere via `current_app.config['MY_NEW_VAR']` or through the config object directly.

### Writing Background Jobs

Background tasks are managed using Celery and should be defined in `app/tasks.py`. Redis is used as the broker and result backend (configured via `REDIS_URL` in your `.env`).

```python
# app/tasks.py

from celery import Celery
from app.core.config import Config_is

celery = Celery(__name__, broker=Config_is.REDIS_URL)

@celery.task
def send_email(recipient, subject, body):
    # send email logic
    pass
```

To trigger a task from an endpoint or service, call it with `.delay()` or `.apply_async()`:

```python
send_email.delay("user@example.com", "Welcome", "Thanks for signing up.")
```

Start the Celery worker separately:

```bash
celery -A app.tasks.celery worker --loglevel=info
```

### Adding Packages

All Python dependencies are tracked in `requirements.txt`. When you add a new package, install it and update the file:

```bash
pip install <package-name>
pip freeze > requirements.txt
```

Keep `requirements.txt` pinned to specific versions to ensure reproducible environments.

## Built-in Integrations

| Component          | Library                  |
|--------------------|--------------------------|
| ORM                | Flask-SQLAlchemy         |
| Migrations         | Flask-Migrate (Alembic)  |
| Serialization      | Flask-Marshmallow        |
| Background jobs    | Celery + Redis           |
| API documentation  | Flasgger (Swagger UI)    |
| CORS               | Flask-CORS               |
| Authentication     | Flask-HTTPAuth           |
| Response compression | Flask-Compress         |
| AWS / S3           | boto3                    |
| Production server  | Gunicorn                 |

## Running in Production

Use Gunicorn to serve the application:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 "runserver:app"
```

Set `CONFIG=prod` in your environment to activate the production configuration class.
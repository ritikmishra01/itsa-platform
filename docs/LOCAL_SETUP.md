# ITSA Platform: Local Development Setup & Workflows

## 1. Quick Start Commands

To start the local development environment:

```powershell
# 1. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 2. Run test suite
pytest -q

# 3. Start local development server
python run.py
```

The server binds to `http://127.0.0.1:5000` with interactive debugging enabled (`FLASK_DEBUG=True`).

---

## 2. Default Local Demo Accounts

The project includes seeded accounts for testing and demonstration:

| Role | Email | Password | Full Name / Description |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@itsa.edu` | `SecureLocalAdmin#2026` | ITSA Administrator (Full Superuser Access) |
| **Coordinator 1** | `coord1@itsa.edu` | `Coord#2026` | Prof. Rajesh Kulkarni (Lead: TechFest 2026) |
| **Coordinator 2** | `coord2@itsa.edu` | `Coord#2026` | Dr. Sunita Patil (Lead: CodeSprint 2026) |
| **Coordinator 3** | `coord3@itsa.edu` | `Coord#2026` | Prof. Amit Deshmukh (Lead: AI Workshop) |
| **Coordinator 4** | `coord4@itsa.edu` | `Coord#2026` | Dr. Neha Sharma (Lead: WebDev Bootcamp) |
| **Coordinator 5** | `coord5@itsa.edu` | `Coord#2026` | Prof. Vikram Joshi (Lead: Innovation Meetup) |
| **Student** | `rahul@itsa.edu` | `Student@12345` | Rahul Sharma (Computer Science, Year 3) |

---

## 3. Local Database Management

- The local development environment uses **SQLite** located at `instance/itsa_platform.db` (or relative path specified by `DATABASE_URL=sqlite:///itsa_platform.db`).
- To re-seed the 5 demo coordinators and 5 college events without duplicating existing data:
  ```powershell
  python scripts/seed_demo_data.py
  ```
- To test full database audit:
  ```powershell
  python scripts/audit_db.py
  ```

---

## 4. Running Tests Locally

Run the complete test suite:
```powershell
pytest -q
```
Run specific module tests:
```powershell
pytest tests/test_auth.py -v
pytest tests/test_events.py -v
pytest tests/test_issue_fixes.py -v
```
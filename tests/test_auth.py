def test_health_check(client):
    res = client.get('/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'healthy'

def test_student_registration(client):
    res = client.post('/api/v1/auth/register', json={
        'email': 'new_student@itsa.edu',
        'password': 'Password@123',
        'full_name': 'New Student',
        'student_id': 'ST2026999',
        'department': 'Information Technology',
        'year_of_study': 2
    })
    assert res.status_code == 201
    assert res.get_json()['success'] is True

def test_login_success(client):
    res = client.post('/api/v1/auth/login', json={
        'email': 'test_student@itsa.edu',
        'password': 'Student@12345'
    })
    assert res.status_code == 200
    assert res.get_json()['data']['email'] == 'test_student@itsa.edu'

def test_login_wrong_password(client):
    res = client.post('/api/v1/auth/login', json={
        'email': 'test_student@itsa.edu',
        'password': 'WrongPassword123'
    })
    assert res.status_code == 401


def test_database_url_normalization():
    import pytest
    from app.config import normalize_database_url

    # 1. Standard Render postgres URLs
    assert normalize_database_url("postgres://u:p@host:5432/db") == "postgresql+psycopg2://u:p@host:5432/db"
    assert normalize_database_url("postgresql://u:p@host:5432/db") == "postgresql+psycopg2://u:p@host:5432/db"
    assert normalize_database_url("postgresql+psycopg2://u:p@host:5432/db") == "postgresql+psycopg2://u:p@host:5432/db"

    # 2. Wrapped quotes and whitespace
    assert normalize_database_url(' "postgresql://u:p@host:5432/db" ') == "postgresql+psycopg2://u:p@host:5432/db"
    assert normalize_database_url(" 'postgres://u:p@host:5432/db' \n") == "postgresql+psycopg2://u:p@host:5432/db"

    # 3. Accidental variable prefix
    assert normalize_database_url("DATABASE_URL=postgresql://u:p@host:5432/db") == "postgresql+psycopg2://u:p@host:5432/db"

    # 4. SQLite local support
    assert normalize_database_url("sqlite:///itsa_platform.db") == "sqlite:///itsa_platform.db"
    assert "sqlite:///" in normalize_database_url("")
    assert "sqlite:///" in normalize_database_url(None)

    # 5. Safe rejection of unconfigured placeholder
    with pytest.raises(ValueError) as excinfo:
        normalize_database_url("<Render PostgreSQL Internal Database URL>")
    assert "placeholder" in str(excinfo.value).lower()


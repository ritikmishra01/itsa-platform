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


def test_admin_creation_and_password_synchronization():
    import os
    from app import create_app, db
    from app.models.user import User
    from scripts.init_prod_admin import init_production_system

    test_app = create_app('testing')
    with test_app.app_context():
        db.create_all()

        # 1. Initial creation with Password A
        os.environ['ADMIN_EMAIL'] = 'admin@itsa.edu'
        os.environ['ADMIN_PASSWORD'] = 'InitialAdminPass#2026'
        init_production_system(test_app)

        admin_count = User.query.filter_by(role='ADMIN').count()
        assert admin_count == 1
        admin = User.query.filter_by(email='admin@itsa.edu').first()
        assert admin is not None
        assert admin.role == 'ADMIN'
        assert admin.check_password('InitialAdminPass#2026') is True
        assert admin.check_password('WrongPass#2026') is False

    test_client = test_app.test_client()

    # Test login with Initial Password
    res = test_client.post('/api/v1/auth/login', json={
        'email': 'admin@itsa.edu',
        'password': 'InitialAdminPass#2026'
    })
    assert res.status_code == 200
    assert res.get_json()['data']['role'] == 'ADMIN'

    # Test login with Incorrect Password fails
    res_fail = test_client.post('/api/v1/auth/login', json={
        'email': 'admin@itsa.edu',
        'password': 'WrongPass#2026'
    })
    assert res_fail.status_code == 401

    with test_app.app_context():
        # 2. Re-running initialization with SAME password is idempotent and creates no duplicate
        init_production_system(test_app)
        assert User.query.filter_by(role='ADMIN').count() == 1

        # 3. Update/Sync Password to Password B without creating duplicates
        os.environ['ADMIN_PASSWORD'] = 'UpdatedAdminPass#2026'
        init_production_system(test_app)

        # Verify no duplicate admin created
        admin_count_after = User.query.filter_by(role='ADMIN').count()
        assert admin_count_after == 1

        admin_updated = User.query.filter_by(email='admin@itsa.edu').first()
        assert admin_updated.check_password('UpdatedAdminPass#2026') is True
        assert admin_updated.check_password('InitialAdminPass#2026') is False

    # Test login with Updated Password succeeds
    res_new = test_client.post('/api/v1/auth/login', json={
        'email': 'admin@itsa.edu',
        'password': 'UpdatedAdminPass#2026'
    })
    assert res_new.status_code == 200
    assert res_new.get_json()['data']['role'] == 'ADMIN'

    # Test old password now fails
    res_old = test_client.post('/api/v1/auth/login', json={
        'email': 'admin@itsa.edu',
        'password': 'InitialAdminPass#2026'
    })
    assert res_old.status_code == 401




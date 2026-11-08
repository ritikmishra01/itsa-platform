"""
Cross-Role Functional and Security Verification Script for ITSA Platform.
Tests public, student, coordinator, and admin routes with role boundary validation.
"""
import sys
import os

# Add root directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models.user import User
from app.models.event import Event

def run_verification():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    client = app.test_client()

    results = []

    def check(name, status, expected_statuses, extra=""):
        passed = status in expected_statuses
        results.append({
            "name": name,
            "status": status,
            "expected": expected_statuses,
            "passed": passed,
            "extra": extra
        })
        mark = "PASS" if passed else "FAIL"
        print(f"[{mark}] {name} -> HTTP {status} (Expected {expected_statuses}) {extra}")

    print("=" * 70)
    print("PHASE 1: PUBLIC / GUEST ACCESSIBILITY TESTS")
    print("=" * 70)

    public_urls = [
        ("Events Directory", "/events"),
        ("Leaderboard", "/leaderboard"),
        ("Certificate Verification", "/certificates/verify"),
        ("Login Page", "/login"),
        ("Register Page", "/register"),
    ]

    for name, url in public_urls:
        res = client.get(url)
        check(f"Guest: {name} ({url})", res.status_code, [200])

    # Unauthenticated root redirects to login
    res = client.get("/", follow_redirects=False)
    check("Guest: Root Route Dispatcher (Expect 302 -> /login)", res.status_code, [302])

    # Test protected routes as guest
    res = client.get("/student/dashboard", follow_redirects=False)
    check("Guest -> /student/dashboard (Expect Redirect to Login)", res.status_code, [302])
    res = client.get("/coordinator/dashboard", follow_redirects=False)
    check("Guest -> /coordinator/dashboard (Expect Redirect to Login)", res.status_code, [302])
    res = client.get("/admin/dashboard", follow_redirects=False)
    check("Guest -> /admin/dashboard (Expect Redirect to Login)", res.status_code, [302])

    with app.app_context():
        sample_event = Event.query.first()
        sample_event_id = sample_event.id if sample_event else 1

    print("\n" + "=" * 70)
    print("PHASE 2: STUDENT SESSION & BOUNDARY TESTS")
    print("=" * 70)

    # Login as student
    student_client = app.test_client()
    login_res = student_client.post("/api/v1/auth/login", json={
        "email": "demo.student001@example.test",
        "password": "DemoStudent@123"
    })
    check("Student Login via API", login_res.status_code, [200])

    student_urls = [
        ("Student Dashboard", "/student/dashboard"),
        ("My Events", "/my-events"),
        ("My Tickets", "/tickets"),
        ("My Certificates", "/certificates"),
        ("My Attendance", "/attendance"),
        ("Community Feed", "/feed"),
        ("Leaderboard", "/leaderboard"),
        ("AI Chatbot", "/chatbot"),
        ("Student Profile", "/profile"),
        ("Notifications", "/notifications"),
    ]

    for name, url in student_urls:
        res = student_client.get(url)
        check(f"Student: {name} ({url})", res.status_code, [200])

    # Security boundary checks: Student must NOT access Admin or Coordinator routes
    res = student_client.get("/admin/dashboard", follow_redirects=False)
    check("Student RBAC -> /admin/dashboard (Expect 403 Forbidden)", res.status_code, [403, 302])
    res = student_client.get("/coordinator/dashboard", follow_redirects=False)
    check("Student RBAC -> /coordinator/dashboard (Expect 403 Forbidden)", res.status_code, [403, 302])

    print("\n" + "=" * 70)
    print("PHASE 3: COORDINATOR SESSION & BOUNDARY TESTS")
    print("=" * 70)

    # Login as coordinator
    coord_client = app.test_client()
    login_res = coord_client.post("/api/v1/auth/login", json={
        "email": "demo.coord001@example.test",
        "password": "DemoCoord@123"
    })
    check("Coordinator Login via API", login_res.status_code, [200])

    coord_urls = [
        ("Coordinator Dashboard", "/coordinator/dashboard"),
        ("Attendance Roster", f"/coordinator/events/{sample_event_id}/attendance"),
        ("QR Scanner", f"/coordinator/events/{sample_event_id}/scan"),
        ("Feedback & AI Sentiment", f"/coordinator/events/{sample_event_id}/feedback"),
    ]

    for name, url in coord_urls:
        res = coord_client.get(url)
        check(f"Coordinator: {name} ({url})", res.status_code, [200])

    # Security boundary check: Coordinator must NOT access Admin routes
    res = coord_client.get("/admin/dashboard", follow_redirects=False)
    check("Coordinator RBAC -> /admin/dashboard (Expect 403 Forbidden)", res.status_code, [403, 302])

    print("\n" + "=" * 70)
    print("PHASE 4: ADMIN SESSION & ALL ADMIN SUBPAGES")
    print("=" * 70)

    # Login as admin
    admin_client = app.test_client()
    login_res = admin_client.post("/api/v1/auth/login", json={
        "email": "demo.admin001@example.test",
        "password": "DemoAdmin@123"
    })
    check("Admin Login via API", login_res.status_code, [200])

    admin_urls = [
        ("Admin Dashboard", "/admin/dashboard"),
        ("Admin Users", "/admin/users"),
        ("Admin Events", "/admin/events"),
        ("Admin Registrations", "/admin/registrations"),
        ("Admin Attendance", "/admin/attendance"),
        ("Admin Certificates", "/admin/certificates"),
        ("Admin Coordinators", "/admin/coordinators"),
        ("Admin Analytics", "/admin/analytics"),
        ("Admin AI Center", "/admin/ai-center"),
        ("Admin Community", "/admin/community"),
        ("Admin Gamification", "/admin/gamification"),
        ("Admin Gallery", "/admin/gallery"),
        ("Admin Reports", "/admin/reports"),
        ("Admin Audit Logs", "/admin/audit-logs"),
        ("Admin Settings", "/admin/settings"),
        ("Admin Search with Query", "/admin/search?q=demo"),
        ("Admin Moderation Queue", "/admin/moderation"),
        ("Admin Notifications", "/admin/notifications"),
    ]

    for name, url in admin_urls:
        res = admin_client.get(url)
        check(f"Admin: {name} ({url})", res.status_code, [200])

    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["passed"])
    failed_tests = total_tests - passed_tests

    print("\n" + "=" * 70)
    print(f"VERIFICATION SUMMARY: {passed_tests}/{total_tests} Passed ({failed_tests} Failed)")
    print("=" * 70)

    return failed_tests == 0

if __name__ == '__main__':
    success = run_verification()
    sys.exit(0 if success else 1)

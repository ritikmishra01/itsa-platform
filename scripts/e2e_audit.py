import os
import sys
import json
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models.user import User
from app.models.event import Event
from app.models.certificate import Certificate
from app.models.ticket import EventTicket

def run_e2e_audit():
    app = create_app('development')
    client = app.test_client()

    print("==================================================")
    print("STARTING ITSA PLATFORM END-TO-END PRODUCTION AUDIT")
    print("==================================================")

    with app.app_context():
        # 1. Health check
        res = client.get('/health')
        assert res.status_code == 200, f"Health check failed: {res.status_code}"
        print(" [PASS] 1. GET /health is active and healthy.")

        # 2. Register fresh student
        email = f"audit_student_{os.getpid()}@itsa.edu"
        reg_res = client.post('/api/v1/auth/register', json={
            'email': email,
            'password': 'AuditPassword@123',
            'full_name': 'Audit Tester',
            'student_id': f'AUDIT_{os.getpid()}',
            'department': 'Computer Science',
            'year_of_study': 3,
            'bio': 'Auditing full stack flows'
        })
        assert reg_res.status_code == 201, f"Student registration failed: {reg_res.get_json()}"
        user_data = reg_res.get_json()['data']
        student_id = user_data['id']
        print(f" [PASS] 2. Student registered successfully: {email} (ID: {student_id})")

        # 3. Browse open events
        events_res = client.get('/api/v1/events')
        assert events_res.status_code == 200
        events = events_res.get_json()['data']
        assert len(events) > 0, "No open events found"
        event = events[0]
        event_id = event['id']
        print(f" [PASS] 3. Retrieved open events. Selected: '{event['title']}' (ID: {event_id})")

        # 4. Student registers for event
        event_reg = client.post(f'/api/v1/events/{event_id}/register')
        assert event_reg.status_code == 201, f"Event registration failed: {event_reg.get_json()}"
        ticket_data = event_reg.get_json()['data']['ticket']
        ticket_code = ticket_data['ticket_code']
        qr_image_path = ticket_data['qr_image_path']
        assert ticket_code.startswith('ITSA-TKT-'), f"Invalid ticket format: {ticket_code}"
        print(f" [PASS] 4. Event registration confirmed. Ticket Code: {ticket_code}")

        # Check QR image exists on disk
        full_qr_path = os.path.join(app.config['UPLOAD_FOLDER'], qr_image_path.replace('uploads/', ''))
        assert os.path.exists(full_qr_path), f"QR code image not generated on disk: {full_qr_path}"
        print(f" [PASS] 5. QR image verified on filesystem: {full_qr_path}")

        # 5. Unauthorized scan: Student tries to mark their own attendance
        student_scan = client.post('/api/v1/attendance/scan', json={
            'event_id': event_id,
            'ticket_code': ticket_code
        })
        assert student_scan.status_code == 403, f"Security Violation: Student was able to scan own attendance! Status: {student_scan.status_code}"
        print(" [PASS] 6. RBAC Guard verified: Student cannot scan own attendance (403 Forbidden).")

        # 6. Coordinator logs in and scans attendance
        client.post('/api/v1/auth/logout')
        coord_login = client.post('/api/v1/auth/login', json={
            'email': 'coordinator@itsa.edu',
            'password': 'Coord@12345'
        })
        assert coord_login.status_code == 200, f"Coordinator login failed: {coord_login.get_json()}"
        print(" [PASS] 7. Coordinator logged in.")

        # Coordinator scans student's QR code
        coord_scan = client.post('/api/v1/attendance/scan', json={
            'event_id': event_id,
            'ticket_code': ticket_code
        })
        assert coord_scan.status_code == 200, f"Coordinator scan failed: {coord_scan.get_json()}"
        print(" [PASS] 8. Coordinator QR check-in verified (+10 ITSA points & cert generated).")

        # 7. Duplicate scan attempt must be rejected
        dup_scan = client.post('/api/v1/attendance/scan', json={
            'event_id': event_id,
            'ticket_code': ticket_code
        })
        assert dup_scan.status_code == 400, f"Duplicate scan was not rejected! Status: {dup_scan.status_code}"
        print(f" [PASS] 9. Duplicate attendance scan blocked: {dup_scan.get_json()['error']['message']}")

        # 8. Student checks certificate & downloads PDF
        client.post('/api/v1/auth/logout')
        client.post('/api/v1/auth/login', json={'email': email, 'password': 'AuditPassword@123'})

        my_certs = client.get('/api/v1/certificates/my')
        assert my_certs.status_code == 200
        certs_list = my_certs.get_json()['data']
        assert len(certs_list) >= 1, "Certificate was not automatically generated"
        cert = certs_list[0]
        cert_code = cert['certificate_code']
        print(f" [PASS] 10. Certificate verified in student account: {cert_code}")

        # Check PDF generated on disk
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], cert['pdf_path'].replace('uploads/', ''))
        assert os.path.exists(pdf_path), f"Certificate PDF does not exist on disk: {pdf_path}"
        print(f" [PASS] 11. ReportLab Certificate PDF verified on disk: {pdf_path}")

        # Public verification
        client.post('/api/v1/auth/logout')
        public_verify = client.get(f'/api/v1/certificates/verify/{cert_code}')
        assert public_verify.status_code == 200
        verify_data = public_verify.get_json()['data']
        assert verify_data['valid'] is True
        assert verify_data['student_name'] == 'Audit Tester'
        print(" [PASS] 12. Public Certificate Verification Portal validated authentic.")

        # 9. Student submits feedback (+5 pts)
        client.post('/api/v1/auth/login', json={'email': email, 'password': 'AuditPassword@123'})
        fb_res = client.post('/api/v1/feedback', json={
            'event_id': event_id,
            'rating': 5,
            'speaker_rating': 5,
            'organization_rating': 5,
            'venue_rating': 5,
            'content': 'Outstanding organization and technical depth!',
            'suggestions': 'Add more hands-on lab sessions.'
        })
        assert fb_res.status_code == 201, f"Feedback submission failed: {fb_res.get_json()}"
        print(" [PASS] 13. Feedback submitted successfully (+5 ITSA points).")

        # 10. Social Feed: Create post, react, comment
        post_res = client.post('/api/v1/posts', data={
            'content': 'Auditing the #ITSA platform! Great job team. #AuditTest'
        })
        assert post_res.status_code == 201
        post_id = post_res.get_json()['data']['id']
        print(f" [PASS] 14. Community post created: ID {post_id} (+2 ITSA points)")

        # React
        react_res = client.post(f'/api/v1/posts/{post_id}/react', json={'reaction_type': 'LOVE'})
        assert react_res.status_code == 200
        print(" [PASS] 15. Post reaction recorded.")

        # Comment
        comm_res = client.post(f'/api/v1/comments/post/{post_id}', json={'content': 'Confirmed operational!'})
        assert comm_res.status_code == 201
        print(" [PASS] 16. Post comment posted (+1 ITSA point).")

        # 11. Gamification check
        pts_res = client.get('/api/v1/points/my')
        assert pts_res.status_code == 200
        pts_data = pts_res.get_json()['data']
        # 3 (reg) + 10 (att) + 5 (fb) + 2 (post) + 1 (comm) = 21 points
        assert pts_data['total_points'] == 21, f"Unexpected points balance: {pts_data['total_points']}"
        print(f" [PASS] 17. ITSA Points ledger verified: exactly {pts_data['total_points']} pts.")

        # 12. Leaderboard
        lb_res = client.get('/api/v1/leaderboard')
        assert lb_res.status_code == 200
        print(" [PASS] 18. Leaderboard API verified.")

        # 13. AI Assistant & Features
        ai_chat = client.post('/api/v1/ai/chat', json={'message': 'What events can I attend?'})
        assert ai_chat.status_code == 200
        assert len(ai_chat.get_json()['data']['reply']) > 0
        print(" [PASS] 19. AI Chatbot assistant response validated.")

        ai_recs = client.get('/api/v1/ai/recommendations')
        assert ai_recs.status_code == 200
        print(" [PASS] 20. AI ML Recommendation engine validated.")

        # 14. Admin operations
        client.post('/api/v1/auth/logout')
        admin_login = client.post('/api/v1/auth/login', json={'email': 'admin@itsa.edu', 'password': 'Admin@12345'})
        assert admin_login.status_code == 200
        print(" [PASS] 21. Admin authenticated.")

        admin_overview = client.get('/api/v1/admin/analytics/overview')
        assert admin_overview.status_code == 200
        metrics = admin_overview.get_json()['data']
        print(f" [PASS] 22. Admin metrics: {metrics['total_students']} students, {metrics['total_events']} events, {metrics['total_attendances']} attendances.")

        # Admin creates coordinator
        coord_create = client.post('/api/v1/admin/coordinators', json={
            'email': f'new_coord_{os.getpid()}@itsa.edu',
            'password': 'CoordPassword@123',
            'full_name': 'New Audit Coordinator',
            'designation': 'Support Lead',
            'department': 'IT'
        })
        assert coord_create.status_code == 201
        print(" [PASS] 23. Admin created new coordinator account.")

        print("==================================================")
        print("ALL 23 CORE WORKFLOWS FULLY AUDITED AND PASSED!")
        print("==================================================")

if __name__ == '__main__':
    run_e2e_audit()

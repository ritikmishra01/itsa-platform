def test_ai_chatbot_response(auth_client_student):
    res = auth_client_student.post('/api/v1/ai/chat', json={'message': 'What events are upcoming?'})
    assert res.status_code == 200
    assert 'reply' in res.get_json()['data']

def test_ai_recommendations(auth_client_student):
    res = auth_client_student.get('/api/v1/ai/recommendations')
    assert res.status_code == 200
    assert isinstance(res.get_json()['data'], list)

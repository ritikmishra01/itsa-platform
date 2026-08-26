def test_create_and_react_post(auth_client_student):
    # Create post
    post_res = auth_client_student.post('/api/v1/posts', data={
        'content': 'Hello #ITSA community! #CodeLife'
    })
    assert post_res.status_code == 201
    post_id = post_res.get_json()['data']['id']

    # React to post
    react_res = auth_client_student.post(f'/api/v1/posts/{post_id}/react', json={'reaction_type': 'LOVE'})
    assert react_res.status_code == 200

    # Add comment
    comm_res = auth_client_student.post(f'/api/v1/comments/post/{post_id}', json={'content': 'Great initiative!'})
    assert comm_res.status_code == 201

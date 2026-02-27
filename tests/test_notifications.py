# Create
# Edit
# Delete
# Query all

def test_add_notification(client):
    r = client.get("/")
    print(r)
    assert r.status_code == 200
    assert r.json() == {"msg": "Hello World!"}


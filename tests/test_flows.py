def test_register_and_duplicate_rejected(client):
    r=client.post("/api/auth/register",json={"email":"uno@example.com","password":"password-larga-123"})
    assert r.status_code==201
    assert r.json()["user"]["role"]=="student"
    assert "password" not in r.json()["user"]
    assert client.post("/api/auth/register",json={"email":"uno@example.com","password":"password-larga-123"}).status_code==409

def test_login_rejects_wrong_password(client):
    client.post("/api/auth/register",json={"email":"dos@example.com","password":"password-larga-123"})
    assert client.post("/api/auth/login",json={"email":"dos@example.com","password":"incorrecta"}).status_code==401
    assert client.post("/api/auth/login",json={"email":"dos@example.com","password":"password-larga-123"}).status_code==200

def test_create_summary_and_delete_expense(client,auth_headers):
    h=auth_headers
    r=client.post("/api/expenses",headers=h,json={"amount":125.5,"currency":"MXN","category":"Comida","note":"almuerzo","spent_on":"2026-10-03"})
    assert r.status_code==201
    assert r.json()["amount"]==125.5
    assert len(client.get("/api/expenses",headers=h).json())==1
    summary=client.get("/api/summary?month=2026-10",headers=h).json()
    assert summary["count"]==1 and summary["totals"]["MXN"]==125.5
    assert client.delete(f"/api/expenses/{r.json()['id']}",headers=h).status_code==204
    assert client.get("/api/summary?month=2026-10",headers=h).json()["count"]==0

def test_users_cannot_read_each_others_expenses(client,auth_headers):
    created=client.post("/api/expenses",headers=auth_headers,json={"amount":20,"category":"Otro","spent_on":"2026-10-02"}).json()
    client.post("/api/auth/register",json={"email":"otra@example.com","password":"password-larga-456"})
    token=client.post("/api/auth/login",json={"email":"otra@example.com","password":"password-larga-456"}).json()["access_token"]
    assert client.delete(f"/api/expenses/{created['id']}",headers={"Authorization":f"Bearer {token}"}).status_code==404

def test_expense_input_validation(client,auth_headers):
    assert client.post("/api/expenses",headers=auth_headers,json={"amount":-1,"category":"Otro"}).status_code==422

def test_private_routes_require_auth(client):
    assert client.get("/api/expenses").status_code==401

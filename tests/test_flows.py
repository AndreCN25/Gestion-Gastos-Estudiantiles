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

from decimal import Decimal


def test_create_summary_and_delete_expense(client,auth_headers):
    h=auth_headers
    r=client.post("/api/expenses",headers=h,json={"amount":125.5,"currency":"MXN","category":"Comida","note":"almuerzo","spent_on":"2026-10-03"})
    assert r.status_code==201
    assert Decimal(str(r.json()["amount"]))==Decimal("125.50")
    assert len(client.get("/api/expenses",headers=h).json())==1
    summary=client.get("/api/summary?month=2026-10",headers=h).json()
    assert summary["count"]==1 and Decimal(str(summary["totals"]["MXN"]))==Decimal("125.50")
    assert client.delete(f"/api/expenses/{r.json()['id']}",headers=h).status_code==204
    assert client.get("/api/summary?month=2026-10",headers=h).json()["count"]==0

def test_users_cannot_read_each_others_expenses(client,auth_headers):
    created=client.post("/api/expenses",headers=auth_headers,json={"amount":20,"category":"Otro","spent_on":"2026-10-02"}).json()
    client.post("/api/auth/register",json={"email":"otra@example.com","password":"password-larga-456"})
    token=client.post("/api/auth/login",json={"email":"otra@example.com","password":"password-larga-456"}).json()["access_token"]
    assert client.delete(f"/api/expenses/{created['id']}",headers={"Authorization":f"Bearer {token}"}).status_code==404

def test_expense_input_validation(client,auth_headers):
    assert client.post("/api/expenses",headers=auth_headers,json={"amount":-1,"category":"Otro"}).status_code==422
    assert client.post("/api/expenses",headers=auth_headers,json={"amount":10.129,"category":"Otro"}).status_code==422
    assert client.post("/api/expenses",headers=auth_headers,json={"amount":10,"currency":"XYZ","category":"Otro"}).status_code==422

def test_invalid_summary_month_returns_validation_error(client,auth_headers):
    assert client.get("/api/summary?month=2026-99",headers=auth_headers).status_code==422
    assert client.get("/api/summary?month=0000-01",headers=auth_headers).status_code==422

def test_private_routes_require_auth(client):
    assert client.get("/api/expenses").status_code==401

def test_admin_role_and_student_restriction(client,auth_headers):
    from app.database import SessionLocal
    from app.models import User
    from app.security import create_token, hash_password
    db=SessionLocal()
    admin=User(email="admin@example.com",password_hash=hash_password("administrador-seguro"),role="admin")
    db.add(admin)
    db.commit()
    db.refresh(admin)
    admin_headers={"Authorization":f"Bearer {create_token(admin)}"}
    db.close()
    assert client.get("/api/admin/summary",headers=admin_headers).status_code==200
    assert client.get("/api/admin/summary",headers=auth_headers).status_code==403

def test_external_integrations_are_called_through_authenticated_routes(client,auth_headers,monkeypatch):
    weather_calls=[]
    async def fake_weather(city=None,latitude=None,longitude=None):
        weather_calls.append((city,latitude,longitude))
        return {"city":city or "Tu ubicación actual","temperature_c":28,"weather_code":1,"condition":"Mayormente despejado"}
    exchange_calls=[]
    async def fake_exchange(source,target):
        exchange_calls.append((source,target))
        return {"date":"2026-10-26","from":source,"to":target,"rate":0.05}
    monkeypatch.setattr("app.main.fetch_weather",fake_weather)
    monkeypatch.setattr("app.main.fetch_exchange",fake_exchange)
    weather=client.get("/api/external/weather?city=Mérida",headers=auth_headers)
    location=client.get("/api/external/weather?latitude=19.4326&longitude=-99.1332",headers=auth_headers)
    exchange=client.get("/api/external/exchange?source=MXN&target=USD",headers=auth_headers)
    assert weather.status_code==200 and weather.json()["temperature_c"]==28
    assert location.status_code==200 and location.json()["city"]=="Tu ubicación actual"
    assert weather_calls==[("Mérida",None,None),(None,19.4326,-99.1332)]
    assert exchange_calls==[("MXN","USD")]
    assert exchange.status_code==200 and exchange.json()["rate"]==0.05

def test_ai_endpoint_has_local_fallback(client,auth_headers,monkeypatch):
    monkeypatch.setattr("app.services.settings.openai_api_key","")
    client.post("/api/expenses",headers=auth_headers,json={"amount":80,"category":"Comida"})
    result=client.post("/api/ai/tips",headers=auth_headers)
    assert result.status_code==200
    assert "Comida" in result.json()["tips"]
    assert "mode" in result.json()
    next_result=client.post("/api/ai/tips",headers=auth_headers,json={"previous_tips":[result.json()["tips"]]})
    assert next_result.status_code==200 and next_result.json()["tips"]!=result.json()["tips"]

def test_generic_saving_tips_change_on_each_request(client,auth_headers,monkeypatch):
    monkeypatch.setattr("app.services.settings.openai_api_key","")
    first=client.post("/api/ai/tips",headers=auth_headers,json={}).json()["tips"]
    second=client.post("/api/ai/tips",headers=auth_headers,json={"previous_tips":[first]}).json()["tips"]
    assert second!=first

def test_web_shell_is_served(client):
    assert client.get("/").status_code==200
    assert client.get("/static/app.js").status_code==200
    assert client.get("/static/manifest.webmanifest").status_code==200
    assert client.get("/static/favicon.svg").status_code==200
    service_worker=client.get("/static/sw.js").text
    assert "SHELL_PATHS.has(url.pathname)" in service_worker
    assert "'/api/expenses'" not in service_worker

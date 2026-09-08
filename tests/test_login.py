import pytest
from fastapi.testclient import TestClient
import os 
import app.database as database
import hashlib
from datetime import datetime,timezone,timedelta
from app.main import app
import app.users as users
@pytest.fixture
def client(monkeypatch):
        database.DATABASE_PATH="test_library_test.db"
        if os.path.exists("test_library_test.db"):
               os.remove("test_library_test.db")
        database.init_db()
        client=TestClient(app)
        monkeypatch.setattr(users,"send_verification_email",lambda email,token:None)
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
                "name":"azouz",
                "email":"azouz@gmail.com",
                "password":"testazouz"
        }
        response=client.post("/users/",json=user)
        assert response.status_code==200
        cursor.execute("UPDATE users SET is_verified=? WHERE email=?",(1,user["email"]))
        conn.commit()
        yield client
        conn.close()
        try:
            if os.path.exists("test_library_test.db"):
                os.remove("test_library_test.db")
        except PermissionError:
               pass
    
def test_login_success(client):
        response=client.post("/users/login",data={"username":"azouz@gmail.com","password":"testazouz"})
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()
def test_refresh_token(client):
        response=client.post("/users/login",data={"username":"azouz@gmail.com","password":"testazouz"})
        refresh_token=response.json()["refresh_token"]
        response_refresh_token=client.post("/users/refresh",params={"refresh_token":refresh_token})
        assert response_refresh_token.status_code == 200
        assert "access_token" in response_refresh_token.json()
        assert "refresh_token" in response_refresh_token.json()
        assert "token_type" in response_refresh_token.json()
        response_refresh_token=client.post("/users/refresh",params={"refresh_token":refresh_token})
        assert response_refresh_token.status_code == 401
def test_refresh_expired_token(client):
        try:
            conn=database.get_connection()
            cursor=conn.cursor()
            response=client.post("/users/login",data={"username":"azouz@gmail.com","password":"testazouz"})
            refresh_token=response.json()["refresh_token"]
            hash_refresh_token=hashlib.sha256(
            refresh_token.encode()
            ).hexdigest()
            time=datetime.isoformat(datetime.now(timezone.utc)-timedelta(hours=1))
            cursor.execute("UPDATE refresh_tokens SET expire_at=? WHERE hash_token=?",(time,hash_refresh_token))
            conn.commit()
            response_refresh_token=client.post("/users/refresh",params={"refresh_token":refresh_token})
            assert response_refresh_token.status_code == 401
        finally:
            conn.close()
def test_revoke_token(client):
        try:
                conn=database.get_connection()
                cursor=conn.cursor()
                response=client.post("/users/login",data={"username":"azouz@gmail.com","password":"testazouz"})
                refresh_token=response.json()["refresh_token"]
                hash_refresh_token=hashlib.sha256(
                refresh_token.encode()
                ).hexdigest()
                cursor.execute("UPDATE refresh_tokens SET revoked=? WHERE hash_token=?",(1,hash_refresh_token))
                conn.commit()
                response_refresh_token=client.post("/users/refresh",params={"refresh_token":refresh_token})
                assert response_refresh_token.status_code == 401
        finally:
                conn.close()
       
def test_refresh_invalid_token(client):
        response=client.post("/users/refresh",params={"refresh_token":"asdkfjasierpaweorjsdjfkawpeoiruisdf"})
        assert response.status_code == 401

def test_login_wrong_password(client):
        response=client.post("/users/login",data={"username":"azouz@gmail.com","password":"testtest"})
        assert response.status_code == 401
def test_login_unknown_email(client):
        response=client.post("/users/login",data={"username":"test@gmail.com","password":"testazouz"})
        assert response.status_code == 401
from fastapi.testclient import TestClient
import pytest
from app.main import app
import os 
import app.database as database
import app.users as users
import hashlib
from datetime import datetime,timezone,timedelta
from app.tokens import create_access_token,SECRET_KEY,ALGORITHM
from jose import jwt
saved_token=[]
def fake_send_verification_email(email,token):
    saved_token.append(token)
reset_token=[]
def fake_send_reset_password(email,token):
    reset_token.append(email)
    reset_token.append(token)
@pytest.fixture
def client(monkeypatch):
    database.DATABASE_PATH="test_library_test.db"
    database.init_db()
    monkeypatch.setattr(users,"send_verification_email",fake_send_verification_email)
    monkeypatch.setattr(users,"send_password_reset_email",fake_send_reset_password)
    yield TestClient(app)
    try:
        os.remove("test_library_test.db")
    except PermissionError:
        pass 
def test_verify_email(client):
    saved_token.clear()
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"test",
            "email":"test@gmail.com",
            "password":"testtest"
        }
        response1=client.post("/users/",json=user)
        assert response1.status_code == 200
        response= client.get("/users/verify-email",params={"token":saved_token[0]})
        assert response.status_code == 200
        cursor.execute("SELECT * FROM users WHERE email=?",(user["email"],))
        row=cursor.fetchone()
        assert row[6] == 1
    finally:
        conn.close()
def test_verify_email_invalid_token(client):
    response=client.get("/users/verify-email",params={"token":"s;lakjdf;ajsd;klfja;ljdsfjadjfla"})
    assert response.status_code == 401
def test_verify_email_expired_token(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"test",
            "email":"test@gmail.com",
            "password":"testtest"
        }
        response1=client.post("/users/",json=user)
        assert response1.status_code == 200
        hash_token=hashlib.sha256(saved_token[0].encode()).hexdigest()
        time=datetime.isoformat(datetime.now(timezone.utc)-timedelta(hours=1))
        cursor.execute("UPDATE email_verifications SET expires_at=? WHERE token_hash=?",(time,hash_token))
        conn.commit()
        response=client.get("/users/verify-email",params={"token":saved_token[0]})
        assert response.status_code == 401
    finally:
        conn.close()
def test_creat_user_duplicate_email(client):
    user={
        "name":"test",
        "email":"test@gmail.com",
        "password":"testtest"
    }
    response1=client.post("/users/",json=user)
    assert response1.status_code == 200
    response2=client.post("/users/",json=user)
    assert response2.status_code == 409
def test_creat_user_invalid_email(client):
    user={
        "name":"test",
        "email":"not-an-email",
        "password":"testtest"
    }
    response=client.post("/users/",json=user)
    assert response.status_code == 422
def test_creat_user_without_row(client):
    user={
        "name":"test",
        "password":"testtest"
    }
    response=client.post("/users/",json=user)
    assert response.status_code == 422
def test_invalid_password(client):
    user={
        "name":"test",
        "email":"test@gmail.com",
        "password":"test"
    }
    response=client.post("/users/",json=user)
    assert response.status_code == 422
def test_forgot_password(client):
    user={
        "name":"test",
        "email":"test@gmail.com",
        "password":"12345678"
    }
    response0=client.post("/users/",json=user)
    assert response0.status_code==200
    response=client.post("/users/forgot-password",params={"email":user["email"]})
    assert response.status_code==200
    assert user["email"] in reset_token
    assert reset_token[1]
@pytest.fixture
def reset_data(client):
    reset_token.clear()
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"test",
            "email":"test@gmail.com",
            "password":"12345678"
        }
        response0=client.post("/users/",json=user)
        assert response0.status_code==200
        cursor.execute("UPDATE users SET is_verified=? WHERE email=?",(1,user["email"]))
        conn.commit()
        response1=client.post('/users/forgot-password',params={"email":user["email"]})
        assert response1.status_code==200
        return user,reset_token[-1]
    finally:
        conn.close()
    
def test_reset_password_success(client,reset_data):
    user,token=reset_data
    response2=client.post("/users/reset-password",params={"token":token,"new_password":"azouzazouz"})
    assert response2.status_code==200
    response3=client.post("/users/login",data={"username":user["email"],"password":"12345678"})
    assert response3.status_code==401
    response4=client.post("/users/login",data={"username":user["email"],"password":"azouzazouz"})
    assert response4.status_code==200
def test_reset_invalid_token(client):
    response1=client.post("/users/reset-password",params={"token":"lskdjhglskdflgjslgjsk","new_password":"azouzazouz"})
    assert response1.status_code==401
def test_reset_expired_token(client,reset_data):
    try:
        user,token=reset_data
        conn=database.get_connection()
        cursor=conn.cursor()
        hash_token=hashlib.sha256(token.encode()).hexdigest()
        time=datetime.isoformat(datetime.now(timezone.utc)-timedelta(hours=1))
        cursor.execute("UPDATE password_resets SET expires_at=? WHERE token_hash=?",(time,hash_token))
        conn.commit()
        response0=client.post("/users/reset-password",params={"token":token,"new_password":"azouzazouz"})
        assert response0.status_code==401
    finally:
        conn.close()
def test_reset_password_reuesd_token(client,reset_data):
    user,token=reset_data
    response=client.post("/users/reset-password",params={"token":token,"new_password":"azouzazouz"})
    assert response.status_code==200
    response0=client.post("/users/reset-password",params={"token":token, "new_password":"abdoabdo"})
    assert response0.status_code==401
def test_forgot_password_user_not_found(client):
    response=client.post("/users/forgot-password",params={"email":"azouz@gmail.com"})
    assert response.status_code==401
def test_read_user_id(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"tset",
            "email":"test@gmail.com",
            "password":"12345678"
        }
        response1=client.post("/users/",json=user)
        assert response1.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user["email"],))
        user_id=cursor.fetchone()[0]
        response2=client.get(f"/users/user/{user_id}")
        assert response2.status_code==200
    finally:
        conn.close()
def test_read_user_id_not_found(client):
    response=client.get(f"/users/user/{9999999}")
    assert response.status_code==404
def test_update_user(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"test",
            "email":"test@gmail.com",
            "password":"12345678"
        }
        response1=client.post("/users/",json=user)
        assert response1.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user["email"],))
        user_id=cursor.fetchone()[0]
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        response2=client.put(f"/users/user/{user_id}",json={"name":"updated_name"},headers=headers)
        assert response2.status_code==403
    finally:
        conn.close()

def test_update_user_admin(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"test",
            "email":"test@gmail.com",
            "password":"123456789"
        }
        response1=client.post("/users/",json=user)
        assert response1.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user["email"],))
        user_id=cursor.fetchone()[0]
        cursor.execute("UPDATE users SET role=? WHERE id=?",("admin",user_id))
        conn.commit()
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        response2=client.put(f"/users/user/{user_id}",json={"name":"updated_name"},headers=headers)
        assert response2.status_code==200
    finally:
        conn.close()
def test_delete_user(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"test",
            "email":"test@gmail.com",
            "password":"12345678"
        }
        response1=client.post("/users/",json=user)
        assert response1.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user["email"],))
        user_id=cursor.fetchone()[0]
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        response2=client.delete(f"/users/user/{user_id}",headers=headers)
        assert response2.status_code==403
    finally:
        conn.close()
def test_delete_user_admin(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"test",
            "email":"test@gmail.com",
            "password":"123456789"
        }
        response1=client.post("/users/",json=user)
        assert response1.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user["email"],))
        user_id=cursor.fetchone()[0]
        cursor.execute("UPDATE users SET role=? WHERE id=?",("admin",user_id))
        conn.commit()
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        response2=client.delete(f"/users/user/{user_id}",headers=headers)
        assert response2.status_code==200
    finally:
        conn.close()
def test_delete_user_not_found(client):
    token=create_access_token(data={"sub":str(9999999)})
    headers={"Authorization":f"Bearer {token}"}
    response=client.delete(f"/users/user/{9999999}",headers=headers)
    assert response.status_code==404
def test_get_me(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"test",
            "email":"test@gmail.com",
            "password":"123456789"
        }
        response1=client.post("/users/",json=user)
        assert response1.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user["email"],))
        user_id=cursor.fetchone()[0]
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        response2=client.get("/users/me",headers=headers)
        assert response2.status_code==200
    finally:
        conn.close()
def test_get_me_invalid_token(client):
    headers={"Authorization":"Bearer invalid_token"}
    response=client.get("/users/me",headers=headers)
    assert response.status_code==401
def test_get_me_expired_token(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"test",
            "email":"test@gamil.com",
            "password":"123456789"
        }
        response1=client.post("/users/",json=user)
        assert response1.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user["email"],))
        user_id=cursor.fetchone()[0]
        expire_time=datetime.now(timezone.utc)-timedelta(hours=1)
        to_encode={"sub":str(user_id),"exp":expire_time,"token_type":"access"}
        token=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
        headers={"Authorization":f"Bearer {token}"}
        response2=client.get("/users/me",headers=headers)
        assert response2.status_code==401
    finally:
        conn.close()



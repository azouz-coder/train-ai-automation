from fastapi.testclient import TestClient
import os
import app.database as database
import pytest
from app.main import app
from app.tokens import create_access_token
import app.users as users
@pytest.fixture
def client(monkeypatch):
    database.DATABASE_PATH="test_library_test.db"
    if os.path.exists("test_library_test.db"):
        os.remove("test_library_test.db")
    database.init_db()
    monkeypatch.setattr(users,"send_verification_email",lambda email,token:None)
    yield TestClient(app)
    try:   
        if os.path.exists("test_library_test.db"):
            os.remove("test_library_test.db")
    except PermissionError:
        pass

def test_create_book_admin(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        book={
            "isbn":"10000",
            "title":"Test Book",
            "author":"Test Author"
        }
        user={
            "name":"test",
            "email":"test@example.com",
            "password":"testpassword"
        }
        response=client.post("/users/",json=user)
        assert response.status_code==200
        cursor.execute("UPDATE users SET role=? WHERE email=?",("admin",user["email"]))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE email=?",(user["email"],))
        row=cursor.fetchone()
        token=create_access_token(data={"sub":str(row[0])})
        headers={"Authorization":f"Bearer {token}"}
        response0=client.post("/books/",json=book,headers=headers)
        assert response0.status_code==200
    finally:
        conn.close()
def test_create_book(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        book={
            "isbn":"1000",
            "title":"Test Book",
            "author":"Test Author"
        }
        user={
            "name":"Test",
            "email":"test@example.com",
            "password":"123456789"
        }
        response=client.post("/users/",json=user)
        assert response.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user["email"],))
        user_id=cursor.fetchone()[0]
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        response0=client.post("/books/",json=book,headers=headers)
        assert response0.status_code==403
    finally:
        conn.close()
def test_create_with_the_same_isbn(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        book={
            "isbn":"10000",
            "title":"Test Book",
            "author":"Test Author"
        }
        user={
            "name":"test",
            "email":"test@example.com",
            "password":"testpassword"
        }
        response=client.post("/users/",json=user)
        assert response.status_code==200
        cursor.execute("UPDATE users SET role=? WHERE email=?",("admin",user["email"]))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE email=?",(user["email"],))
        row=cursor.fetchone()
        token=create_access_token(data={"sub":str(row[0])})
        headers={"Authorization":f"Bearer {token}"}
        response0=client.post("/books/",json=book,headers=headers)
        assert response0.status_code==200
        response1=client.post("/books/",json=book,headers=headers)
        assert response1.status_code==409
    finally:
        conn.close()
def test_read_book(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        book={
            "isbn":"10000",
            "title":"Test Book",
            "author":"Test Author"
        }
        user={
            "name":"test",
            "email":"test@example.com",
            "password":"testpassword"
        }
        response=client.post("/users/",json=user)
        assert response.status_code==200
        cursor.execute("UPDATE users SET role=? WHERE email=?",("admin",user["email"]))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE email=?",(user["email"],))
        row=cursor.fetchone()
        token=create_access_token(data={"sub":str(row[0])})
        headers={"Authorization":f"Bearer {token}"}
        response0=client.post("/books/",json=book,headers=headers)
        assert response0.status_code==200
        isbn=book["isbn"]
        response1=client.get(f"/books/{isbn}")
        assert response1.status_code==200
        data=response1.json()
        assert data["isbn"]==book["isbn"]
        assert data["title"]==book["title"]
        assert data["author"]==book["author"]
    finally:
        conn.close()
def test_read_book_not_found(client):
    response=client.get(f"/books/{1}")
    assert response.status_code==404
def test_search_with_isbn_author_title(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        book1={
            "isbn":"10000",
            "title":"Test Book",
            "author":"Test Author"
        }
        book2={
            "isbn":"10001",
            "title":"Clean Code",
            "author":"python API"
        }
        book3={
            "isbn":"10002",
            "title":"Clean Test",
            "author":"python test"
        }
        user={
            "name":"test",
            "email":"test@example.com",
            "password":"testpassword"
        }
        response=client.post("/users/",json=user)
        assert response.status_code==200
        cursor.execute("UPDATE users SET role=? WHERE email=?",("admin",user["email"]))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE email=?",(user["email"],))
        row=cursor.fetchone()
        token=create_access_token(data={"sub":str(row[0])})
        headers={"Authorization":f"Bearer {token}"}
        response1=client.post("/books/",json=book1,headers=headers)
        assert response1.status_code==200
        response2=client.post("/books/",json=book2,headers=headers)
        assert response2.status_code==200
        response3=client.post("/books/",json=book3,headers=headers)
        assert response3.status_code==200
        response4=client.get("/books/?search=python")
        assert response4.status_code==200
        data=response4.json()
        assert len(data["items"])==2
        assert data["items"][0]["isbn"]=="10001"
        assert data["items"][1]["isbn"]=="10002"
        response5=client.get("/books/?search=Test")
        data=response5.json()
        assert response5.status_code==200
        assert len(data["items"])==2
        assert data["items"][0]["isbn"]=="10002"
        assert data["items"][1]["isbn"]=="10000"
        response6=client.get("/books/?search=10000")
        assert response6.status_code==200
        data=response6.json()
        assert len(data["items"])==1
        assert data["items"][0]["isbn"]=="10000"

    finally:
        conn.close()
def test_updated_book_admin(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        book={
            "isbn":"1000",
            "title":"Test Book",
            "author":"Test Author"
        }
        user={
            "name":"Test",
            "email":"test@example.com",
            "password":"123456789"
        }
        response=client.post("/users/",json=user)
        assert response.status_code==200
        cursor.execute("UPDATE users SET role=? WHERE email=?",("admin",user["email"]))
        conn.commit()
        cursor.execute("SELECT id FROM users WHERE email=?",(user["email"],))
        user_id=cursor.fetchone()[0]
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        response0=client.post("/books/",json=book,headers=headers)
        assert response0.status_code==200
        response1=client.put(f"/books/1000",json={"title":"Test Updatbook","author":"Testupdate"},headers=headers)
        assert response1.status_code==200
        response2=client.get("/books/1000")
        assert response2.status_code==200
        data=response2.json()
        assert data["title"]=="Test Updatbook"
        assert data["author"]=="Testupdate"


    finally:
        conn.close()
def test_updated_book_not_found(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"Test",
            "email":"test@example.com",
            "password":"123456789"
        }
        response=client.post("/users/",json=user)
        assert response.status_code==200
        cursor.execute("UPDATE users SET role=? WHERE email=?",("admin",user["email"]))
        conn.commit()
        cursor.execute("SELECT id FROM users WHERE email=?",(user["email"],))
        user_id=cursor.fetchone()[0]
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        response=client.put("/books/1000",json={"title":"fialed","author":"fialed"},headers=headers)
        assert response.status_code==404
    finally:
        conn.close()
def test_updated_book_user(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"Test",
            "email":"test@example.com",
            "password":"123456789"
        }
        response=client.post("/users/",json=user)
        assert response.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user["email"],))
        user_id=cursor.fetchone()[0]
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        response1=client.put("/books/1000",json={"title":"test","author":"test"},headers=headers)
        assert response1.status_code==403
    finally:
        conn.close()
def test_delete_book_admin(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        book={
            "isbn":"10000",
            "title":"Test Book",
            "author":"Test Author"
        }
        user={
            "name":"test",
            "email":"test@example.com",
            "password":"testpassword"
        }
        response=client.post("/users/",json=user)
        assert response.status_code==200
        cursor.execute("UPDATE users SET role=? WHERE email=?",("admin",user["email"]))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE email=?",(user["email"],))
        row=cursor.fetchone()
        token=create_access_token(data={"sub":str(row[0])})
        headers={"Authorization":f"Bearer {token}"}
        response0=client.post("/books/",json=book,headers=headers)
        assert response0.status_code==200
        response1=client.delete("/books/10000",headers=headers)
        assert response1.status_code==200
        response2=client.get("/books/10000")
        assert response2.status_code==404
    finally:
        conn.close()
def test_delete_book_not_found(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"Test",
            "email":"test@example.com",
            "password":"123456789"
        }
        response=client.post("/users/",json=user)
        assert response.status_code==200
        cursor.execute("UPDATE users SET role=? WHERE email=?",("admin",user["email"]))
        conn.commit()
        cursor.execute("SELECT id FROM users WHERE email=?",(user["email"],))
        user_id=cursor.fetchone()[0]
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        response=client.delete("/books/1000",headers=headers)
        assert response.status_code==404
    finally:
        conn.close()
def test_delet_book_user(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"Test",
            "email":"test@example.com",
            "password":"123456789"
        }
        response=client.post("/users/",json=user)
        assert response.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user["email"],))
        user_id=cursor.fetchone()[0]
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        response1=client.delete("/books/1000",headers=headers)
        assert response1.status_code==403
    finally:
        conn.close()
def test_pagination(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        book1={
            "isbn":"10000",
            "title":"Test Book",
            "author":"Test Author"
        }
        book2={
            "isbn":"10001",
            "title":"Clean Code",
            "author":"python API"
        }
        book3={
            "isbn":"10002",
            "title":"Clean Test",
            "author":"python test"
        }
        user={
            "name":"test",
            "email":"test@example.com",
            "password":"testpassword"
        }
        response=client.post("/users/",json=user)
        assert response.status_code==200
        cursor.execute("UPDATE users SET role=? WHERE email=?",("admin",user["email"]))
        conn.commit()
        cursor.execute("SELECT * FROM users WHERE email=?",(user["email"],))
        row=cursor.fetchone()
        token=create_access_token(data={"sub":str(row[0])})
        headers={"Authorization":f"Bearer {token}"}
        response1=client.post("/books/",json=book1,headers=headers)
        assert response1.status_code==200
        response2=client.post("/books/",json=book2,headers=headers)
        assert response2.status_code==200
        response3=client.post("/books/",json=book3,headers=headers)
        assert response3.status_code==200
        response4=client.get("/books/?limit=1&offset=1")
        assert response4.status_code==200
        data=response4.json()
        assert data["items"][0]["isbn"]=="10002"
    finally:
        conn.close()
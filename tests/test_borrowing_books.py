import pytest
import os
from fastapi.testclient import TestClient
import app.database as database
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
def test_borrowing_book(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"azouz",
            "email":"testborrow@gamil.com",
            "password":"test12345"
        }
        book={
            "isbn":"1234",
            "title":"borrowin",
            "author":"azouz"
        }
        resoponse_1=client.post("/users/",json=user)
        assert resoponse_1.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user['email'],))
        user_id=cursor.fetchone()[0]
        cursor.execute('UPDATE users SET role=? WHERE id=?',("admin",user_id))
        conn.commit()
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        resoponse_2=client.post("/books/",json=book,headers=headers)
        assert resoponse_2.status_code==200
        resoponse_3=client.post("/borrowing/",json={"isbn":book["isbn"],"user_id":user_id},headers=headers)
        assert resoponse_3.status_code==200
    finally:
        conn.close()
def test_borrowing_book_not_found(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"azouz",
            "email":"testborrow@gamil.com",
            "password":"test12345"
        }
        resoponse_1=client.post("/users/",json=user)
        assert resoponse_1.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user['email'],))
        user_id=cursor.fetchone()[0]
        cursor.execute('UPDATE users SET role=? WHERE id=?',("admin",user_id))
        conn.commit()
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}

        resoponse_3=client.post("/borrowing/",json={"isbn":"222222","user_id":user_id},headers=headers)
        assert resoponse_3.status_code==404
    finally:
        conn.close()
def test_borrowing_book_borrowed(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"azouz",
            "email":"testborrow@gamil.com",
            "password":"test12345"
        }
        book={
            "isbn":"1234",
            "title":"borrowin",
            "author":"azouz"
        }
        resoponse_1=client.post("/users/",json=user)
        assert resoponse_1.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user['email'],))
        user_id=cursor.fetchone()[0]
        cursor.execute('UPDATE users SET role=? WHERE id=?',("admin",user_id))
        conn.commit()
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        resoponse_2=client.post("/books/",json=book,headers=headers)
        assert resoponse_2.status_code==200
        resoponse_3=client.post("/borrowing/",json={"isbn":book["isbn"],"user_id":user_id},headers=headers)
        assert resoponse_3.status_code==200
        resoponse_4=client.post("/borrowing/",json={"isbn":book["isbn"],"user_id":user_id},headers=headers)
        assert resoponse_4.status_code==409
    finally:
        conn.close()
def test_return_book_not_borrowed(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"azouz",
            "email":"testborrowing@gamil.com",
            "password":"test12345"
        }
        book={
            "isbn":"1234",
            "title":"borrowin",
            "author":"azouz"
        }
        resoponse_1=client.post("/users/",json=user)
        assert resoponse_1.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user['email'],))
        user_id=cursor.fetchone()[0]
        cursor.execute('UPDATE users SET role=? WHERE id=?',("admin",user_id))
        conn.commit()
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        resoponse_2=client.post("/books/",json=book,headers=headers)
        assert resoponse_2.status_code==200
        resoponse_3=client.put("/borrowing/",params={"isbn":book["isbn"],"user_id":user_id},headers=headers)
        assert resoponse_3.status_code==404
    finally:
        conn.close()

def test_return_book_borrowed(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"azouz",
            "email":"testborrow@gamil.com",
            "password":"test12345"
        }
        book={
            "isbn":"1234",
            "title":"borrowin",
            "author":"azouz"
        }
        resoponse_1=client.post("/users/",json=user)
        assert resoponse_1.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user['email'],))
        user_id=cursor.fetchone()[0]
        cursor.execute('UPDATE users SET role=? WHERE id=?',("admin",user_id))
        conn.commit()
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        resoponse_2=client.post("/books/",json=book,headers=headers)
        assert resoponse_2.status_code==200
        resoponse_3=client.post("/borrowing/",json={"isbn":book["isbn"],"user_id":user_id},headers=headers)
        assert resoponse_3.status_code==200
        resoponse_4=client.put("/borrowing/",params={"isbn":book["isbn"],"user_id":user_id},headers=headers)
        assert resoponse_4.status_code==200
        cursor.execute("SELECT * FROM borrowing WHERE user_id=?",(user_id,))
        row=cursor.fetchone()
        returned_at=row[4]
        assert returned_at is not None
    finally:
        conn.close()
def test_borrowing_book_user_not_found(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"azouz",
            "email":"testborrow@gamil.com",
            "password":"test12345"
        }
        book={
            "isbn":"1234",
            "title":"borrowin",
            "author":"azouz"
        }
        resoponse_1=client.post("/users/",json=user)
        assert resoponse_1.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user['email'],))
        user_id=cursor.fetchone()[0]
        cursor.execute('UPDATE users SET role=? WHERE id=?',("admin",user_id))
        conn.commit()
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        resoponse_2=client.post("/books/",json=book,headers=headers)
        assert resoponse_2.status_code==200
        resoponse_3=client.post("/borrowing/",json={"isbn":book["isbn"],"user_id":22222},headers=headers)
        assert resoponse_3.status_code==404
    finally:
        conn.close()
def test_return_book_user_not_found(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"azouz",
            "email":"testborrow@gamil.com",
            "password":"test12345"
        }
        book={
            "isbn":"1234",
            "title":"borrowin",
            "author":"azouz"
        }
        resoponse_1=client.post("/users/",json=user)
        assert resoponse_1.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user['email'],))
        user_id=cursor.fetchone()[0]
        cursor.execute('UPDATE users SET role=? WHERE id=?',("admin",user_id))
        conn.commit()
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        resoponse_2=client.post("/books/",json=book,headers=headers)
        assert resoponse_2.status_code==200
        resoponse_3=client.post("/borrowing/",json={"isbn":book["isbn"],"user_id":user_id},headers=headers)
        assert resoponse_3.status_code==200
        resoponse_4=client.put("/borrowing/",params={"isbn":book["isbn"],"user_id":2222},headers=headers)
        assert resoponse_4.status_code==404
    finally:
        conn.close()
def test_delete_borrowing_not_returned(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"azouz",
            "email":"testborrow@gamil.com",
            "password":"test12345"
        }
        book={
            "isbn":"1234",
            "title":"borrowin",
            "author":"azouz"
        }
        resoponse_1=client.post("/users/",json=user)
        assert resoponse_1.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user['email'],))
        user_id=cursor.fetchone()[0]
        cursor.execute('UPDATE users SET role=? WHERE id=?',("admin",user_id))
        conn.commit()
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        resoponse_2=client.post("/books/",json=book,headers=headers)
        assert resoponse_2.status_code==200
        resoponse_3=client.post("/borrowing/",json={"isbn":book["isbn"],"user_id":user_id},headers=headers)
        assert resoponse_3.status_code==200
        cursor.execute("SELECT * FROM borrowing WHERE user_id=?",(user_id,))
        row=cursor.fetchone()
        resoponse_4=client.delete(f"/borrowing/{row[0]}")
        assert resoponse_4.status_code==409
    finally:
        conn.close()
def test_delete_borrowing_retuned(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"azouz",
            "email":"testborrow@gamil.com",
            "password":"test12345"
        }
        book={
            "isbn":"1234",
            "title":"borrowin",
            "author":"azouz"
        }
        resoponse_1=client.post("/users/",json=user)
        assert resoponse_1.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user['email'],))
        user_id=cursor.fetchone()[0]
        cursor.execute('UPDATE users SET role=? WHERE id=?',("admin",user_id))
        conn.commit()
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        resoponse_2=client.post("/books/",json=book,headers=headers)
        assert resoponse_2.status_code==200
        resoponse_3=client.post("/borrowing/",json={"isbn":book["isbn"],"user_id":user_id},headers=headers)
        assert resoponse_3.status_code==200
        
        cursor.execute("SELECT * FROM borrowing WHERE user_id=?",(user_id,))
        row=cursor.fetchone()
        resoponse_4=client.put("/borrowing/",params={"isbn":book["isbn"],'user_id':user_id},headers=headers)
        assert resoponse_4.status_code==200
        resoponse_5=client.delete(f"/borrowing/{row[0]}")
        assert resoponse_5.status_code==200
        cursor.execute("SELECT * FROM borrowing WHERE id=?",(row[0],))
        delete_row=cursor.fetchone()
        assert delete_row is None
    finally:
        conn.close()
def test_read_all_borrowing(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"azouz",
            "email":"testborrow@gamil.com",
            "password":"test12345"
        }
        book={
            "isbn":"1234",
            "title":"borrowin",
            "author":"azouz"
        }
        resoponse_1=client.post("/users/",json=user)
        assert resoponse_1.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user['email'],))
        user_id=cursor.fetchone()[0]
        cursor.execute('UPDATE users SET role=? WHERE id=?',("admin",user_id))
        conn.commit()
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        resoponse_2=client.post("/books/",json=book,headers=headers)
        assert resoponse_2.status_code==200
        resoponse_3=client.post("/borrowing/",json={"isbn":book["isbn"],"user_id":user_id},headers=headers)
        assert resoponse_3.status_code==200
        resoponse_4=client.get("/borrowing/borrow")
        assert resoponse_4.status_code==200
        data=resoponse_4.json()
        assert "azouz" == data[0]["name"]
    finally:
        conn.close()
def test_read_all_borrowing_not_found(client):
    resoponse=client.get("/borrowing/borrow")
    assert resoponse.status_code==404
def test_read_brrowed_found(client):
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        user={
            "name":"azouz",
            "email":"testborrow@gamil.com",
            "password":"test12345"
        }
        book={
            "isbn":"1234",
            "title":"borrowin",
            "author":"azouz"
        }
        resoponse_1=client.post("/users/",json=user)
        assert resoponse_1.status_code==200
        cursor.execute("SELECT id FROM users WHERE email=?",(user['email'],))
        user_id=cursor.fetchone()[0]
        cursor.execute('UPDATE users SET role=? WHERE id=?',("admin",user_id))
        conn.commit()
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"Bearer {token}"}
        resoponse_2=client.post("/books/",json=book,headers=headers)
        assert resoponse_2.status_code==200
        resoponse_3=client.post("/borrowing/",json={"isbn":book["isbn"],"user_id":user_id},headers=headers)
        assert resoponse_3.status_code==200
        cursor.execute("SELECT * FROM borrowing WHERE user_id=?",(user_id,))
        row=cursor.fetchone()
        resoponse_4=client.get(f"/borrowing/{row[0]}")
        assert resoponse_4.status_code==200
        data=resoponse_4.json()
        assert "azouz" == data["name"]
    finally:
        conn.close()
def test_read_borrowed_not_found(client):
    resoponse=client.get(f"/borrowing/{34}")
    assert resoponse.status_code==404


        
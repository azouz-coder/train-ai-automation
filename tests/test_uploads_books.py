import pytest
import os
import app.database as database
from app.main import app
from fastapi.testclient import TestClient
from app.tokens import create_access_token
import app.book as book
import app.users as users
@pytest.fixture
def client(monkeypatch,tmp_path):
    database.DATABASE_PATH=str(tmp_path/"test_library_test.db")
    database.init_db()
    monkeypatch.setattr(users,"send_verification_email",lambda email,token:None)
    yield TestClient(app)
    try:
        if os.path.exists("test_library_test.db"):
            os.remove("test_library_test.db")
    except PermissionError:
        pass

def test_upload_file(client):
    conn=None
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        book={
            "isbn":"10012",
            "title":"testupload",
            "author":"testone"
        }
        user={
            "name":"testing",
            "email":"upload@gamil.com",
            "password":"test1234"
        }
        isbn=book["isbn"]
        response_1=client.post("/users/",json=user)
        assert response_1.status_code==200
        cursor.execute("UPDATE users SET role=? WHERE email=?",("admin",user["email"]))
        conn.commit()
        cursor.execute("SELECT id FROM users WHERE email=?",(user["email"],))
        user_id=cursor.fetchone()[0]
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"bearer {token}"}
        response_2=client.post("/books/",json=book,headers=headers)
        assert response_2.status_code==200
        with open("test_image.png","rb") as f:
            content=f.read()
      
        response_3=client.post(f"/books/{isbn}/uploads",files={
            "file":(
                "test.png",
                content,
                "image/png"
            )
        })
       
        assert response_3.status_code==200
    finally:
            if conn is not None:
                conn.close()
def test_image_not_true(client):
    conn=None
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        book={
            "isbn":"10012",
            "title":"testupload",
            "author":"testone"
        }
        user={
            "name":"testing",
            "email":"upload@gamil.com",
            "password":"test1234"
        }
        isbn=book["isbn"]
        response_1=client.post("/users/",json=user)
        assert response_1.status_code==200
        cursor.execute("UPDATE users SET role=? WHERE email=?",("admin",user["email"]))
        conn.commit()
        cursor.execute("SELECT id FROM users WHERE email=?",(user["email"],))
        user_id=cursor.fetchone()[0]
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"bearer {token}"}
        response_2=client.post("/books/",json=book,headers=headers)
        assert response_2.status_code==200
        with open("test_image.png","rb") as f:
            content=b"this is not real image png" + f.read()
        response_3=client.post(f"/books/{isbn}/uploads",files={
            "file":(
                "test.png",
                content,
                "image/png"
            )
        })
        assert response_3.status_code==415
    finally:
      if conn is not None:
        conn.close()
def test_file_too_big(client):
    conn=None
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        book_1={
            "isbn":"10012",
            "title":"testupload",
            "author":"testone"
        }
        user={
            "name":"testing",
            "email":"upload@gamil.com",
            "password":"test1234"
        }
        isbn=book_1["isbn"]
        response_1=client.post("/users/",json=user)
        assert response_1.status_code==200
        cursor.execute("UPDATE users SET role=? WHERE email=?",("admin",user["email"]))
        conn.commit()
        cursor.execute("SELECT id FROM users WHERE email=?",(user["email"],))
        user_id=cursor.fetchone()[0]
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"bearer {token}"}
        response_2=client.post("/books/",json=book_1,headers=headers)
        assert response_2.status_code==200
        with open("large_file.png","wb") as f:
            f.write(b"a"*(8*1024)*1024)
        with open("large_file.png","rb") as f:
            content=b"\x89PNG\r\n\x1a\n"+f.read()
        response_3=client.post(f"/books/{isbn}/uploads",files={
            "file":(
                "large_file.png",
                content,
                "image/png"
            )
        })
        assert response_3.status_code==413
    finally:
        if conn is not None:
            conn.close()
def test_isbn_not_found(client):
    with open("test_image.png","rb") as f:
        content=f.read()
    response=client.post(f"/books/{9999999}/uploads",files={
        "file":(
            "test.png",
            content,
            "image/png"
        )
    })
    assert response.status_code==404
def test_upload_fialed_database(client,monkeypatch):
    conn=None
    try:
        conn=database.get_connection()
        cursor=conn.cursor()
        class FakeCursor:
            def __init__(self,real_cursor):
                self.real_cursor=real_cursor
            def execute(self,query,params=None):
                if "UPDATE books SET image_path" in query:
                    raise Exception("Database Error")
                return self.real_cursor.execute(query,params)
            def __getattr__(self, name):
                return getattr(self.real_cursor,name)
           
        class FakeConnection:
            def __init__(self,real_conn):
                self.real_conn=real_conn
            def cursor(self):
                return FakeCursor(self.real_conn.cursor())
            def close(self):
                self.real_conn.close()
        def fake_get_connection():
            return FakeConnection(conn)
        monkeypatch.setattr(book,"get_connection",fake_get_connection)
    
        book_1={
            "isbn":"10012",
            "title":"testupload",
            "author":"testone"
        }
        user={
            "name":"testing",
            "email":"upload@gamil.com",
            "password":"test1234"
        }
        isbn=book_1["isbn"]
        response_1=client.post("/users/",json=user)
        assert response_1.status_code==200
        cursor.execute("UPDATE users SET role=? WHERE email=?",("admin",user["email"]))
        conn.commit()
        cursor.execute("SELECT id FROM users WHERE email=?",(user["email"],))
        user_id=cursor.fetchone()[0]
        token=create_access_token(data={"sub":str(user_id)})
        headers={"Authorization":f"bearer {token}"}
        response_2=client.post("/books/",json=book_1,headers=headers)
        assert response_2.status_code==200
        files_before=set(os.listdir("uploads"))
        with open("test_image.png","rb") as f:
            content=f.read()
      
        response_3=client.post(f"/books/{isbn}/uploads",files={
            "file":(
                "test.png",
                content,
                "image/png"
            )
        })
       
        assert response_3.status_code==500
        files_after=set(os.listdir("uploads"))
        assert files_after==files_before
    
    finally:
        if conn is not None:
            conn.close()
        
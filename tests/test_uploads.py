import os

import pytest
from fastapi.testclient import TestClient

import app.database as database
import app.users as users
from app.main import app
from app.tokens import create_access_token


@pytest.fixture
def client(monkeypatch, tmp_path):
    database.DATABASE_PATH = str(tmp_path / "test_library_test.db")

    database.init_db()

    monkeypatch.setattr(
        users,
        "send_verification_email",
        lambda email, token: None
    )

    yield TestClient(app)


def create_test_user():
    conn = None

    try:
        conn = database.get_connection()
        cursor = conn.cursor()

        user = {
            "name": "test",
            "email": "upload@gmail.com",
            "password": "testupload"
        }

        # إنشاء المستخدم
        cursor.execute(
            """
            INSERT INTO users
            (name, email, password, role, is_verified)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user["name"],
                user["email"],
                user["password"],
                "user",
                1
            )
        )

        conn.commit()

        # الحصول على user_id
        cursor.execute(
            "SELECT id FROM users WHERE email=?",
            (user["email"],)
        )

        user_id = cursor.fetchone()[0]

        # تحويل المستخدم إلى admin
        cursor.execute(
            "UPDATE users SET role=? WHERE id=?",
            ("admin", user_id)
        )

        conn.commit()

        # إنشاء Token
        token = create_access_token(
            data={"sub": str(user_id)}
        )

        headers = {
            "Authorization": f"bearer {token}"
        }

        return user_id, headers

    finally:
        if conn is not None:
            conn.close()


def test_upload_jpg(client):
    user_id, headers = create_test_user()

    with open("test_image.jpg", "rb") as f:
        content = f.read()

    response = client.post(
        f"/users/user/{user_id}/avatars",
        files={
            "file": (
                "test.jpg",
                content,
                "image/jpeg"
            )
        },
        headers=headers
    )

    assert response.status_code == 200

    conn = None

    try:
        conn = database.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT image_profile FROM users WHERE id=?",
            (user_id,)
        )

        row = cursor.fetchone()

        assert row[0] is not None

    finally:
        if conn is not None:
            conn.close()


def test_upload_png(client):
    user_id, headers = create_test_user()

    with open("test_image.png", "rb") as f:
        content = f.read()

    response = client.post(
        f"/users/user/{user_id}/avatars",
        files={
            "file": (
                "test.png",
                content,
                "image/png"
            )
        },
        headers=headers
    )

    assert response.status_code == 200

    conn = None

    try:
        conn = database.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT image_profile FROM users WHERE id=?",
            (user_id,)
        )

        row = cursor.fetchone()

        assert row[0] is not None

    finally:
        if conn is not None:
            conn.close()


def test_upload_invalid_type(client):
    user_id, headers = create_test_user()

    with open("test_image.ico", "rb") as f:
        content = f.read()

    response = client.post(
        f"/users/user/{user_id}/avatars",
        files={
            "file": (
                "test.ico",
                content,
                "image/x-icon"
            )
        },
        headers=headers
    )

    assert response.status_code == 415


def test_upload_fake_jpeg(client):
    user_id, headers = create_test_user()

    with open("test_image.jpg", "rb") as f:
        content = b"fakejpeg" + f.read()

    response = client.post(
        f"/users/user/{user_id}/avatars",
        files={
            "file": (
                "test.jpg",
                content,
                "image/jpeg"
            )
        },
        headers=headers
    )

    assert response.status_code == 415


def test_upload_too_large_file(client):
    user_id, headers = create_test_user()

    content = (
        b"\x89PNG\r\n\x1a\n"
        + os.urandom((2 * 1024) * 1024 + 1)
    )

    response = client.post(
        f"/users/user/{user_id}/avatars",
        files={
            "file": (
                "test_image_large.png",
                content,
                "image/png"
            )
        },
        headers=headers
    )

    assert response.status_code == 413


def test_upload_user_not_found(client):
    _, headers = create_test_user()

    with open("test_image.jpg", "rb") as f:
        content = f.read()

    user_id = 9999

    response = client.post(
        f"/users/user/{user_id}/avatars",
        files={
            "file": (
                "test.jpg",
                content,
                "image/jpeg"
            )
        },
        headers=headers
    )

    assert response.status_code == 404


def test_upload_file_exists(client):
    user_id, headers = create_test_user()

    with open("test_image.jpg", "rb") as f:
        content = f.read()

    response = client.post(
        f"/users/user/{user_id}/avatars",
        files={
            "file": (
                "test.jpg",
                content,
                "image/jpeg"
            )
        },
        headers=headers
    )

    assert response.status_code == 200

    conn = None

    try:
        conn = database.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT image_profile FROM users WHERE id=?",
            (user_id,)
        )

        row = cursor.fetchone()

        path = row[0]

        assert os.path.exists(path)

    finally:
        if conn is not None:
            conn.close()


def test_upload_file_remove_old_file(client):
    user_id, headers = create_test_user()

    with open("carbon (49).png", "rb") as f:
        content = f.read()

    response1 = client.post(
        f"/users/user/{user_id}/avatars",
        files={
            "file": (
                "carbon (49).png",
                content,
                "image/png"
            )
        },
        headers=headers
    )

    assert response1.status_code == 200

    conn = None

    try:
        conn = database.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT image_profile FROM users WHERE id=?",
            (user_id,)
        )

        old_image_path = cursor.fetchone()[0]

    finally:
        if conn is not None:
            conn.close()

    with open("watsup.jpeg", "rb") as f:
        content = f.read()

    response2 = client.post(
        f"/users/user/{user_id}/avatars",
        files={
            "file": (
                "watsup.jpeg",
                content,
                "image/jpeg"
            )
        },
        headers=headers
    )

    assert response2.status_code == 200

    conn = None

    try:
        conn = database.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT image_profile FROM users WHERE id=?",
            (user_id,)
        )

        new_image_path = cursor.fetchone()[0]

    finally:
        if conn is not None:
            conn.close()

    assert new_image_path != old_image_path
    assert not os.path.exists(old_image_path)
    assert os.path.exists(new_image_path)


def test_upload_db_failure(client, monkeypatch):
    user_id, headers = create_test_user()

    conn = database.get_connection()
    real_cursor = conn.cursor()

    class FakeCursor:

        def execute(self, query, params=None):
            if query.startswith("UPDATE users SET image_profile"):
                raise Exception("Database error")

            return real_cursor.execute(query, params)

        def fetchone(self):
            return real_cursor.fetchone()

    class FakeConnection:

        def cursor(self):
            return FakeCursor()

        def commit(self):
            return conn.commit()

        def close(self):
            return conn.close()

    def fake_get_connection():
        return FakeConnection()

    monkeypatch.setattr(
        users,
        "get_connection",
        fake_get_connection
    )

    files_before = set(os.listdir("avatars"))

    with open("test_image.jpg", "rb") as f:
        content = f.read()

    response = client.post(
        f"/users/user/{user_id}/avatars",
        files={
            "file": (
                "test.jpg",
                content,
                "image/jpeg"
            )
        },
        headers=headers
    )

    assert response.status_code == 500

    files_after = set(os.listdir("avatars"))

    assert files_before == files_after

    conn.close()

from app.database import get_connection
from app.security import hash_password
from fastapi import HTTPException
from app.schema import EmailStr
from datetime import datetime,timezone

from app.loggin_config import logger

def crud_create_user(user):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? ",(user.email,))
        row=cursor.fetchone()
        if row:
            logger.warning("User already to creat , Email found")
            raise HTTPException(
                status_code=409,
                detail="User already to create"
            )
        cursor.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",(user.name,user.email,hash_password(user.password),'user'))
        conn.commit()
        logger.info("User created successfully")
        user_id=cursor.lastrowid
        return user_id
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error")
        raise
    finally:
        if conn is not None:
            conn.close()
def crud_read_users(user_id:int):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?",(user_id,))
        row=cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            ) 
        return {
            "name":row[1],
            "email":row[2],
            "role":row[4]
        }
    except HTTPException:
        raise
    finally:
        if conn is not None:
            conn.close()

def crud_updated_user(user_id:int,users):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        updated=[]
        values=[]
        if users.name is not None:
            updated.append("name=?")
            values.append(users.name)
        if users.email is not None:
            updated.append("email=?")
            values.append(users.email)
        if not updated:
            raise HTTPException(
                status_code=400,
                detail="No fields provided"
            )
        values.append(user_id)
        cursor.execute(f"""UPDATE users SET {",".join(updated)}  WHERE id=?""",values)
        conn.commit()
        if cursor.rowcount==0:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        return {
            "message":"User updated successfully."
        }
    except HTTPException:
        raise
    finally:
        if conn is not None:
            conn.close()

def crud_delete_user(user_id:int):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("DELETE FROM users WHERE id=?",(user_id,))
        conn.commit()
        if cursor.rowcount==0:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
    
        return {
            "message":"User deleted successfully"
        }
    except HTTPException:
        raise
    finally:
        if conn is not None:
            conn.close()

def crud_get_user_email(email:EmailStr):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=?",(email,))
        row=cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        return row
    except HTTPException:
        raise
    finally:
        if conn is not None:
            conn.close()

def crud_creat_verification(user_id: int , token_hash: str , expires_at: datetime):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        expires_at=datetime.isoformat(expires_at)
        cursor.execute("INSERT INTO email_verifications(user_id,token_hash,expires_at) VALUES (?,?,?)",(user_id,token_hash,expires_at))
        conn.commit()
    finally:
        if conn is not None:
            conn.close()
def crud_get_verification(token_hash: str):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM email_verifications WHERE token_hash =? ",(token_hash,))
        row=cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=401,
                detail="Invalid verification token"
            )
        expires_at=datetime.fromisoformat(row[3])
        now=datetime.now(timezone.utc)
        if expires_at < now:
            raise HTTPException(
                status_code=401,
                detail="Verification token expired"
            )
        used=row[4]
        if used:
            raise HTTPException(
                status_code=401,
                detail="The token is used"
            )
        cursor.execute("UPDATE email_verifications SET used=? WHERE token_hash =?",(True,token_hash))
        conn.commit()
        return row[1]
    except HTTPException:
        raise
    finally:
        if conn is not None:
            conn.close()
def crud_verify_user(user_id: int):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("UPDATE users SET is_verified=? WHERE id=?",(True,user_id))
        conn.commit()
    finally:
        if conn is not None:
            conn.close()

def crud_record_password_test(user_id:int,token_hash:str,expires_at: datetime):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        expires_at=datetime.isoformat(expires_at)
        cursor.execute("INSERT INTO password_resets(user_id,token_hash,expires_at,used) VALUES(?,?,?,?)",(user_id,token_hash,expires_at,0))
        conn.commit()
    finally:
        if conn is not None:
            conn.close()
def crud_verify_token(token_hash:str):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM password_resets WHERE token_hash=?",(token_hash,))
        row=cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=401,
                detail="Invalid verified token"
            )
        expires_at=datetime.fromisoformat(row[3])
        now=datetime.now(timezone.utc)
        if now > expires_at:
            raise HTTPException(
                status_code=401,
                detail="Invalid verified token, Time out"
            )
        used=row[4]
        if used:
            raise HTTPException(
                status_code=401,
                detail="Invalid verified token "
            )
        return row[1],row[2]
    except HTTPException:
        raise
    finally:
        if conn is not None:
            conn.close()
def new_reset_password(user_id:int,new_password:str):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        hash_new_password=hash_password(new_password)
        cursor.execute("UPDATE users SET password=? WHERE id=?",(hash_new_password,user_id))
        conn.commit()
    finally:
        if conn is not None:
            conn.close()
def revoke_token(token_hash:str):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("UPDATE password_resets SET used=? WHERE token_hash=? ",(1,token_hash))
        conn.commit()
    finally:
        if conn is not None:
            conn.close()

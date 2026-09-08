from jose import jwt , JWTError
from fastapi import HTTPException
from datetime import datetime,timezone,timedelta
import hashlib
import secrets
import os
from app.database import get_connection
from app.security import oauth2_scheme
from fastapi import Depends
from dotenv import load_dotenv
load_dotenv()
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM="HS256"
EXPIRE_ACCESS_TOKEN=30
def create_access_token(data:dict):
    expire=datetime.now(timezone.utc)+timedelta(minutes=EXPIRE_ACCESS_TOKEN)
    to_encode=data.copy()
    to_encode["exp"]=expire
    to_encode["token_type"]="access"
    jwt_encode=jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return jwt_encode
def verify_access_token(token:str):
    try:
        payload=jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        user_id=payload.get("sub")
        if payload.get("token_type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid Token"
            )
        if  user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid Token"
            )
        from app.crud_user import crud_read_users
        return crud_read_users(int(user_id))
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid"
        )

def require_admin(token:str=Depends(oauth2_scheme)):
    row=verify_access_token(token)
    if row["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="You don't have permission"
        )

def create_refresh_token(user_id:int):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        refresh_token=secrets.token_urlsafe(32)
        hash_refresh_token=hashlib.sha256(
            refresh_token.encode()
        ).hexdigest()
        create_at=datetime.now(timezone.utc)
        expire_at=create_at+timedelta(days=7)
        create_at=create_at.isoformat()
        expire_at=expire_at.isoformat()
        revoked=0
        cursor.execute("INSERT INTO refresh_tokens VALUES(?,?,?,?,?)",(user_id,hash_refresh_token,create_at,expire_at,revoked))
        conn.commit()
        return refresh_token,hash_refresh_token,create_at,expire_at,revoked
    finally:
        if conn is not None:
            conn.close()
def verify_refresh_token(refresh_token:str):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        hash_refresh_token=hashlib.sha256(
            refresh_token.encode()
        ).hexdigest()
        cursor.execute("SELECT * FROM refresh_tokens WHERE hash_token=?",(hash_refresh_token,))
        row=cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=401,
                detail="Invialid refresh token"
            )
        expire=datetime.fromisoformat(row[3])
        if datetime.now(timezone.utc) > expire:
            raise HTTPException(
                status_code=401,
                detail="Refresh token expired"
            )
        if row[4]!=0:
            raise HTTPException(
                status_code=401,
                detail="Refresh token is revoked"
            )
        return row
    except HTTPException:
        raise
    finally:
        if conn is not None:
            conn.close()
def revoke_refresh_token(refresh_token:str):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        hash_refresh_token=hashlib.sha256(
            refresh_token.encode()
        ).hexdigest()
        cursor.execute("SELECT * FROM refresh_tokens WHERE hash_token=?",(hash_refresh_token,))
        row=cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )
        cursor.execute("UPDATE refresh_tokens SET revoked=? WHERE hash_token=?",(1,hash_refresh_token))
        conn.commit()
        new_access_token=create_access_token(data={"sub":str(row[0])})
        new_refresh_token=create_refresh_token(row[0])
        return {
            "access_token":new_access_token,
            "refresh_token":new_refresh_token[0],
            "token_type":"bearer"
        }
    except HTTPException:
        raise
    finally:
        if conn is not None:
            conn.close()

    


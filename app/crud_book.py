from app.database import get_connection
from fastapi import HTTPException
from typing import Optional,List

def crud_create_book(book):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM books WHERE isbn=?",(book.isbn,))
        row=cursor.fetchone()
        if row:
            raise HTTPException(
                status_code=409,
                detail="Book already to creat"
            )
        cursor.execute("INSERT INTO books(isbn,title,author) VALUES(?,?,?)",(book.isbn,book.title,book.author))
        conn.commit()
        return {
            "message":"Book added seccussfully"
        }
    except HTTPException:
        raise
    finally:
        if conn is not None:
            conn.close()

def crud_read_book(isbn:str):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("SELECT * FROM books WHERE isbn=?",(isbn,))
        row=cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=404,
                detail="Book not found"
            )
        return {
            "isbn":row[0],
            "title":row[1],
            "author":row[2]
        }
    except HTTPException:
        raise
    finally:
        if conn is not None:
            conn.close()
    
def crud_search_books(search: str = None ,author: str =None, authors: Optional[List[str]]=None, limit: int = 10 , offset : int = 0):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        conditions=[]
        params=[]
        where_clause=""
        value=[]
        if search:
            search_term=f"%{search}%"
            conditions.append("(isbn LIKE ? OR title LIKE ? OR author LIKE ?)")
            params.extend([search_term,search_term,search_term])
        if author:
            conditions.append(" author = ?")
            params.append(author)
        if authors:
            for i in range(len(authors)):
                value.append("?")
            value=",".join(value)
            conditions.append(f" author IN ({value})")
            params.extend(authors)
        if conditions:
            where_clause=" WHERE "+" AND ".join(conditions)
        cursor.execute(f"SELECT COUNT(*) FROM books {where_clause}",params)
        total=cursor.fetchone()[0]
        params.extend([limit,offset])
        cursor.execute(f"SELECT * FROM books {where_clause} ORDER BY title ASC LIMIT ? OFFSET ?",params)
        rows=cursor.fetchall()
        return {
            "total":total,
            "items":[{
                "isbn":row[0],
                "title":row[1],
                "author":row[2]
            }for row in rows]
        }
    finally:
        if conn is not None:
            conn.close()
def crud_update_book(isbn:str,book):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("UPDATE books SET title=? , author=? WHERE isbn=?",(book.title,book.author,isbn))
        conn.commit()
        if cursor.rowcount==0:
            raise HTTPException(
                status_code=404,
                detail="Book not found"
            )
        return {
            "message":"Book updated seccussfully"
        }
    except HTTPException:
        raise
    finally:
        if conn is not None:
            conn.close()

def crud_delete_book(isbn:str):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("DELETE FROM books WHERE isbn=?",(isbn,))
        conn.commit()
        if cursor.rowcount==0:
            raise HTTPException(
                status_code=404,
                detail="Book not found"
            )
        return{
            "message":"Book deleted seccussfully"
        }
    except HTTPException:
        raise
    finally:
        if conn is not None:
            conn.close()
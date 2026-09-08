from app.database import get_connection
from fastapi import HTTPException
from datetime import datetime,timezone
def crud_create_borrowing(borrow):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        now=datetime.now(timezone.utc).isoformat()
        cursor.execute("SELECT * FROM books WHERE isbn=? ",(borrow.isbn,))
        row=cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=404,
                detail="Book not found"
            )
        cursor.execute("SELECT * FROM borrowing WHERE isbn=? AND returned_at IS NULL",(borrow.isbn,))
        row_return=cursor.fetchone()
        if row_return:
            raise HTTPException(
                status_code=409,
                detail="Book not available"
            )
        cursor.execute("SELECT * FROM users WHERE id=?",(borrow.user_id,))
        row_user=cursor.fetchone()
        if not row_user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        cursor.execute("INSERT INTO borrowing(user_id,isbn,borrowed_at) VALUES(?,?,?)",(borrow.user_id,borrow.isbn,now))
        conn.commit()
        return{
            "message":"Book borrowed successfully"
        }
    except HTTPException:
        raise
    finally:
        if conn is not None:
            conn.close()

def crud_return_book(isbn:str,user_id:int):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        now=datetime.now(timezone.utc).isoformat()
        cursor.execute("SELECT * FROM books WHERE isbn=? ",(isbn,))
        row=cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=404,
                detail="Book not found"
            )
        cursor.execute("SELECT * FROM users WHERE id=?",(user_id,))
        row_user=cursor.fetchone()
        if not row_user:
            raise HTTPException(
                status_code=404,
                detail="User not found"
            )
        cursor.execute("SELECT * FROM borrowing WHERE isbn=? AND user_id=? AND returned_at IS NULL",(isbn,user_id))
        row_return=cursor.fetchone()
        if not row_return:
            raise HTTPException(
                status_code=404,
                detail="Book not available"
            )
        cursor.execute("UPDATE borrowing SET returned_at=? WHERE isbn=? AND user_id=? AND returned_at IS NULL",(now,isbn,user_id))
        conn.commit()
        return{
            "message":"Book returned successfully"
        }
    except HTTPException:
        raise
    finally:
        if conn is not None:
            conn.close()

def crud_read_borrowing(id:int):
    conn=None 
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute('''SELECT users.name,books.title,borrowing.borrowed_at,borrowing.returned_at FROM borrowing 
        JOIN users ON borrowing.user_id = users.id
        JOIN books ON borrowing.isbn = books.isbn WHERE borrowing.id=?''',(id,))
        row=cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=404,
                detail="This register is not found"
            )
        return {
            "name":row[0],
            "title":row[1],
            "borrowed_at":row[2],
            "returned_at":row[3]
        }
    except HTTPException:
        raise
    finally:
        if conn is not None:
            conn.close()
def crud_read_all_borrowing():
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute('''SELECT users.name,books.title,borrowing.borrowed_at,borrowing.returned_at FROM borrowing 
        JOIN users ON borrowing.user_id = users.id
        JOIN books ON borrowing.isbn = books.isbn''')
        rows=cursor.fetchall()
        if not rows:
            raise HTTPException(
                status_code=404,
                detail="This register is not found"
            )
        return [dict(row) for row in rows]
    except HTTPException:
        raise
    finally:
        if conn is not None:
            conn.close()    

def crud_delete_register(id:int):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute("DELETE FROM borrowing WHERE id=? AND returned_at IS NOT NULL",(id,))
        conn.commit()
        if cursor.rowcount==0:
            raise HTTPException(
                status_code=409,
                detail="This register not available to delete"
            )
        return {
            "massage":"Borrowing record deleted successfully"
        }
    except HTTPException:
        raise
    finally:
        if conn is not None:
            conn.close()
def crud_read_borrowed_books():
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        cursor.execute('''SELECT users.name , books.title , borrowing.borrowed_at , borrowing.returned_at FROM borrowing
        JOIN users ON borrowing.user_id=users.id
        JOIN books ON borrowing.isbn=books.isbn
        WHERE borrowing.returned_at IS NULL''')
        rows=cursor.fetchall()
        if not rows:
            raise HTTPException(
                status_code=404,
                detail="No books borrowed"
            )
        return [dict(row) for row in rows]
    except HTTPException:
        raise
    finally:
        if conn is not None:
            conn.close()
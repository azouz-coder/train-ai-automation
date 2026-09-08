from typing import Optional,List
from fastapi import APIRouter,Depends,File,UploadFile,Query,HTTPException
from app.schema import CreateBook,ResponseBook,BookPaginatedRespons,UpdateBook
from app.crud_book import (
    crud_create_book,
    crud_read_book,
    crud_search_books,
    crud_update_book,
    crud_delete_book,
)
from app.database import get_connection
from app.tokens import require_admin
import uuid
import os 

router=APIRouter(
    prefix="/books",
    tags=['books']
)
@router.post("/")
async def created_book(book:CreateBook,crruent_book=Depends(require_admin)):
    return crud_create_book(book)

@router.get("/{isbn}",response_model=ResponseBook)
async def read_book(isbn:str):
    return crud_read_book(isbn)
@router.get("/",response_model=BookPaginatedRespons)
async def search_book(search: str = None ,author:str = None,  authors: Optional[List[str]]=Query(None), limit: int = Query(10,ge=1,le=100) , offset: int = Query(0,ge=0)):
    return crud_search_books(search,author,authors,limit,offset)

@router.put("/{isbn}")
async def update_book(isbn:str,book:UpdateBook,crruent_book=Depends(require_admin)):
    return crud_update_book(isbn,book)

@router.delete("/{isbn}")
async def delete_book(isbn:str,crruent_book=Depends(require_admin)):
    return crud_delete_book(isbn)
@router.post("/{isbn}/uploads")
async def upload_book_image(isbn:str,file:UploadFile=File(...)):
    conn=None
    try:
        conn=get_connection()
        cursor=conn.cursor()
        if file.content_type not in ["image/png","image/jpeg"]:
            raise HTTPException(
                status_code=415,
                detail="Invalid content type"
            )
        content_bytes=await file.read(8)
        JPEG_SIGNATURE=b"\xff\xd8\xff"
        PNG_SIGNATURE=b"\x89PNG\r\n\x1a\n"
        if file.content_type=="image/png" and not content_bytes.startswith(PNG_SIGNATURE):
            raise HTTPException(
                status_code=415,
                detail="Invalid image file"
            )
        if file.content_type=="image/jpeg" and not content_bytes.startswith(JPEG_SIGNATURE):
            raise HTTPException(
                status_code=415,
                detail="Invalid image file"
            )
        await file.seek(0)
        content=await file.read()
        if len(content) > (5*1024)*1024:
            raise HTTPException(
                status_code=413,
                detail="This file is bigger than allow size,Please Enter a file smaller than 5MB"
            )
        cursor.execute("SELECT * FROM books WHERE isbn=?",(isbn,))
        row=cursor.fetchone()
        if not row:
            raise HTTPException(
                status_code=404,
            detail="Book not found"
            )
        
        if file.content_type=="image/jpeg":
            extension=".jpg"
        else:
            extension=".png"
        path=os.path.join("uploads",f"{uuid.uuid4()}{extension}")
        with open(path , "wb") as f:
            f.write(content)
        db_updated=False
        try:
            cursor.execute("UPDATE books SET image_path=? WHERE isbn=?",(path,isbn))
            conn.commit()
            db_updated=True
            old_image_path=row[3]
            if old_image_path is not None:
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
        except Exception :
            if not db_updated:
                if os.path.exists(path):
                    os.remove(path)
                raise HTTPException(
                        status_code=500,
                    detail="It happened a wrong to saved the file in database"
                )
        return {
            "message":"the file saved successfully"
        }
    except HTTPException:
        raise
    finally:
        if conn is None:
            conn.close()
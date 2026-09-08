from fastapi import APIRouter,Depends
from app.crud_borrowing import (
    crud_create_borrowing,
    crud_return_book,
    crud_read_all_borrowing,
    crud_read_borrowing,
    crud_delete_register,
    crud_read_borrowed_books,
)

from app.schema import CreateBorrowing, ResponseBorrowing
from app.tokens import require_admin
router=APIRouter(
    prefix="/borrowing",
    tags=["borrowing"]
)

@router.post("/")
async def borrow_book(borrow:CreateBorrowing,current_borrowing=Depends(require_admin)):
    return crud_create_borrowing(borrow)
@router.put("/")
async def returned_book(isbn:str,user_id:int,current_borrowing=Depends(require_admin)):
    return crud_return_book(isbn,user_id)
@router.get('/borrow',response_model=list[ResponseBorrowing])
async def read_all_borrowing():
    return crud_read_all_borrowing()

@router.get("/{id}",response_model=ResponseBorrowing)
async def read_borrowing(id:int):
    return crud_read_borrowing(id)


@router.delete("/{id}")
async def deleted_register(id:int):
    return crud_delete_register(id)

@router.get("/",response_model=list[ResponseBorrowing])
async def read_borrowed_books():
    return crud_read_borrowed_books()
from pydantic import BaseModel,Field,EmailStr


class CreateUser(BaseModel):
    name: str = Field(min_length=3)
    email: EmailStr
    password: str = Field(min_length=8)

class ResponseUser(BaseModel):
    name: str
    email: EmailStr
    role: str

class UpdatedUser(BaseModel):
    name: str|None=None
    email: EmailStr|None=None

#Books
class CreateBook(BaseModel):
    isbn: str
    title: str = Field(min_length=3)
    author: str = Field(min_length=3)

class ResponseBook(BaseModel):
    isbn: str
    title: str
    author: str
class BookPaginatedRespons(BaseModel):
    total: int
    items: list[ResponseBook]
class UpdateBook(BaseModel):
    title: str = Field(min_length=3)
    author: str = Field(min_length=3)

#Borrowing
class CreateBorrowing(BaseModel):
    isbn: str
    user_id: int

class ResponseBorrowing(BaseModel):
    name:str
    title:str
    borrowed_at:str
    returned_at:str|None
class RespondeLogin(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str

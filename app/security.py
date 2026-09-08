from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
pwd_context=CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

def hash_password(password:str):
    return pwd_context.hash(password)

def verify_password(plain_password: str,hash_password: str):
    return pwd_context.verify(
        plain_password,
        hash_password
    )
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="users/login")
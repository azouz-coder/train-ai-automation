from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends,HTTPException
from app.crud_user import crud_get_user_email
from app.security import verify_password
from app.tokens import create_access_token,create_refresh_token
from app.loggin_config import logger
def login_user(data: OAuth2PasswordRequestForm = Depends()):
    try:
        row=crud_get_user_email(data.username)
        verified=verify_password(
            data.password,
            row[3]
        )
        if not verified:
            logger.warning("Failed login attempt")
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        is_verified=row[6]
        if not is_verified:
            logger.warning("Email not verified")
            raise HTTPException(
                status_code=403,
                detail="Please verify your email"
            )
        access_token=create_access_token(data={"sub":str(row[0])})
        refresh_token=create_refresh_token(row[0])
        logger.info("User login successfully.")
        return {
            "access_token":access_token,
            "refresh_token":refresh_token[0],
            "token_type":"bearer"
            }
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error")
        raise
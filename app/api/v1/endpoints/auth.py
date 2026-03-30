from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse, TokenResponse
from app.services.user_service import create_user, authenticate_user
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user account."""
    return create_user(db, data)


@router.post("/token", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate and receive a Bearer token."""
    user = authenticate_user(db, form_data.username, form_data.password)
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)
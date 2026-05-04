from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter()


def _user_by_email(db: Session, email: str) -> User | None:
    """Satu baris User atau None (SQLAlchemy 2 — hindari salah pakai scalar_one_or_none)."""
    return db.scalar(select(User).where(User.email == email))


@router.post("/register", response_model=TokenResponse)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    email_norm = str(body.email).lower().strip()
    if _user_by_email(db, email_norm) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sudah terdaftar",
        )
    user = User(
        name=body.name.strip(),
        email=email_norm,
        hashed_password=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(sub=str(user.id))
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    email = str(body.email).lower().strip()
    user = _user_by_email(db, email)
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email atau kata sandi salah",
        )
    token = create_access_token(sub=str(user.id))
    return TokenResponse(access_token=token)

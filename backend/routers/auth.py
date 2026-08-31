from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from models.user import User
from schemas.user import UserCreate, UserResponse
from services.password_service import hash_password


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    # 이메일 중복 확인
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 가입된 이메일입니다."
        )

    # 비밀번호 해싱
    hashed_password = hash_password(user_data.password)

    # 사용자 생성
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        nickname=user_data.nickname
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
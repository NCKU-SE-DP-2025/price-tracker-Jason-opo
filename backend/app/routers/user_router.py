from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user_schema import UserCreate, UserLogin, UserLoginResponse, User
from app.services.user_service import UserService

router = APIRouter()
user_service = UserService()

# 註冊
@router.post("/register", response_model=User)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """註冊新使用者"""
    return user_service.create_user(db, user)

# 登入
@router.post("/login", response_model=UserLoginResponse)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    """登入並回傳 access_token"""
    # 呼叫 service 取得 token dict
    token_data = user_service.login(db, user)

    # 取得使用者資料
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    return UserLoginResponse(
        user_id=db_user.id,
        username=db_user.username,
        access_token=token_data["access_token"],
        token_type=token_data["token_type"]
    )

# 取得目前使用者 (Depends)
def get_current_user(token: str, db: Session = Depends(get_db)):
    """供 Depends() 使用的自訂驗證函數"""
    return user_service.authenticate_token(token, db)

# 取得目前使用者資訊
@router.get("/me", response_model=User)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

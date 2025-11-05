from pydantic import BaseModel

# 使用者基本資料
class UserBase(BaseModel):
    username: str

# 建立使用者時輸入資料
class UserCreate(UserBase):
    password: str  # 明文，service 會轉成 hashed_password

# 登入資料
class UserLogin(BaseModel):
    username: str
    password: str

# 登入後回傳
class UserLoginResponse(BaseModel):
    user_id: int
    username: str
    access_token: str
    token_type: str
# 回傳用（含 id）
class User(UserBase):
    id: int

    class Config:
        orm_mode = True

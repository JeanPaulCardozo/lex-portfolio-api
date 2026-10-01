from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserOut(BaseModel):
    id: int
    email: str

    model_config = ConfigDict(from_attributes=True)

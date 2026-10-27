from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)

    @field_validator("password")
    @classmethod
    def bcrypt_byte_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña no puede superar 72 bytes UTF-8")
        return value


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("password")
    @classmethod
    def bcrypt_byte_limit(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("La contraseña no puede superar 72 bytes UTF-8")
        return value


class ExpenseIn(BaseModel):
    amount: float = Field(gt=0, le=1_000_000)
    currency: str = Field(default="MXN", pattern=r"^[A-Za-z]{3}$")
    category: str = Field(min_length=2, max_length=40)
    note: str = Field(default="", max_length=160)
    spent_on: date = Field(default_factory=date.today)


class ExpenseOut(ExpenseIn):
    id: int
    model_config = ConfigDict(from_attributes=True)

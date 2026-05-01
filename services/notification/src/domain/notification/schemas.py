from pydantic import BaseModel, EmailStr

class PasswordResetNotification(BaseModel):
    to_email: EmailStr
    reset_link: str

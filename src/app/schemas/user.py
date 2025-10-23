from pydantic import BaseModel


class UserLoginRequest(BaseModel):
    """User login request."""

    login: str
    password: str


class UserLoginResponse(BaseModel):
    """User login response."""

    access_token: str | None


class UserLogoutResponse(BaseModel):
    """User logout response."""

    message: str

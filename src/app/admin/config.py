import contextlib

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend, login_required
from sqlalchemy import select, true

from src.app.api.endpoints.user import auth_user
from src.app.core.config import settings
from src.app.core.db import async_session_maker, get_async_session
from src.app.models import Node
from src.app.models.user import User, UserRolesEnum
from src.app.schemas.user import UserLoginRequest
from src.app.services.user import get_current_user

get_async_session_context = contextlib.asynccontextmanager(get_async_session)


class NodeException(Exception):
    """Node exception."""

    def __init__(self, message: str) -> None:
        """Error message."""
        self.message = message


async def node_exception_handler(
        request: Request, exc: NodeException) -> JSONResponse:
    """Node exception handler."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": exc.message})


class CustomAdmin(Admin):
    """Custom index view for Admin."""

    @login_required
    async def index(self, request: Request) -> Response:
        """Index view with nodes tree."""
        async with async_session_maker() as session:
            result = await session.execute(
                select(Node).filter(Node.is_active == true()))
            nodes = result.scalars().all()
            nodes_dict = {}
            for node in nodes:
                nodes_dict[node.id] = {
                    'id': node.id,
                    'title': node.title,
                    'parent_id': node.parent_id,
                    'children': [],
                }

            root_nodes = []
            for node in nodes:
                if node.parent_id is None:
                    root_nodes.append(nodes_dict[node.id])
                else:
                    if node.parent_id in nodes_dict:
                        nodes_dict[node.parent_id]['children'].append(
                            nodes_dict[node.id],
                        )

            return await self.templates.TemplateResponse(
                request,
                "sqladmin/index.html",
                context={"tree": root_nodes})


async def get_user_from_request(request: Request) -> User | None:
    """Get current user from request."""
    token = request.session.get('access_token')
    if not token:
        return None
    async with get_async_session_context() as session:
        return await get_current_user(
                token=token['access_token'],
                session=session,
            )


class AdminAuth(AuthenticationBackend):
    """SQLAlchemyAdmin login backend class."""

    async def login(self, request: Request) -> bool:
        """Login user."""
        try:
            form = await request.form()
            username, password = form['username'], form['password']
            auth_data = UserLoginRequest(login=username, password=password)
        except ValueError:
            return False
        response = Response()
        async with get_async_session_context() as session:
            token = await auth_user(
                user_data=auth_data,
                response=response,
                session=session,
                )
        request.session.update({'access_token': token})
        return True

    async def logout(self, request: Request) -> bool:
        """Logout user."""
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool | RedirectResponse:
        """Authentificate user."""
        current_user = await get_user_from_request(request=request)
        if current_user:
            if (
                current_user.role == UserRolesEnum.ADMIN or
                current_user.role == UserRolesEnum.MANAGER
            ):
                return True
        return RedirectResponse('/admin/login')


authentication_backend = AdminAuth(secret_key=settings.secret)

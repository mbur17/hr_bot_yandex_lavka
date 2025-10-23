import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.const import MIN_PASSWORD_LEN
from src.app.crud.user import user_crud
from src.app.models.user import User, UserRolesEnum
from src.app.services.user import get_password_hash


async def import_users_from_excel(
    file_bytes: bytes, session: AsyncSession,
) -> int:
    """Read users from file and check correctness."""
    df = pd.read_excel(file_bytes)
    count = 0
    for _, row in df.iterrows():
        # Login check.
        login = str(row['login']).strip()
        user_exists = await user_crud.get_by_login(
            login=login, session=session,
        )
        if user_exists:
            continue

        # Telegram ID check.
        telegram_id = row.get('telegram_id')
        if pd.notna(telegram_id):
            try:
                telegram_id = int(telegram_id)
            except Exception:
                continue
            user_by_telegram = await user_crud.get_by_telegram_id(
                telegram_id=telegram_id, session=session,
            )
            if user_by_telegram:
                continue

        # ENUM role check.
        role_str = str(row['role']).strip()
        try:
            role = UserRolesEnum(role_str)
        except ValueError:
            continue

        # Password check and hash.
        password_cell = row.get('password')
        password_raw = None
        if not pd.isna(password_cell):
            password_raw = str(password_cell).strip()

        if role in (UserRolesEnum.ADMIN.value, UserRolesEnum.MANAGER.value):
            if not password_raw or len(password_raw) < MIN_PASSWORD_LEN:
                continue
            hashed_password = get_password_hash(password_raw)
        else:
            hashed_password = None

        user = User(
            login=login,
            full_name=str(row.get('full_name', '')).strip(),
            hashed_password=hashed_password,
            telegram_id=telegram_id if pd.notna(
                row.get('telegram_id'),
            ) else None,
            is_active=True,  # Default true.
            role=role,
        )
        session.add(user)
        count += 1

    await session.commit()
    return count

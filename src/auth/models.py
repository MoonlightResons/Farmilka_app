from sqlalchemy import Column, Integer, String, ForeignKey, Table, MetaData, JSON, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

metadata = MetaData()


role = Table(
    "role",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, nullable=False),
    Column("permissions", JSON)
)


user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column('email', String, nullable=False),
    Column('password', String, nullable=False),
    Column('registered_at', TIMESTAMP, default=lambda: datetime.now(timezone.utc)),
    Column("nickname", String, nullable=False),
    Column('role_id', Integer, ForeignKey(role.c.id)),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("is_superuser", Boolean, default=False, nullable=False),
    Column("is_verified", Boolean, default=False, nullable=False),
)


wallet = Table(
    "wallet",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("wallet", String, nullable=False),
    Column('wallet_id', Integer, ForeignKey(user.c.id)),
    Column("crypto", Integer, default=0)
)


# profile = Table(
#     "profile",
#     metadata,
#     Column("id", Integer, primary_key=True),
#     Column("nickname", String, nullable=False),
#     Column("user", Integer, ForeignKey("users.id"))
#     # Column("avatar")
# )
from sqlalchemy.orm import mapped_column, Mapped

from disco_server.core.database.dtos.base import Base


class KeyValueDto(Base):
    """Key value store for adhoc data"""

    __tablename__ = 'key_value'

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(unique=True)
    value: Mapped[str | None] = mapped_column()
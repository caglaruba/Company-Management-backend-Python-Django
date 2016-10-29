from models import Base
from sqlalchemy import Column
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy import String


class StoredSession(Base):
    __tablename__ = "sessions"
    id = Column(String(length=36), primary_key=True, nullable=False)
    data = Column(Text, nullable=False)
    expires = Column(DateTime, nullable=False)

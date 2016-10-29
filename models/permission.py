from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref

from models import Base


class Permission(Base):
    __tablename__ = "permission"

    id = Column(Integer, primary_key=True, autoincrement=True)

    role_id = Column(Integer, ForeignKey("role.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    role = relationship("Role", backref=backref("permissions", order_by=id, cascade="all,delete-orphan", ))

    action = Column(String(length=256), nullable=False)

from models import Base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import CheckConstraint
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

class AccountCompany(Base):
    __tablename__ = "account_company"

    account_id = Column(Integer, ForeignKey("account.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    company_id = Column(Integer, ForeignKey("company.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)

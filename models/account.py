from passlib.handlers.pbkdf2 import pbkdf2_sha512

from models import Base
from models.account_company import AccountCompany

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import CheckConstraint
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

class Account(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True)

    firstname = Column(String, nullable=False)
    lastname_prefix = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    mailaddress = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("role.id", onupdate="SET NULL", ondelete="SET NULL"), nullable=False)
    role = relationship("Role")

    companies = relationship("Company", secondary=AccountCompany.__table__)

    def set_password(self, new_password):
        self.password_hash = pbkdf2_sha512.encrypt(new_password)

    def is_password(self, claimed_password):
        try:
            return pbkdf2_sha512.verify(claimed_password, self.password_hash)
        except ValueError:
            return False

    def to_dict(self):
        data_dict = dict()
        data_dict["id"] = self.id
        data_dict["name"] = self.firstname + " " + self.lastname_prefix + " " + self.lastname
        data_dict["role_id"] = self.role_id

        data_dict["companies"] = []
        for company in self.companies:
            data_dict["companies"].append({"id":company.id,"name":company.name})

        return data_dict



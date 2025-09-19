from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base

class RoleRequest(Base):
    __tablename__ = "role_requests"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    requested_role = Column(String, nullable=False)  # 'analyst' | 'manager'
    status = Column(String, default="pending")       # 'pending' | 'approved' | 'rejected'
    comment = Column(String, nullable=True)
    decided_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    decided_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", foreign_keys=[user_id])

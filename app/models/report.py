from sqlalchemy import Column, Integer, String, DateTime, LargeBinary, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
import enum


class ReportFormat(str, enum.Enum):
    pdf = "pdf"
    csv = "csv"
    xlsx = "xlsx"


class ReportArchive(Base):
    __tablename__ = "report_archive"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    format = Column(Enum(ReportFormat), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    content = Column(LargeBinary, nullable=False)

    generated_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    generated_by = relationship("User", back_populates="reports")
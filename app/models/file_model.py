from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from app.models.database import Base


class FileRecord(Base):
    __tablename__ = "files"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    feature_count = Column(Integer, default=0)
    crs = Column(String, nullable=True)
    status = Column(String, nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
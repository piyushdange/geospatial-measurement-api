from sqlalchemy import Column, Float, ForeignKey, Integer, String, Text

from app.models.database import Base


class FeatureRecord(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True, autoincrement=True)

    file_id = Column(
        String,
        ForeignKey("files.id"),
        nullable=False,
        index=True
    )

    feature_index = Column(Integer, nullable=False)

    geometry_type = Column(String, nullable=False)

    geometry = Column(Text, nullable=True)

    properties = Column(Text, nullable=True)

    measurement_type = Column(String, nullable=True)

    measurement_value = Column(Float, nullable=True)

    measurement_unit = Column(String, nullable=True)
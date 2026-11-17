from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from .db import Base

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    version = Column(String(50), default="1.0")
    source_filename = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    records = relationship("DatasetRecord", cascade="all, delete-orphan", back_populates="dataset")

class DatasetRecord(Base):
    __tablename__ = "dataset_records"
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    pid = Column(String(100), nullable=False)
    arrival_time = Column(Float, nullable=False)
    burst_time = Column(Float, nullable=False)
    priority = Column(Float, nullable=False, default=1)
    workload_id = Column(String(100), default="workload-1")
    dataset = relationship("Dataset", back_populates="records")

class TrainingJob(Base):
    __tablename__ = "training_jobs"
    id = Column(Integer, primary_key=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    status = Column(String(50), default="queued")
    message = Column(Text, default="")
    metrics_json = Column(JSON)
    model_version = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

class ModelArtifact(Base):
    __tablename__ = "model_artifacts"
    id = Column(Integer, primary_key=True)
    version = Column(String(100), unique=True, nullable=False)
    dataset_id = Column(Integer, ForeignKey("datasets.id"))
    path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    metrics_json = Column(JSON)
    feature_importance_json = Column(JSON)

class SimulationRecord(Base):
    __tablename__ = "simulation_records"
    id = Column(Integer, primary_key=True)
    algorithm = Column(String(100))
    payload_json = Column(JSON)
    result_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

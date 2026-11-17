from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ProcessIn(BaseModel):
    pid: str
    arrival_time: float = Field(ge=0)
    burst_time: float = Field(gt=0)
    priority: float = 1

class SimulateRequest(BaseModel):
    algorithm: str
    processes: List[ProcessIn]
    quantum: Optional[float] = Field(default=2, gt=0)

class GenerateProcessesRequest(BaseModel):
    count: int = Field(default=10, ge=1, le=500)

class CompareRequest(BaseModel):
    processes: List[ProcessIn]
    algorithms: Optional[List[str]] = None
    quantum: Optional[float] = Field(default=2, gt=0)

class RecommendationRequest(BaseModel):
    processes: List[ProcessIn]

class TrainRequest(BaseModel):
    dataset_id: int
    n_estimators: int = Field(default=100, ge=1, le=2000)
    max_depth: Optional[int] = Field(default=10, ge=1, le=100)
    random_state: int = 42
    test_size: float = Field(default=0.2, gt=0.05, lt=0.5)
    weight_accuracy: float = 1
    weight_waiting_time: float = 1

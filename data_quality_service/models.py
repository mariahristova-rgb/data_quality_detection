# data-quality-service/src/models.py
from dataclasses import dataclass


@dataclass
class DataQualityMetrics:
    completeness: float = 0.0
    accuracy: float = 0.0
    consistency: bool = True
    validity: bool = True

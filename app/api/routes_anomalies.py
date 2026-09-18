from fastapi import APIRouter

from app.anomalies.detector import AnomalyDetector

router = APIRouter(
    prefix="/anomalies",
    tags=["Anomalies"],
)

detector = AnomalyDetector()


@router.get("")
def get_anomalies():
    return {
        "summary": detector.summary(),
        "anomalies": detector.detect(),
    }

from fastapi import APIRouter
from ..services.evidently_metrics_service import EvidentlyService

router = APIRouter(prefix="/metrics", tags=["Metrics"])
service = EvidentlyService()

@router.get("/evidently")
async def get_evidently_metrics():
    return service.get_prediction_metrics()

@router.get("/evidently/drift")
async def get_drift_status():
    return service.compute_drift()

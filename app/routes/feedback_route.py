from fastapi import APIRouter, HTTPException
from ..schemas.prediction_schemas import FeedbackInput
from ..services.feedback_service import FeedbackService

router = APIRouter(prefix="/feedback", tags=["Feedback"])
service = FeedbackService()

@router.post("/", status_code=201)
async def submit_feedback(feedback_data: FeedbackInput):
    try:
        service.submit_feedback(feedback_data.prediction_id, feedback_data.target)
        return {"status": "success", "message": "Feedback enregistré avec succès."}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne lors de l'enregistrement du feedback : {e}"
        )

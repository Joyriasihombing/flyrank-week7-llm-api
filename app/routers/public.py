from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.submission import Submission
from app.schemas.submission import SubmissionCreate
from app.database import get_db
from app.models.widget import Widget

router = APIRouter()


@router.get("/widgets/{widget_id}")
def get_public_widget(
    widget_id: int,
    db: Session = Depends(get_db)
):
    widget = db.query(Widget).filter(
        Widget.id == widget_id,
        Widget.is_active == True
    ).first()

    if widget is None:
        raise HTTPException(
            status_code=404,
            detail="Widget not found"
        )

    return {
        "id": widget.id,
        "title": widget.title,
        "description": widget.description,
        "widget_type": widget.widget_type,
        "button_text": widget.button_text
    }
@router.post("/widgets/{widget_id}/submit")
def submit_widget(
    widget_id: int,
    submission: SubmissionCreate,
    db: Session = Depends(get_db)
):
    widget = db.query(Widget).filter(
        Widget.id == widget_id,
        Widget.is_active == True
    ).first()

    if widget is None:
        raise HTTPException(
            status_code=404,
            detail="Widget not found"
        )

    new_submission = Submission(
        widget_id=widget.id,
        name=submission.name,
        email=submission.email,
        message=submission.message
    )

    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)

    return {
        "message": "Submission received",
        "submission_id": new_submission.id
    }
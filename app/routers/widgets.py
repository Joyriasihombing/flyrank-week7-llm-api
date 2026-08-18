from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.dependencies import get_current_user

from app.models.user import User
from app.models.widget import Widget
from app.models.submission import Submission

from app.schemas.widget import WidgetCreate
from app.schemas.submission import SubmissionCreate, SubmissionResponse

from app.llm.client import get_llm_client

import json
import os


router = APIRouter()


# =========================================================
# CREATE WIDGET
# =========================================================

@router.post("/")
def create_widget(
    widget: WidgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_widget = Widget(
        user_id=current_user.id,
        title=widget.title,
        description=widget.description,
        widget_type=widget.widget_type,
        button_text=widget.button_text,
        is_active=True
    )

    db.add(new_widget)
    db.commit()
    db.refresh(new_widget)

    return new_widget


# =========================================================
# GET ALL WIDGETS
# =========================================================

@router.get("/")
def get_widgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Widget).filter(
        Widget.user_id == current_user.id
    ).all()


# =========================================================
# DASHBOARD STATS
# IMPORTANT: put this BEFORE /{widget_id}
# =========================================================

@router.get("/dashboard/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_widgets = db.query(Widget).filter(
        Widget.user_id == current_user.id
    ).count()

    total_submissions = (
        db.query(Submission)
        .join(Widget)
        .filter(Widget.user_id == current_user.id)
        .count()
    )

    return {
        "total_widgets": total_widgets,
        "total_submissions": total_submissions
    }


# =========================================================
# GET SINGLE WIDGET
# =========================================================

@router.get("/{widget_id}")
def get_widget(
    widget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    widget = db.query(Widget).filter(
        Widget.id == widget_id,
        Widget.user_id == current_user.id
    ).first()

    if widget is None:
        raise HTTPException(
            status_code=404,
            detail="Widget not found"
        )

    return widget


# =========================================================
# UPDATE WIDGET
# =========================================================

@router.put("/{widget_id}")
def update_widget(
    widget_id: int,
    widget: WidgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_widget = db.query(Widget).filter(
        Widget.id == widget_id,
        Widget.user_id == current_user.id
    ).first()

    if db_widget is None:
        raise HTTPException(
            status_code=404,
            detail="Widget not found"
        )

    db_widget.title = widget.title
    db_widget.description = widget.description
    db_widget.widget_type = widget.widget_type
    db_widget.button_text = widget.button_text

    db.commit()
    db.refresh(db_widget)

    return db_widget


# =========================================================
# DELETE WIDGET
# =========================================================

@router.delete("/{widget_id}")
def delete_widget(
    widget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_widget = db.query(Widget).filter(
        Widget.id == widget_id,
        Widget.user_id == current_user.id
    ).first()

    if db_widget is None:
        raise HTTPException(
            status_code=404,
            detail="Widget not found"
        )

    db.delete(db_widget)
    db.commit()

    return {
        "message": "Widget deleted successfully"
    }


# =========================================================
# GET SUBMISSIONS
# =========================================================

@router.get("/{widget_id}/submissions")
def get_widget_submissions(
    widget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    widget = db.query(Widget).filter(
        Widget.id == widget_id,
        Widget.user_id == current_user.id
    ).first()

    if widget is None:
        raise HTTPException(
            status_code=404,
            detail="Widget not found"
        )

    return db.query(Submission).filter(
        Submission.widget_id == widget.id
    ).all()


# =========================================================
# CREATE SUBMISSION + AI TRIAGE
# =========================================================

@router.post(
    "/{widget_id}/submissions",
    response_model=SubmissionResponse
)
def create_submission(
    widget_id: int,
    submission: SubmissionCreate,
    db: Session = Depends(get_db)
):
    # -----------------------------------------------------
    # 1. Check widget
    # -----------------------------------------------------

    widget = db.query(Widget).filter(
        Widget.id == widget_id,
        Widget.is_active == True
    ).first()

    if widget is None:
        raise HTTPException(
            status_code=404,
            detail="Widget not found or inactive"
        )

    # -----------------------------------------------------
    # 2. Default AI result
    # -----------------------------------------------------

    category = "other"
    urgency = "normal"
    confidence = 0.5
    reason = "Default classification."

    # -----------------------------------------------------
    # 3. AI TRIAGE
    # -----------------------------------------------------

    try:
        client = get_llm_client()

        prompt = f"""
Classify this customer support message.

Choose exactly one category:
- billing
- bug
- feature
- other

Choose exactly one urgency:
- low
- normal
- high

Return ONLY valid JSON.

Format:

{{
  "category": "billing",
  "urgency": "normal",
  "confidence": 0.0,
  "reason": "short explanation"
}}

Customer message:
{submission.message}
"""

        response = client.chat.completions.create(
            model=os.environ["LLM_MODEL"],
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a customer support triage classifier. "
                        "Return only valid JSON."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        content = response.choices[0].message.content

        # Remove possible markdown code fences
        if content.startswith("```"):
            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()

        result = json.loads(content)

        category = result.get("category", "other")
        urgency = result.get("urgency", "normal")
        confidence = float(result.get("confidence", 0.5))
        reason = result.get(
            "reason",
            "No reason provided."
        )

    except Exception as e:
        print(f"LLM TRIAGE ERROR: {e}")

    # -----------------------------------------------------
    # 4. Save submission
    # -----------------------------------------------------

    new_submission = Submission(
        widget_id=widget.id,
        name=submission.name,
        email=submission.email,
        message=submission.message
    )

    try:
        db.add(new_submission)
        db.commit()
        db.refresh(new_submission)

    except SQLAlchemyError:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to save submission"
        )

    # -----------------------------------------------------
    # 5. Return submission
    # -----------------------------------------------------

    return new_submission
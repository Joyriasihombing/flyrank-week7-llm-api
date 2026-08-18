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
from app.llm.prompts import TRIAGE_PROMPT
from app.llm.schema import TriageResponse
from app.llm.cost import log_llm_usage

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

    llm_enabled = (
        os.getenv("LLM_ENABLED", "true").lower() == "true"
    )

    if llm_enabled:
        try:
            client = get_llm_client()

            prompt = TRIAGE_PROMPT.format(
                text=submission.message
            )

            # =================================================
            # FIRST LLM REQUEST
            # =================================================

            response = client.chat.completions.create(
                model=os.environ["LLM_MODEL"],
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a customer support "
                            "triage classifier. "
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

            # =================================================
            # LOG FIRST LLM USAGE
            # =================================================

            usage = response.usage

            if usage:
                log_llm_usage(
                    model=os.environ["LLM_MODEL"],
                    prompt_tokens=usage.prompt_tokens,
                    completion_tokens=usage.completion_tokens,
                    total_tokens=usage.total_tokens
                )

            # =================================================
            # GET CONTENT
            # =================================================

            content = response.choices[0].message.content

            if not content:
                raise ValueError(
                    "LLM returned empty response"
                )

            content = content.strip()

            # Remove markdown code fences
            if content.startswith("```"):
                content = (
                    content
                    .replace("```json", "")
                    .replace("```", "")
                    .strip()
                )

            # =================================================
            # VALIDATE FIRST RESPONSE
            # =================================================

            try:
                result = TriageResponse.model_validate_json(
                    content
                )

            except Exception as validation_error:

                print(
                    "LLM validation failed. "
                    f"Starting repair retry: {validation_error}"
                )

                # =================================================
                # REPAIR REQUEST
                # =================================================

                repair_prompt = f"""
Convert the following model output into valid JSON.

The JSON MUST follow this exact structure:

{{
  "category": "billing|bug|feature|other",
  "urgency": "low|normal|high",
  "confidence": 0.0,
  "reason": "short explanation"
}}

Rules:
- category must be exactly one of billing, bug, feature, other
- urgency must be exactly one of low, normal, high
- confidence must be a number between 0 and 1
- reason must be a short string
- return ONLY JSON
- do not use markdown
- do not add extra fields

Invalid model output:

{content}
"""

                repair_response = client.chat.completions.create(
                    model=os.environ["LLM_MODEL"],
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a JSON repair assistant. "
                                "Return ONLY valid JSON."
                            )
                        },
                        {
                            "role": "user",
                            "content": repair_prompt
                        }
                    ],
                    temperature=0
                )

                # =================================================
                # LOG REPAIR USAGE
                # =================================================

                repair_usage = repair_response.usage

                if repair_usage:
                    log_llm_usage(
                        model=os.environ["LLM_MODEL"],
                        prompt_tokens=repair_usage.prompt_tokens,
                        completion_tokens=repair_usage.completion_tokens,
                        total_tokens=repair_usage.total_tokens
                    )

                # =================================================
                # GET REPAIRED CONTENT
                # =================================================

                repaired_content = (
                    repair_response.choices[0].message.content
                )

                if not repaired_content:
                    raise ValueError(
                        "Repair attempt returned empty response"
                    )

                repaired_content = repaired_content.strip()

                if repaired_content.startswith("```"):
                    repaired_content = (
                        repaired_content
                        .replace("```json", "")
                        .replace("```", "")
                        .strip()
                    )

                # =================================================
                # VALIDATE REPAIRED RESPONSE
                # =================================================

                result = TriageResponse.model_validate_json(
                    repaired_content
                )

                print("LLM repair successful.")

            # =================================================
            # USE VALIDATED RESULT
            # =================================================

            category = result.category.value
            urgency = result.urgency.value
            confidence = result.confidence
            reason = result.reason

            print(
                "LLM TRIAGE SUCCESS: "
                f"category={category}, "
                f"urgency={urgency}, "
                f"confidence={confidence}, "
                f"reason={reason}"
            )

        except Exception as e:
            print(
                f"LLM TRIAGE ERROR: {e}"
            )

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
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.submission import Submission
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.widget import Widget
from app.schemas.widget import WidgetCreate

router = APIRouter()
@router.get("/")

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


@router.get("/")
def get_widgets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    widgets = db.query(Widget).filter(
        Widget.user_id == current_user.id
    ).all()

    return widgets


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

    submissions = db.query(Submission).filter(
        Submission.widget_id == widget.id
    ).all()

    return submissions

@router.get("/dashboard/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    widget_count = db.query(Widget).filter(
        Widget.user_id == current_user.id
    ).count()

    submission_count = (
        db.query(Submission)
        .join(Widget)
        .filter(Widget.user_id == current_user.id)
        .count()
    )

    return {
        "total_widgets": widget_count,
        "total_submissions": submission_count
    }

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

    submissions = db.query(Submission).filter(
        Submission.widget_id == widget.id
    ).all()

    return submissions

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
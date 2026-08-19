from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import List

from database import get_db
from models import Notification, Product, User
from auth import verify_token

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)


# Pydantic models
class NotificationCreate(BaseModel):
    product_id: int
    alert_type: str  # LOW_STOCK, EXPIRY, DEMAND, etc.
    title: str
    message: str
    severity: str  # CRITICAL, WARNING, INFO


class NotificationResponse(BaseModel):
    id: int
    product_id: int
    alert_type: str
    title: str
    message: str
    severity: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationMarkRead(BaseModel):
    notification_ids: List[int]


# Endpoints
@router.get("/", response_model=List[NotificationResponse])
def get_user_notifications(
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get notifications for current user"""
    
    try:
        # Get user
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Build query
        query = db.query(Notification).filter(
            Notification.user_id == user.id
        )
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        # Get notifications sorted by newest first
        notifications = query.order_by(
            desc(Notification.created_at)
        ).offset(skip).limit(limit).all()
        
        return notifications
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving notifications: {str(e)}"
        )


@router.get("/unread-count")
def get_unread_count(
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        count = db.query(Notification).filter(
            Notification.user_id == user.id,
            Notification.is_read == False
        ).count()
        
        return {"unread_count": count}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error counting notifications: {str(e)}"
        )


@router.patch("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Mark a specific notification as read"""
    
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user.id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        notification.is_read = True
        db.commit()
        db.refresh(notification)
        
        return notification
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating notification: {str(e)}"
        )


@router.patch("/read-all")
def mark_all_read(
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Mark all notifications as read"""
    
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        db.query(Notification).filter(
            Notification.user_id == user.id,
            Notification.is_read == False
        ).update({"is_read": True})
        
        db.commit()
        
        return {"message": "All notifications marked as read"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking notifications: {str(e)}"
        )


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Delete a notification"""
    
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        notification = db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user.id
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        db.delete(notification)
        db.commit()
        
        return {"message": "Notification deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting notification: {str(e)}"
        )


# Internal helper functions
def create_notification(
    db: Session,
    user_id: int,
    product_id: int,
    alert_type: str,
    title: str,
    message: str,
    severity: str
):
    """Create a new notification (internal use)"""
    
    try:
        notification = Notification(
            user_id=user_id,
            product_id=product_id,
            alert_type=alert_type,
            title=title,
            message=message,
            severity=severity
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification
    except Exception as e:
        db.rollback()
        raise Exception(f"Failed to create notification: {str(e)}")


def create_alert_notifications(db: Session, alerts: list, admin_user_id: int = 1):
    """Create notifications for all alerts (called from alerts.py)"""
    
    try:
        for alert in alerts:
            title = f"⚠️ {alert['alert_type']}: {alert['product_name']}"
            
            if alert['alert_type'] == 'LOW_STOCK':
                message = f"Stock for {alert['product_name']} is at {alert['current_stock']} units (Minimum: {alert['minimum_stock']})"
                severity = "CRITICAL" if alert['severity'] == "CRITICAL" else "WARNING"
            else:
                message = alert.get('message', 'New alert')
                severity = alert.get('severity', 'INFO')
            
            create_notification(
                db,
                user_id=admin_user_id,
                product_id=alert['product_id'],
                alert_type=alert['alert_type'],
                title=title,
                message=message,
                severity=severity
            )
    except Exception as e:
        print(f"Error creating alert notifications: {str(e)}")


def cleanup_old_notifications(db: Session, days: int = 30):
    """Delete notifications older than specified days"""
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        db.query(Notification).filter(
            Notification.created_at < cutoff_date,
            Notification.is_read == True  # Only delete read notifications
        ).delete()
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error cleaning up notifications: {str(e)}")

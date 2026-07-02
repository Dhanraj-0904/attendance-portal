from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Center, User
from ..schemas import CenterCreate, CenterResponse
from .auth import get_current_user, require_role, log_action

router = APIRouter(prefix="/centers", tags=["Centers"])

@router.get("/", response_model=List[CenterResponse])
def get_centers(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Center).all()

@router.get("/{id}", response_model=CenterResponse)
def get_center_by_id(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    center = db.query(Center).filter(Center.id == id).first()
    if not center:
        raise HTTPException(status_code=404, detail="Center not found")
    return center

@router.post("/", response_model=CenterResponse)
def create_center(
    center_in: CenterCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(["admin"]))
):
    nsdc_code = center_in.nsdc_center_code
    if not nsdc_code:
        import time
        nsdc_code = f"NSDC_{int(time.time())}"

    dup = db.query(Center).filter(Center.nsdc_center_code == nsdc_code).first()
    if dup:
        raise HTTPException(status_code=400, detail="NSDC center code already registered")

    new_center = Center(
        name=center_in.name,
        district=center_in.district,
        state=center_in.state,
        nsdc_center_code=nsdc_code
    )
    db.add(new_center)
    db.commit()
    db.refresh(new_center)
    
    log_action(db, current_user.id, "create_center", "centers", new_center.id)
    return new_center

@router.put("/{id}", response_model=CenterResponse)
def update_center(
    id: int, 
    center_in: CenterCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(["admin"]))
):
    center = db.query(Center).filter(Center.id == id).first()
    if not center:
        raise HTTPException(status_code=404, detail="Center not found")

    nsdc_code = center_in.nsdc_center_code
    if not nsdc_code:
        nsdc_code = center.nsdc_center_code

    center.name = center_in.name
    center.district = center_in.district
    center.state = center_in.state
    center.nsdc_center_code = nsdc_code
    
    db.commit()
    db.refresh(center)
    
    log_action(db, current_user.id, "update_center", "centers", center.id)
    return center

@router.delete("/{id}")
def delete_center(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role(["admin"]))
):
    center = db.query(Center).filter(Center.id == id).first()
    if not center:
        raise HTTPException(status_code=404, detail="Center not found")
        
    db.delete(center)
    db.commit()
    
    log_action(db, current_user.id, "delete_center", "centers", id)
    return {"message": f"Center {id} deleted successfully"}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.PositionResponse])
def list_positions(db: Session = Depends(get_db)):
    return crud.get_positions(db)


@router.get("/{position_id}", response_model=schemas.PositionResponse)
def read_position(position_id: int, db: Session = Depends(get_db)):
    pos = crud.get_position(db, position_id)
    if not pos:
        raise HTTPException(status_code=404, detail="职位不存在")
    return pos


@router.post("/", response_model=schemas.PositionResponse, status_code=201)
def add_position(position: schemas.PositionCreate, db: Session = Depends(get_db)):
    return crud.create_position(db, position)


@router.put("/{position_id}", response_model=schemas.PositionResponse)
def edit_position(position_id: int, position: schemas.PositionCreate, db: Session = Depends(get_db)):
    pos = crud.update_position(db, position_id, position)
    if not pos:
        raise HTTPException(status_code=404, detail="职位不存在")
    return pos


@router.delete("/{position_id}")
def remove_position(position_id: int, db: Session = Depends(get_db)):
    if not crud.delete_position(db, position_id):
        raise HTTPException(status_code=404, detail="职位不存在")
    return {"detail": "删除成功"}

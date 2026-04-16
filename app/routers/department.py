from fastapi import APIRouter,Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db

router = APIRouter()

@router.get('/',
response_model=list[schemas.DepartmentResponse])
def list_departments(db: Session = Depends(get_db)):
    return crud.get_departments(db)

@router.get("/{department_id}",response_model=schemas.DepartmentResponse)
def read_department(department_id:int,db:Session = Depends(get_db)):
    dept = crud.get_department(db,department_id)
    if not dept:
        raise HTTPException(status_code=404,detail="部门不存在")
    return dept

@router.post("/", response_model=schemas.DepartmentResponse, status_code=201)
def add_department(department: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    return crud.create_department(db, department)

@router.put("/{department_id}", response_model=schemas.DepartmentResponse)
def edit_department(department_id: int, department: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    dept = crud.update_department(db, department_id, department)
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    return dept

@router.delete("/{department_id}")
def remove_department(department_id: int, db: Session = Depends(get_db)):
    if not crud.delete_department(db, department_id):
        raise HTTPException(status_code=404, detail="部门不存在")
    return {"detail": "删除成功"}

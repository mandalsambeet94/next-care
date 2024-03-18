import logging
from typing import Optional

from sqlalchemy.orm import Session
from app.schemas.user import CaseCreate, CaseUpdate
from app.models.doctor import Doctor
from app.models.user_upload import UserUpload
from sqlalchemy.exc import IntegrityError
from app.crud.base import CRUDBase
from fastapi import HTTPException
from typing import Any, Dict, List, Optional, Union
from sqlalchemy import or_, func, and_

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CRUDCase(CRUDBase[Doctor, CaseCreate, CaseUpdate]):

    def get_by_patient_user_id(self, db: Session, *, user_id: str) -> Optional[Doctor]:
        return db.query(self.model).filter(Doctor.patient_user_id == user_id).first()

    def create(self, db: Session, *, obj_in: CaseCreate) -> Doctor:

        try:
            db_obj = Doctor()
            db_obj.doctor_user_id = obj_in.doctor_user_id
            db_obj.patient_user_id = obj_in.patient_user_id
            db_obj.status = 'In Progress'

            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        except IntegrityError as ie:
            logger.error("DB error occured", exc_info=True)
            print("dwqdwqdwqd", ie.detail)
            raise HTTPException(
                status_code=500,
                detail=str(ie.orig),
            )
        except Exception as e:
            logger.error("Error creating the case", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Error creating case...",
            )

        return db_obj

    def update_case(
            self,
            db: Session,
            *,
            db_obj: Doctor,
            obj_in: Union[CaseUpdate, Dict[str, Any]],
    ) -> Doctor:
        updated_case = None
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        try:
            print("dscsadhcb: ", update_data)
            updated_case = super().update(db, db_obj=db_obj, obj_in=update_data)
        except IntegrityError as ie:
            logger.error("DB error occured", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=str(ie.orig)
            )
        return updated_case

    def get_doctor_list(self, db: Session, status: int, doctor_user_id: str, skip: int = 0, limit: int = 10) -> List[
        Dict]:
        case_items = None
        print("doc id: ", type(doctor_user_id))
        if not doctor_user_id:
            case_items = db.query(self.model).filter(or_(self.model.status == status)).all()
            print("if case items", case_items)
        else:
            case_items = db.query(self.model). \
                filter(and_(self.model.status == status, self.model.doctor_user_id == doctor_user_id)). \
                all()
            print("else case items", case_items)

        print("case items: ", case_items)
        user_ids = [obj.patient_user_id for obj in case_items]
        print("user ids: ", user_ids)
        # image_path_items = db.query(UserUpload).filter(UserUpload.user_id.in_(user_ids)).all()
        image_path_items = db.query(UserUpload). \
            filter(UserUpload.user_id.in_(user_ids)). \
            filter(func.DATE(UserUpload.created_at) == func.DATE(case_items[0].created_at)). \
            all()

        item_dicts = [
            {
                "case_id": case_item.case_id,
                "doctor_user_id": case_item.doctor_user_id,
                "patient_user_id": case_item.patient_user_id,
                # Add more fields as needed
                "status": case_item.status,
                "insights":case_item.insights,
                "created_at": case_item.created_at,
                "image_path": image_path_item.image_path
            }
            for case_item, image_path_item in zip(case_items, image_path_items)
            if case_item.patient_user_id == image_path_item.user_id
        ]

        return item_dicts


case = CRUDCase(Doctor)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import models
from app.schemas import investment_recommendation as schemas
from app.db.database import get_db

router = APIRouter(
    prefix="/investment-recommendations",
    tags=["investment-recommendations"]
)


# =============== GET Endpoints ===============

@router.get("/{cryptocurrency_id}", response_model=schemas.InvestmentRecommendationResponse)
async def get_investment_recommendations_by_crypto(
    cryptocurrency_id: int,
    db: Session = Depends(get_db)
):
    """
    ดึงข้อมูล investment recommendations โดยระบุ cryptocurrency_id

    - **cryptocurrency_id**: ID ของ cryptocurrency ที่ต้องการดูคำแนะนำการลงทุน
    - ไม่ต้องใช้ Token (public endpoint)
    - จะคืนค่าเป็น list ของคำแนะนำการลงทุนทั้งหมดสำหรับ cryptocurrency นี้
    - เรียงลำดับจาก analysis_date ล่าสุดไปเก่าสุด
    """
    # Query investment recommendations
    recommendations = db.query(models.InvestmentRecommendation).filter(
        models.InvestmentRecommendation.cryptocurrency_id == cryptocurrency_id
    ).order_by(
        models.InvestmentRecommendation.analysis_date.desc()
    ).first()

    if not recommendations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No investment recommendations found for cryptocurrency_id {cryptocurrency_id}"
        )

    return recommendations

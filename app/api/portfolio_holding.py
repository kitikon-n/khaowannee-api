from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.db import models
from app.schemas import portfolio_holding as schemas
from app.db.database import get_db
from app.api.suuser import get_current_user

router = APIRouter(
    prefix="/portfolio-holdings",
    tags=["portfolio-holdings"]
)


# =============== GET Endpoint ===============

@router.get("/", response_model=List[schemas.PortfolioHoldingResponse])
async def get_all_portfolio_holdings(
    portfolio_id: int = Query(..., description="Portfolio ID ที่ต้องการดูข้อมูล"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ดึงข้อมูล portfolio holdings ตาม portfolio_id ที่ระบุ

    - **portfolio_id**: ID ของ portfolio ที่ต้องการดูข้อมูล (required)
    - ต้องใช้ Token ใน Header: Authorization: Bearer <your_token>
    - จะตรวจสอบว่า portfolio นี้เป็นของ user ที่ login หรือไม่
    - รวมข้อมูล portfolio_name, cryptocurrency_symbol, cryptocurrency_name
    """
    # ตรวจสอบว่า portfolio นี้เป็นของ user ที่ login หรือไม่
    portfolio = db.query(models.Portfolio).filter(
        models.Portfolio.id == portfolio_id,
        models.Portfolio.user_id == current_user.user_id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found or does not belong to current user"
        )

    # Query with JOIN เพื่อดึงข้อมูลเพิ่มเติม และ filter ด้วย portfolio_id
    results = db.query(
        models.PortfolioHolding,
        models.Portfolio.name.label('portfolio_name'),
        models.Cryptocurrency.symbol.label('cryptocurrency_symbol'),
        models.Cryptocurrency.name.label('cryptocurrency_name')
    ).join(
        models.Portfolio,
        models.PortfolioHolding.portfolio_id == models.Portfolio.id
    ).join(
        models.Cryptocurrency,
        models.PortfolioHolding.cryptocurrency_id == models.Cryptocurrency.id
    ).filter(
        models.PortfolioHolding.portfolio_id == portfolio_id
    ).all()

    # แปลงผลลัพธ์เป็น list of dict
    holdings = []
    for holding, portfolio_name, crypto_symbol, crypto_name in results:
        holding_dict = {
            "id": holding.id,
            "portfolio_id": holding.portfolio_id,
            "cryptocurrency_id": holding.cryptocurrency_id,
            "quantity": holding.quantity,
            "average_buy_price": holding.average_buy_price,
            "total_invested": holding.total_invested,
            "current_price": holding.current_price,
            "current_value": holding.current_value,
            "profit_loss": holding.profit_loss,
            "profit_loss_percentage": holding.profit_loss_percentage,
            "created_by": holding.created_by,
            "created_date": holding.created_date,
            "created_program": holding.created_program,
            "updated_by": holding.updated_by,
            "updated_date": holding.updated_date,
            "updated_program": holding.updated_program,
            "portfolio_name": portfolio_name,
            "cryptocurrency_symbol": crypto_symbol,
            "cryptocurrency_name": crypto_name
        }
        holdings.append(holding_dict)

    return holdings

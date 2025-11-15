from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from datetime import datetime

from app.db import models
from app.schemas import portfolio as schemas
from app.db.database import get_db
from app.api.suuser import get_current_user

router = APIRouter(
    prefix="/portfolios",
    tags=["portfolios"]
)


# =============== GET Endpoints ===============

@router.get("/", response_model=List[schemas.PortfolioResponse])
async def get_all_portfolios(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ดึงข้อมูล portfolios ทั้งหมดของ user ที่ login

    - ต้องใช้ Token ใน Header: Authorization: Bearer <your_token>
    - จะคืนค่าเฉพาะ portfolios ของ user ที่ login เท่านั้น
    - รวมข้อมูล asset_name จาก db_list_value_lang
    - คำนวณ total_invested, current_value, profit_loss จาก transactions และ price_data
    """
    # Query portfolios with calculated values from transactions
    query = text("""
        SELECT 
            p.id
            , p.user_id 
            , p."name" 
            , p.description 
            , p.profit_loss_percentage 
            , p.asset 
            , COALESCE(lvl.value_text, p.asset) as asset_name
            , sum(COALESCE (t.total_amount, 0)) total_invested
            , sum(COALESCE (pd.close_price, 0) * COALESCE (t.quantity, 0)) current_value
            , (sum(COALESCE (pd.close_price, 0) * COALESCE (t.quantity, 0)) - sum(COALESCE (t.total_amount, 0))) profit_loss
            , p.created_by
            , p.created_date
            , p.created_program
            , p.updated_by
            , p.updated_date
            , p.updated_program
        FROM portfolios p
            LEFT JOIN transactions t 
                ON p.id = t.portfolio_id 
            LEFT JOIN price_data pd 
                ON pd.cryptocurrency_id = t.cryptocurrency_id
            LEFT JOIN db_list_value_lang lvl
                ON lvl.value = p.asset
                AND lvl.language_code = 'TH'
        WHERE user_id = 4
        GROUP BY p.id
            , p.user_id 
            , p."name"  
            , p.description 
            , p.profit_loss_percentage 
            , p.asset 
            , lvl.value_text
            , p.created_by
            , p.created_date
            , p.created_program
            , p.updated_by
            , p.updated_date
            , p.updated_program
        ORDER BY p.id desc
    """)

    results = db.execute(query, {"user_id": current_user.user_id})

    # แปลงผลลัพธ์เป็น list of dict
    portfolios = []
    for row in results:
        portfolio_dict = {
            "id": row.id,
            "user_id": row.user_id,
            "name": row.name,
            "description": row.description,
            "total_invested": float(row.total_invested) if row.total_invested else 0,
            "current_value": float(row.current_value) if row.current_value else 0,
            "profit_loss": float(row.profit_loss) if row.profit_loss else 0,
            "profit_loss_percentage": float(row.profit_loss_percentage) if row.profit_loss_percentage else 0,
            "asset": row.asset,
            "asset_name": row.asset_name,
            "created_by": row.created_by,
            "created_date": row.created_date,
            "created_program": row.created_program,
            "updated_by": row.updated_by,
            "updated_date": row.updated_date,
            "updated_program": row.updated_program
        }
        portfolios.append(portfolio_dict)

    return portfolios


@router.get("/{portfolio_id}", response_model=schemas.PortfolioResponse)
async def get_portfolio(
    portfolio_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ดึงข้อมูล portfolio เดียวโดยระบุ ID

    - ต้องใช้ Token ใน Header: Authorization: Bearer <your_token>
    - จะตรวจสอบว่า portfolio นี้เป็นของ user ที่ login หรือไม่
    - รวมข้อมูล asset_name จาก db_list_value_lang
    """
    # Query with LEFT JOIN to get asset_name
    result = db.query(
        models.Portfolio,
        models.DBListValueLang.value_text.label('asset_name')
    ).outerjoin(
        models.DBListValueLang,
        (models.DBListValueLang.value == models.Portfolio.asset) &
        (models.DBListValueLang.language_code == 'TH')
    ).filter(
        models.Portfolio.id == portfolio_id,
        models.Portfolio.user_id == current_user.user_id
    ).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found or does not belong to current user"
        )

    portfolio, asset_name = result

    # แปลงเป็น dict เพื่อรวม asset_name
    portfolio_dict = {
        "id": portfolio.id,
        "user_id": portfolio.user_id,
        "name": portfolio.name,
        "description": portfolio.description,
        "total_invested": portfolio.total_invested,
        "current_value": portfolio.current_value,
        "profit_loss": portfolio.profit_loss,
        "profit_loss_percentage": portfolio.profit_loss_percentage,
        "asset": portfolio.asset,
        "asset_name": asset_name,
        "created_by": portfolio.created_by,
        "created_date": portfolio.created_date,
        "created_program": portfolio.created_program,
        "updated_by": portfolio.updated_by,
        "updated_date": portfolio.updated_date,
        "updated_program": portfolio.updated_program
    }

    return portfolio_dict


@router.get("/{portfolio_id}/detail", response_model=schemas.PortfolioDetailResponse)
async def get_portfolio_detail(
    portfolio_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ดึงข้อมูล portfolio detail พร้อมข้อมูล nested (holdings, transactions)

    - ต้องใช้ Token ใน Header: Authorization: Bearer <your_token>
    - จะตรวจสอบว่า portfolio นี้เป็นของ user ที่ login หรือไม่
    - รวมข้อมูล:
      - portfolio_holdings: รายการ holdings ทั้งหมด
      - transactions: รายการ transactions ทั้งหมด (เรียงจากใหม่ไปเก่า)
      - analysis: [] (ยังไม่มีข้อมูล)
      - overview: [] (ยังไม่มีข้อมูล)
    """
    # Query portfolio with LEFT JOIN to get asset_name
    result = db.query(
        models.Portfolio,
        models.DBListValueLang.value_text.label('asset_name')
    ).outerjoin(
        models.DBListValueLang,
        (models.DBListValueLang.value == models.Portfolio.asset) &
        (models.DBListValueLang.language_code == 'TH')
    ).filter(
        models.Portfolio.id == portfolio_id,
        models.Portfolio.user_id == current_user.user_id
    ).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found or does not belong to current user"
        )

    portfolio, asset_name = result

    # Query holdings with cryptocurrency info
    holdings_results = db.query(
        models.PortfolioHolding,
        models.Cryptocurrency.symbol.label('cryptocurrency_symbol'),
        models.Cryptocurrency.name.label('cryptocurrency_name')
    ).join(
        models.Cryptocurrency,
        models.PortfolioHolding.cryptocurrency_id == models.Cryptocurrency.id
    ).filter(
        models.PortfolioHolding.portfolio_id == portfolio_id
    ).all()

    # Query transactions with cryptocurrency info
    transactions_results = db.query(
        models.Transaction,
        models.Cryptocurrency.symbol.label('cryptocurrency_symbol'),
        models.Cryptocurrency.name.label('cryptocurrency_name')
    ).join(
        models.Cryptocurrency,
        models.Transaction.cryptocurrency_id == models.Cryptocurrency.id
    ).filter(
        models.Transaction.portfolio_id == portfolio_id
    ).order_by(
        models.Transaction.transaction_date.desc()
    ).all()

    # Build holdings list
    holdings = []
    for holding, crypto_symbol, crypto_name in holdings_results:
        # ดึงราคาล่าสุดจาก price_data
        price_query = text("""
            SELECT close_price
            FROM price_data
            WHERE cryptocurrency_id = :cryptocurrency_id
            ORDER BY price_timestamp DESC
            LIMIT 1
        """)
        price_result = db.execute(price_query, {"cryptocurrency_id": holding.cryptocurrency_id})
        price_row = price_result.fetchone()
        latest_price = float(price_row.close_price) if price_row and price_row.close_price else None

        holdings.append({
            "id": holding.id,
            "portfolio_id": holding.portfolio_id,
            "cryptocurrency_id": holding.cryptocurrency_id,
            "quantity": holding.quantity,
            "average_buy_price": holding.average_buy_price,
            "total_invested": holding.total_invested,
            "current_price": latest_price,  # ใช้ราคาล่าสุดจาก price_data
            "current_value": holding.current_value,
            "profit_loss": holding.profit_loss,
            "profit_loss_percentage": holding.profit_loss_percentage,
            "cryptocurrency_symbol": crypto_symbol,
            "cryptocurrency_name": crypto_name,
            "created_by": holding.created_by,
            "created_date": holding.created_date
        })

    # Build transactions list
    transactions = []
    for transaction, crypto_symbol, crypto_name in transactions_results:
        transactions.append({
            "id": transaction.id,
            "portfolio_id": transaction.portfolio_id,
            "cryptocurrency_id": transaction.cryptocurrency_id,
            "transaction_type": transaction.transaction_type,
            "quantity": transaction.quantity,
            "price_per_unit": transaction.price_per_unit,
            "total_amount": transaction.total_amount,
            "fee": transaction.fee,
            "transaction_date": transaction.transaction_date,
            "notes": transaction.notes,
            "cryptocurrency_symbol": crypto_symbol,
            "cryptocurrency_name": crypto_name,
            "created_by": transaction.created_by,
            "created_date": transaction.created_date
        })

    # Query overview data
    overview_query = text("""
        SELECT
            ph.cryptocurrency_id
            , c.symbol
            , pd.close_price AS current_price
            , ph.quantity
            , ph.total_invested
            , COALESCE(ph.quantity, 0) * COALESCE(pd.close_price, 0) AS current_value
            , (COALESCE(ph.quantity, 0) * COALESCE(pd.close_price, 0)) - COALESCE(ph.total_invested, 0) AS unrealized_gain
        FROM portfolio_holdings ph
            JOIN cryptocurrencies c
                ON c.id = ph.cryptocurrency_id
            LEFT JOIN (
                SELECT
                    pd1.cryptocurrency_id,
                    pd1.close_price
                FROM price_data pd1
                INNER JOIN (
                    SELECT
                        cryptocurrency_id,
                        MAX(price_timestamp) as max_timestamp
                    FROM price_data
                    GROUP BY cryptocurrency_id
                ) pd2 ON pd1.cryptocurrency_id = pd2.cryptocurrency_id
                    AND pd1.price_timestamp = pd2.max_timestamp
            ) pd ON pd.cryptocurrency_id = ph.cryptocurrency_id
        WHERE ph.portfolio_id = :p_portfolio_id
    """)
    overview_results = db.execute(overview_query, {"p_portfolio_id": portfolio_id})

    # Build overview list
    overview = []
    for row in overview_results:
        overview.append({
            "cryptocurrency_id": row.cryptocurrency_id,
            "symbol": row.symbol,
            "currentPrice": float(row.current_price) if row.current_price else None,
            "quantity": float(row.quantity) if row.quantity else 0,
            "total_invested": float(row.total_invested) if row.total_invested else 0,
            "currentValue": float(row.current_value) if row.current_value else 0,
            "unrealizedGain": float(row.unrealized_gain) if row.unrealized_gain else 0
        })

    # Build portfolio detail response
    portfolio_detail = {
        "id": portfolio.id,
        "user_id": portfolio.user_id,
        "name": portfolio.name,
        "description": portfolio.description,
        "total_invested": portfolio.total_invested,
        "current_value": portfolio.current_value,
        "profit_loss": portfolio.profit_loss,
        "profit_loss_percentage": portfolio.profit_loss_percentage,
        "created_by": portfolio.created_by,
        "created_date": portfolio.created_date,
        "created_program": portfolio.created_program,
        "updated_by": portfolio.updated_by,
        "updated_date": portfolio.updated_date,
        "updated_program": portfolio.updated_program,
        "asset": portfolio.asset,
        "asset_name": asset_name,
        "portfolio_holdings": holdings,
        "transactions": transactions,
        "analysis": [],  # TODO: เพิ่มข้อมูล analysis ในอนาคต
        "overview": overview
    }

    return portfolio_detail


# =============== POST Endpoint (Create) ===============

@router.post("/", response_model=schemas.PortfolioResponse, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    portfolio_data: schemas.PortfolioCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    สร้าง portfolio ใหม่สำหรับ user ที่ login

    - **name**: ชื่อ portfolio (required)
    - **description**: รายละเอียด portfolio (optional)
    - **asset**: ประเภทสินทรัพย์ (optional)

    ต้องใช้ Token ใน Header: Authorization: Bearer <your_token>
    """
    # สร้าง portfolio ใหม่
    new_portfolio = models.Portfolio(
        user_id=current_user.user_id,
        name=portfolio_data.name,
        description=portfolio_data.description,
        asset=portfolio_data.asset,
        total_invested=portfolio_data.total_invested,
        current_value=0,
        profit_loss=0,
        profit_loss_percentage=0,
        created_by=current_user.user_name,
        created_date=datetime.now(),
        created_program="api"
    )

    db.add(new_portfolio)
    db.commit()
    db.refresh(new_portfolio)

    return new_portfolio


# =============== PUT Endpoint (Update) ===============

@router.put("/{portfolio_id}", response_model=schemas.PortfolioResponse)
async def update_portfolio(
    portfolio_id: int,
    portfolio_data: schemas.PortfolioUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    แก้ไขข้อมูล portfolio

    - ต้องใช้ Token ใน Header: Authorization: Bearer <your_token>
    - จะตรวจสอบว่า portfolio นี้เป็นของ user ที่ login หรือไม่
    - ส่งเฉพาะฟิลด์ที่ต้องการแก้ไข (ไม่จำเป็นต้องส่งทุกฟิลด์)
    """
    # ค้นหา portfolio
    portfolio = db.query(models.Portfolio).filter(
        models.Portfolio.id == portfolio_id,
        models.Portfolio.user_id == current_user.user_id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found or does not belong to current user"
        )

    # อัพเดทเฉพาะฟิลด์ที่ส่งมา
    update_data = portfolio_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(portfolio, field, value)

    # อัพเดท metadata
    portfolio.updated_by = current_user.user_name
    portfolio.updated_date = datetime.now()
    portfolio.updated_program = "api"

    db.commit()
    db.refresh(portfolio)

    return portfolio


# =============== DELETE Endpoint ===============

@router.delete("/{portfolio_id}", status_code=status.HTTP_200_OK)
async def delete_portfolio(
    portfolio_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ลบ portfolio

    - ต้องใช้ Token ใน Header: Authorization: Bearer <your_token>
    - จะตรวจสอบว่า portfolio นี้เป็นของ user ที่ login หรือไม่
    - จะลบ holdings และ transactions ที่เกี่ยวข้องด้วย (cascade delete)
    """
    # ค้นหา portfolio
    portfolio = db.query(models.Portfolio).filter(
        models.Portfolio.id == portfolio_id,
        models.Portfolio.user_id == current_user.user_id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {portfolio_id} not found or does not belong to current user"
        )

    # ลบ portfolio
    db.delete(portfolio)
    db.commit()

    return {
        "message": f"Portfolio '{portfolio.name}' (id: {portfolio_id}) has been deleted successfully"
    }

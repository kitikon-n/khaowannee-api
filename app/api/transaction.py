from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
from datetime import datetime

from app.db import models
from app.schemas import transaction as schemas
from app.db.database import get_db
from app.api.suuser import get_current_user

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"]
)


# =============== Helper Functions ===============

def update_portfolio_holdings(db: Session, portfolio_id: int, cryptocurrency_id: int, username: str):
    """
    อัปเดตข้อมูลสรุปใน portfolio_holdings หลังจากมีการเปลี่ยนแปลง transactions

    Args:
        db: Database session
        portfolio_id: ID ของ portfolio
        cryptocurrency_id: ID ของ cryptocurrency
        username: Username ของผู้ใช้ (สำหรับ audit log)
    """
    try:
        # คำนวณ summary จาก transactions
        query = text("""
            SELECT
                COALESCE(SUM(quantity), 0) as total_quantity,
                COALESCE(SUM(total_amount), 0) as total_invested
            FROM transactions
            WHERE portfolio_id = :portfolio_id
            AND cryptocurrency_id = :cryptocurrency_id
        """)

        result = db.execute(query, {
            "portfolio_id": portfolio_id,
            "cryptocurrency_id": cryptocurrency_id
        })
        row = result.fetchone()

        total_quantity = float(row.total_quantity) if row.total_quantity else 0
        total_invested = float(row.total_invested) if row.total_invested else 0

        # ตรวจสอบว่ามี portfolio_holding อยู่แล้วหรือไม่
        existing_holding = db.query(models.PortfolioHolding).filter(
            models.PortfolioHolding.portfolio_id == portfolio_id,
            models.PortfolioHolding.cryptocurrency_id == cryptocurrency_id
        ).first()

        if existing_holding:
            # UPDATE
            existing_holding.quantity = total_quantity
            existing_holding.total_invested = total_invested
            existing_holding.updated_by = username
            existing_holding.updated_date = datetime.now()
            existing_holding.updated_program = "transaction_api_auto"
        else:
            # INSERT (เฉพาะกรณีที่มี quantity > 0)
            if total_quantity > 0:
                new_holding = models.PortfolioHolding(
                    portfolio_id=portfolio_id,
                    cryptocurrency_id=cryptocurrency_id,
                    quantity=total_quantity,
                    total_invested=total_invested,
                    created_by=username,
                    created_date=datetime.now(),
                    created_program="transaction_api_auto"
                )
                db.add(new_holding)

        db.commit()

    except Exception as e:
        db.rollback()
        raise Exception(f"Error updating portfolio_holdings: {e}")


# =============== GET Endpoint ===============

@router.get("/", response_model=List[schemas.TransactionResponse])
async def get_all_transactions(
    portfolio_id: int = Query(..., description="Portfolio ID ที่ต้องการดูข้อมูล"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ดึงข้อมูล transactions ตาม portfolio_id ที่ระบุ

    - **portfolio_id**: ID ของ portfolio ที่ต้องการดูข้อมูล (required)
    - ต้องใช้ Token ใน Header: Authorization: Bearer <your_token>
    - จะตรวจสอบว่า portfolio นี้เป็นของ user ที่ login หรือไม่
    - รวมข้อมูล portfolio_name, cryptocurrency_symbol, cryptocurrency_name
    - เรียงลำดับตาม transaction_date จากใหม่ไปเก่า
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
        models.Transaction,
        models.Portfolio.name.label('portfolio_name'),
        models.Cryptocurrency.symbol.label('cryptocurrency_symbol'),
        models.Cryptocurrency.name.label('cryptocurrency_name')
    ).join(
        models.Portfolio,
        models.Transaction.portfolio_id == models.Portfolio.id
    ).join(
        models.Cryptocurrency,
        models.Transaction.cryptocurrency_id == models.Cryptocurrency.id
    ).filter(
        models.Transaction.portfolio_id == portfolio_id
    ).order_by(
        models.Transaction.transaction_date.desc()
    ).all()

    # แปลงผลลัพธ์เป็น list of dict
    transactions = []
    for transaction, portfolio_name, crypto_symbol, crypto_name in results:
        transaction_dict = {
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
            "created_by": transaction.created_by,
            "created_date": transaction.created_date,
            "created_program": transaction.created_program,
            "updated_by": transaction.updated_by,
            "updated_date": transaction.updated_date,
            "updated_program": transaction.updated_program,
            "portfolio_name": portfolio_name,
            "cryptocurrency_symbol": crypto_symbol,
            "cryptocurrency_name": crypto_name
        }
        transactions.append(transaction_dict)

    return transactions


@router.get("/{transaction_id}", response_model=schemas.TransactionResponse)
async def get_transaction(
    transaction_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ดึงข้อมูล transaction เดี่ยวตาม ID

    - **transaction_id**: ID ของ transaction ที่ต้องการดู
    - ต้องใช้ Token ใน Header: Authorization: Bearer <your_token>
    - จะตรวจสอบว่า transaction นี้อยู่ใน portfolio ของ user หรือไม่
    """
    # Query with JOIN
    result = db.query(
        models.Transaction,
        models.Portfolio.name.label('portfolio_name'),
        models.Cryptocurrency.symbol.label('cryptocurrency_symbol'),
        models.Cryptocurrency.name.label('cryptocurrency_name')
    ).join(
        models.Portfolio,
        models.Transaction.portfolio_id == models.Portfolio.id
    ).join(
        models.Cryptocurrency,
        models.Transaction.cryptocurrency_id == models.Cryptocurrency.id
    ).filter(
        models.Transaction.id == transaction_id,
        models.Portfolio.user_id == current_user.user_id
    ).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {transaction_id} not found or does not belong to current user"
        )

    transaction, portfolio_name, crypto_symbol, crypto_name = result

    return {
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
        "created_by": transaction.created_by,
        "created_date": transaction.created_date,
        "created_program": transaction.created_program,
        "updated_by": transaction.updated_by,
        "updated_date": transaction.updated_date,
        "updated_program": transaction.updated_program,
        "portfolio_name": portfolio_name,
        "cryptocurrency_symbol": crypto_symbol,
        "cryptocurrency_name": crypto_name
    }


# =============== POST Endpoint ===============

@router.post("/", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: schemas.TransactionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    สร้าง transaction ใหม่

    - **portfolio_id**: ID ของ portfolio (required)
    - **cryptocurrency_id**: ID ของ cryptocurrency (required)
    - **transaction_type**: ประเภท transaction เช่น BUY, SELL (required)
    - **quantity**: จำนวน (required, > 0)
    - **price_per_unit**: ราคาต่อหน่วย (required, > 0)
    - **total_amount**: ยอดรวม (required, > 0)
    - **fee**: ค่าธรรมเนียม (optional, >= 0)
    - **transaction_date**: วันที่ทำธุรกรรม (required)
    - **notes**: หมายเหตุ (optional)
    - ต้องใช้ Token ใน Header: Authorization: Bearer <your_token>
    - จะตรวจสอบว่า portfolio เป็นของ user ที่ login หรือไม่
    """
    # ตรวจสอบว่า portfolio นี้เป็นของ user ที่ login หรือไม่
    portfolio = db.query(models.Portfolio).filter(
        models.Portfolio.id == transaction.portfolio_id,
        models.Portfolio.user_id == current_user.user_id
    ).first()

    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Portfolio with id {transaction.portfolio_id} not found or does not belong to current user"
        )

    # ตรวจสอบว่า cryptocurrency มีอยู่จริง
    cryptocurrency = db.query(models.Cryptocurrency).filter(
        models.Cryptocurrency.id == transaction.cryptocurrency_id
    ).first()

    if not cryptocurrency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cryptocurrency with id {transaction.cryptocurrency_id} not found"
        )

    # สร้าง transaction ใหม่
    new_transaction = models.Transaction(
        portfolio_id=transaction.portfolio_id,
        cryptocurrency_id=transaction.cryptocurrency_id,
        transaction_type=transaction.transaction_type,
        quantity=transaction.quantity,
        price_per_unit=transaction.price_per_unit,
        total_amount=transaction.total_amount,
        fee=transaction.fee,
        transaction_date=transaction.transaction_date,
        notes=transaction.notes,
        created_by=current_user.user_name,
        created_date=datetime.now(),
        created_program="transaction_api"
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    # อัปเดต portfolio_holdings
    update_portfolio_holdings(
        db=db,
        portfolio_id=transaction.portfolio_id,
        cryptocurrency_id=transaction.cryptocurrency_id,
        username=current_user.user_name
    )

    # ดึงข้อมูลเพิ่มเติมเพื่อส่งกลับ
    result = db.query(
        models.Transaction,
        models.Portfolio.name.label('portfolio_name'),
        models.Cryptocurrency.symbol.label('cryptocurrency_symbol'),
        models.Cryptocurrency.name.label('cryptocurrency_name')
    ).join(
        models.Portfolio,
        models.Transaction.portfolio_id == models.Portfolio.id
    ).join(
        models.Cryptocurrency,
        models.Transaction.cryptocurrency_id == models.Cryptocurrency.id
    ).filter(
        models.Transaction.id == new_transaction.id
    ).first()

    transaction_obj, portfolio_name, crypto_symbol, crypto_name = result

    return {
        "id": transaction_obj.id,
        "portfolio_id": transaction_obj.portfolio_id,
        "cryptocurrency_id": transaction_obj.cryptocurrency_id,
        "transaction_type": transaction_obj.transaction_type,
        "quantity": transaction_obj.quantity,
        "price_per_unit": transaction_obj.price_per_unit,
        "total_amount": transaction_obj.total_amount,
        "fee": transaction_obj.fee,
        "transaction_date": transaction_obj.transaction_date,
        "notes": transaction_obj.notes,
        "created_by": transaction_obj.created_by,
        "created_date": transaction_obj.created_date,
        "created_program": transaction_obj.created_program,
        "updated_by": transaction_obj.updated_by,
        "updated_date": transaction_obj.updated_date,
        "updated_program": transaction_obj.updated_program,
        "portfolio_name": portfolio_name,
        "cryptocurrency_symbol": crypto_symbol,
        "cryptocurrency_name": crypto_name
    }


# =============== PUT Endpoint ===============

@router.put("/{transaction_id}", response_model=schemas.TransactionResponse)
async def update_transaction(
    transaction_id: int,
    transaction_update: schemas.TransactionUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    อัพเดท transaction

    - **transaction_id**: ID ของ transaction ที่ต้องการแก้ไข
    - ส่งเฉพาะ field ที่ต้องการแก้ไข
    - ต้องใช้ Token ใน Header: Authorization: Bearer <your_token>
    - จะตรวจสอบว่า transaction นี้อยู่ใน portfolio ของ user หรือไม่
    """
    # ค้นหา transaction และตรวจสอบว่าเป็นของ user หรือไม่
    transaction = db.query(models.Transaction).join(
        models.Portfolio,
        models.Transaction.portfolio_id == models.Portfolio.id
    ).filter(
        models.Transaction.id == transaction_id,
        models.Portfolio.user_id == current_user.user_id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {transaction_id} not found or does not belong to current user"
        )

    # ถ้ามีการเปลี่ยน cryptocurrency_id ให้ตรวจสอบว่ามีอยู่จริง
    # if transaction_update.cryptocurrency_id is not None:
    #     cryptocurrency = db.query(models.Cryptocurrency).filter(
    #         models.Cryptocurrency.id == transaction_update.cryptocurrency_id
    #     ).first()

    #     if not cryptocurrency:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND,
    #             detail=f"Cryptocurrency with id {transaction_update.cryptocurrency_id} not found"
    #         )

    # อัพเดทเฉพาะ field ที่ส่งมา
    update_data = transaction_update.dict(exclude_unset=True)

    # เก็บค่า cryptocurrency_id เดิมไว้ก่อน (กรณีมีการเปลี่ยน cryptocurrency)
    old_cryptocurrency_id = transaction.cryptocurrency_id

    for field, value in update_data.items():
        setattr(transaction, field, value)

    transaction.updated_by = current_user.user_name
    transaction.updated_date = datetime.now()
    transaction.updated_program = "transaction_api"

    db.commit()
    db.refresh(transaction)

    # อัปเดต portfolio_holdings สำหรับ cryptocurrency ใหม่
    update_portfolio_holdings(
        db=db,
        portfolio_id=transaction.portfolio_id,
        cryptocurrency_id=transaction.cryptocurrency_id,
        username=current_user.user_name
    )

    # ถ้ามีการเปลี่ยน cryptocurrency ให้อัปเดต cryptocurrency เดิมด้วย
    if old_cryptocurrency_id != transaction.cryptocurrency_id:
        update_portfolio_holdings(
            db=db,
            portfolio_id=transaction.portfolio_id,
            cryptocurrency_id=old_cryptocurrency_id,
            username=current_user.user_name
        )

    # ดึงข้อมูลเพิ่มเติมเพื่อส่งกลับ
    result = db.query(
        models.Transaction,
        models.Portfolio.name.label('portfolio_name'),
        models.Cryptocurrency.symbol.label('cryptocurrency_symbol'),
        models.Cryptocurrency.name.label('cryptocurrency_name')
    ).join(
        models.Portfolio,
        models.Transaction.portfolio_id == models.Portfolio.id
    ).join(
        models.Cryptocurrency,
        models.Transaction.cryptocurrency_id == models.Cryptocurrency.id
    ).filter(
        models.Transaction.id == transaction_id
    ).first()

    transaction_obj, portfolio_name, crypto_symbol, crypto_name = result

    return {
        "id": transaction_obj.id,
        "portfolio_id": transaction_obj.portfolio_id,
        "cryptocurrency_id": transaction_obj.cryptocurrency_id,
        "transaction_type": transaction_obj.transaction_type,
        "quantity": transaction_obj.quantity,
        "price_per_unit": transaction_obj.price_per_unit,
        "total_amount": transaction_obj.total_amount,
        "fee": transaction_obj.fee,
        "transaction_date": transaction_obj.transaction_date,
        "notes": transaction_obj.notes,
        "created_by": transaction_obj.created_by,
        "created_date": transaction_obj.created_date,
        "created_program": transaction_obj.created_program,
        "updated_by": transaction_obj.updated_by,
        "updated_date": transaction_obj.updated_date,
        "updated_program": transaction_obj.updated_program,
        "portfolio_name": portfolio_name,
        "cryptocurrency_symbol": crypto_symbol,
        "cryptocurrency_name": crypto_name
    }


# =============== DELETE Endpoint ===============

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ลบ transaction

    - **transaction_id**: ID ของ transaction ที่ต้องการลบ
    - ต้องใช้ Token ใน Header: Authorization: Bearer <your_token>
    - จะตรวจสอบว่า transaction นี้อยู่ใน portfolio ของ user หรือไม่
    - คืนค่า 204 No Content เมื่อลบสำเร็จ
    """
    # ค้นหา transaction และตรวจสอบว่าเป็นของ user หรือไม่
    transaction = db.query(models.Transaction).join(
        models.Portfolio,
        models.Transaction.portfolio_id == models.Portfolio.id
    ).filter(
        models.Transaction.id == transaction_id,
        models.Portfolio.user_id == current_user.user_id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with id {transaction_id} not found or does not belong to current user"
        )

    # เก็บข้อมูลก่อนลบ
    portfolio_id = transaction.portfolio_id
    cryptocurrency_id = transaction.cryptocurrency_id

    db.delete(transaction)
    db.commit()

    # อัปเดต portfolio_holdings หลังจากลบ transaction
    update_portfolio_holdings(
        db=db,
        portfolio_id=portfolio_id,
        cryptocurrency_id=cryptocurrency_id,
        username=current_user.user_name
    )

    return None

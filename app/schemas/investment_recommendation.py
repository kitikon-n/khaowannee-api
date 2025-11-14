from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class InvestmentRecommendationResponse(BaseModel):
    id: int
    cryptocurrency_id: Optional[int]
    analysis_date: datetime

    # Short-term fields
    short_term_timeframe: Optional[str]
    short_term_signal: Optional[str]
    short_term_score: Optional[Decimal]
    short_term_recommendation: Optional[str]
    short_term_risk_level: Optional[str]
    short_market_momentum: Optional[str]
    short_trend_direction: Optional[str]
    short_market_volatility: Optional[str]
    short_liquidity: Optional[str]
    short_term_entry_price: Optional[Decimal]
    short_term_target_price: Optional[Decimal]
    short_term_stop_loss: Optional[Decimal]

    # Medium-term fields
    medium_term_timeframe: Optional[str]
    medium_term_signal: Optional[str]
    medium_term_score: Optional[Decimal]
    medium_term_recommendation: Optional[str]
    medium_term_risk_level: Optional[str]
    medium_market_momentum: Optional[str]
    medium_trend_direction: Optional[str]
    medium_market_volatility: Optional[str]
    medium_liquidity: Optional[str]
    medium_term_entry_price: Optional[Decimal]
    medium_term_target_price: Optional[Decimal]
    medium_term_stop_loss: Optional[Decimal]

    # Long-term fields
    long_term_timeframe: Optional[str]
    long_term_signal: Optional[str]
    long_term_score: Optional[Decimal]
    long_term_recommendation: Optional[str]
    long_term_risk_level: Optional[str]
    long_market_momentum: Optional[str]
    long_trend_direction: Optional[str]
    long_market_volatility: Optional[str]
    long_liquidity: Optional[str]
    long_term_entry_price: Optional[Decimal]
    long_term_target_price: Optional[Decimal]
    long_term_stop_loss: Optional[Decimal]

    # Overall fields
    overall_sentiment: Optional[str]
    current_price: Optional[Decimal]
    analyst_notes: Optional[str]
    confidence_level: Optional[str]
    data_sources: Optional[str]

    # Audit fields
    created_by: Optional[str]
    created_date: Optional[datetime]
    created_program: Optional[str]
    updated_by: Optional[str]
    updated_date: Optional[datetime]
    updated_program: Optional[str]

    class Config:
        from_attributes = True

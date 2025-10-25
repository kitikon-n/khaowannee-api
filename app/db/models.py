from sqlalchemy import Column, Integer, String, DateTime, Boolean, Numeric, Text, Date, BigInteger, ForeignKey, ForeignKeyConstraint, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.db.database import Base

# =============== Base Tables (ไม่มี Foreign Keys) ===============

class AIAnalysis(Base):
    __tablename__ = "ai_analysis"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_date = Column(Date)
    recommendation_class = Column(String(50))
    recommendation_title = Column(Text)
    recommendation_text = Column(Text)
    bullish_count = Column(Integer)
    neutral_count = Column(Integer)
    bearish_count = Column(Integer)
    overall_sentiment = Column(String(50))
    recommendation = Column(String(100))
    sentiment_score = Column(Numeric)
    technical_analysis = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    recommendation_stocks = Column(Text)

    # Relationships
    hot_topics = relationship("AIHotTopic", back_populates="analysis", cascade="all, delete-orphan")
    top_articles = relationship("AITopArticle", back_populates="analysis", cascade="all, delete-orphan")


class Cryptocurrency(Base):
    __tablename__ = "cryptocurrencies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    full_name = Column(String(200))
    description = Column(Text)
    website_url = Column(String(500))
    blockchain_network = Column(String(100))
    launch_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_by = Column(String(100))
    created_date = Column(DateTime(timezone=True))
    created_program = Column(String(100))
    updated_by = Column(String(100))
    updated_date = Column(DateTime(timezone=True))
    updated_program = Column(String(100))
    asset_type = Column(String(20))

    # Relationships
    news_cryptocurrencies = relationship("NewsCryptocurrency", back_populates="cryptocurrency")
    portfolio_holdings = relationship("PortfolioHolding", back_populates="cryptocurrency")
    price_alerts = relationship("PriceAlert", back_populates="cryptocurrency")
    transactions = relationship("Transaction", back_populates="cryptocurrency")


class DailyNewsAnalysis(Base):
    __tablename__ = "daily_news_analysis"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(Text)
    sentiment = Column(Text)
    source = Column(Text)
    url = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class DBListGroup(Base):
    __tablename__ = "db_list_group"

    group_code = Column(String(50), primary_key=True)
    description = Column(String(200))
    parent_group_code = Column(String(20))
    active = Column(Boolean, default=True)
    created_by = Column(String(100))
    created_date = Column(DateTime(timezone=True))
    created_program = Column(String(100))
    updated_by = Column(String(100))
    updated_date = Column(DateTime(timezone=True))
    updated_program = Column(String(100))

    # Relationships
    languages = relationship("DBListGroupLang", back_populates="group", cascade="all, delete-orphan")
    values = relationship("DBListValue", back_populates="group", cascade="all, delete-orphan")


class Exchange(Base):
    __tablename__ = "exchanges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    website_url = Column(String(500))
    country = Column(String(100))
    trading_fee_percentage = Column(Numeric(5, 4))
    is_active = Column(Boolean, default=True)
    created_by = Column(String(100))
    created_date = Column(DateTime(timezone=True))
    created_program = Column(String(100))
    updated_by = Column(String(100))
    updated_date = Column(DateTime(timezone=True))
    updated_program = Column(String(100))


class N8NChatHistory(Base):
    __tablename__ = "n8n_chat_histories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(255), nullable=False)
    message = Column(JSONB, nullable=False)


class NewsCategory(Base):
    __tablename__ = "news_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    color_code = Column(String(7))
    is_active = Column(Boolean, default=True)
    created_by = Column(String(100))
    created_date = Column(DateTime(timezone=True))
    created_program = Column(String(100))
    updated_by = Column(String(100))
    updated_date = Column(DateTime(timezone=True))
    updated_program = Column(String(100))

    # Relationships
    news = relationship("News", back_populates="category")


class NewsSource(Base):
    __tablename__ = "news_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    website_url = Column(String(500))
    logo_url = Column(String(500))
    credibility_score = Column(Integer, CheckConstraint('credibility_score >= 1 AND credibility_score <= 10'))
    source_type = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_by = Column(String(100))
    created_date = Column(DateTime(timezone=True))
    created_program = Column(String(100))
    updated_by = Column(String(100))
    updated_date = Column(DateTime(timezone=True))
    updated_program = Column(String(100))

    # Relationships
    news = relationship("News", back_populates="news_source")


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    total_invested = Column(Numeric(15, 2), default=0)
    current_value = Column(Numeric(15, 2), default=0)
    profit_loss = Column(Numeric(15, 2), default=0)
    profit_loss_percentage = Column(Numeric(8, 4), default=0)
    created_by = Column(String(100))
    created_date = Column(DateTime(timezone=True))
    created_program = Column(String(100))
    updated_by = Column(String(100))
    updated_date = Column(DateTime(timezone=True))
    updated_program = Column(String(100))
    asset = Column(String(10))

    # Relationships
    holdings = relationship("PortfolioHolding", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="portfolio")


class User(Base):
    __tablename__ = "su_user"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(20), unique=True, nullable=False)
    password = Column(String(500))
    email = Column(String(50))
    active = Column(Boolean)
    created_by = Column(String(100))
    created_date = Column(DateTime)
    created_program = Column(String(100))
    updated_by = Column(String(100))
    updated_date = Column(DateTime)
    updated_program = Column(String(100))
    telegram_user_id = Column(BigInteger)


# =============== Tables with Foreign Keys ===============

class AIHotTopic(Base):
    __tablename__ = "ai_hot_topics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey('ai_analysis.id', ondelete='CASCADE'))
    topic = Column(Text)
    article_count = Column(Integer)
    average_relevance = Column(Numeric)

    # Relationships
    analysis = relationship("AIAnalysis", back_populates="hot_topics")


class AITopArticle(Base):
    __tablename__ = "ai_top_articles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey('ai_analysis.id', ondelete='CASCADE'))
    title = Column(Text)
    url = Column(Text)
    source = Column(Text)
    article_date = Column(Date)
    sentiment_class = Column(String(50))
    sentiment_hebrew = Column(String(50))

    # Relationships
    analysis = relationship("AIAnalysis", back_populates="top_articles")


class DBListGroupLang(Base):
    __tablename__ = "db_list_group_lang"

    group_code = Column(String(50), ForeignKey('db_list_group.group_code', ondelete='CASCADE'), primary_key=True)
    language_code = Column(String(20), primary_key=True)
    group_name = Column(String(200))
    active = Column(Boolean, default=True)
    created_by = Column(String(100))
    created_date = Column(DateTime(timezone=True))
    created_program = Column(String(100))
    updated_by = Column(String(100))
    updated_date = Column(DateTime(timezone=True))
    updated_program = Column(String(100))

    # Relationships
    group = relationship("DBListGroup", back_populates="languages")


class DBListValue(Base):
    __tablename__ = "db_list_value"

    group_code = Column(String(50), ForeignKey('db_list_group.group_code', ondelete='CASCADE'), primary_key=True)
    value = Column(String(100), primary_key=True)
    description = Column(String(200))
    parent_group_code = Column(String(20))
    parent_value = Column(String(100))
    sequence = Column(Integer)
    active = Column(Boolean, default=True)
    created_by = Column(String(100))
    created_date = Column(DateTime(timezone=True))
    created_program = Column(String(100))
    updated_by = Column(String(100))
    updated_date = Column(DateTime(timezone=True))
    updated_program = Column(String(100))

    # Relationships
    group = relationship("DBListGroup", back_populates="values")
    languages = relationship("DBListValueLang", back_populates="list_value", cascade="all, delete-orphan")


class DBListValueLang(Base):
    __tablename__ = "db_list_value_lang"

    group_code = Column(String(50), primary_key=True)
    value = Column(String(100), primary_key=True)
    language_code = Column(String(20), primary_key=True)
    value_text = Column(Text)
    created_by = Column(String(100))
    created_date = Column(DateTime(timezone=True))
    created_program = Column(String(100))
    updated_by = Column(String(100))
    updated_date = Column(DateTime(timezone=True))
    updated_program = Column(String(100))
    value_json = Column(String(1000))

    # Foreign key constraint (composite key)
    __table_args__ = (
        ForeignKeyConstraint(
            ['group_code', 'value'],
            ['db_list_value.group_code', 'db_list_value.value'],
            ondelete='CASCADE'
        ),
    )

    # Relationships
    list_value = relationship("DBListValue", back_populates="languages")


class News(Base):
    __tablename__ = "news"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(500), unique=True, nullable=False)
    content = Column(Text)
    summary = Column(Text)
    url = Column(String(1000))
    image_url = Column(String(500))
    author = Column(String(200))
    news_source_id = Column(Integer, ForeignKey('news_sources.id'))
    category_id = Column(Integer, ForeignKey('news_categories.id'))
    published_at = Column(DateTime, nullable=False)
    sentiment_score = Column(Numeric(3, 2))
    impact_level = Column(String(20))
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(String(100))
    created_date = Column(DateTime(timezone=True))
    created_program = Column(String(100))
    updated_by = Column(String(100))
    updated_date = Column(DateTime(timezone=True))
    updated_program = Column(String(100))
    recommendation_text = Column(String)

    # Relationships
    news_source = relationship("NewsSource", back_populates="news")
    category = relationship("NewsCategory", back_populates="news")
    news_cryptocurrencies = relationship("NewsCryptocurrency", back_populates="news", cascade="all, delete-orphan")


class NewsCryptocurrency(Base):
    __tablename__ = "news_cryptocurrencies"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    news_id = Column(BigInteger, ForeignKey('news.id', ondelete='CASCADE'))
    cryptocurrency_id = Column(Integer, ForeignKey('cryptocurrencies.id'))
    impact_type = Column(String(20))
    impact_strength = Column(Integer, CheckConstraint('impact_strength >= 1 AND impact_strength <= 5'))
    price_before = Column(Numeric(20, 8))
    price_after_1h = Column(Numeric(20, 8))
    price_after_24h = Column(Numeric(20, 8))
    volume_change_percentage = Column(Numeric(8, 4))
    notes = Column(Text)
    created_by = Column(String(100))
    created_date = Column(DateTime(timezone=True))
    created_program = Column(String(100))
    updated_by = Column(String(100))
    updated_date = Column(DateTime(timezone=True))
    updated_program = Column(String(100))
    ticket = Column(String)
    technical_analysis = Column(String)

    # Relationships
    news = relationship("News", back_populates="news_cryptocurrencies")
    cryptocurrency = relationship("Cryptocurrency", back_populates="news_cryptocurrencies")


class PortfolioHolding(Base):
    __tablename__ = "portfolio_holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id', ondelete='CASCADE'))
    cryptocurrency_id = Column(Integer, ForeignKey('cryptocurrencies.id'))
    quantity = Column(Numeric(30, 8), nullable=False)
    average_buy_price = Column(Numeric(20, 8))
    total_invested = Column(Numeric(15, 2))
    current_price = Column(Numeric(20, 8))
    current_value = Column(Numeric(15, 2))
    profit_loss = Column(Numeric(15, 2))
    profit_loss_percentage = Column(Numeric(8, 4))
    created_by = Column(String(100))
    created_date = Column(DateTime(timezone=True))
    created_program = Column(String(100))
    updated_by = Column(String(100))
    updated_date = Column(DateTime(timezone=True))
    updated_program = Column(String(100))

    __table_args__ = (
        CheckConstraint('portfolio_id IS NOT NULL AND cryptocurrency_id IS NOT NULL', name='portfolio_holdings_portfolio_id_cryptocurrency_id_key'),
    )

    # Relationships
    portfolio = relationship("Portfolio", back_populates="holdings")
    cryptocurrency = relationship("Cryptocurrency", back_populates="portfolio_holdings")


class PriceAlert(Base):
    __tablename__ = "price_alerts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    cryptocurrency_id = Column(Integer, ForeignKey('cryptocurrencies.id'))
    alert_type = Column(String(20), CheckConstraint("alert_type IN ('ABOVE', 'BELOW', 'CHANGE_PERCENT')"))
    target_price = Column(Numeric(20, 8))
    percentage_change = Column(Numeric(8, 4))
    timeframe = Column(String(10), default='24h')
    message = Column(Text)
    is_triggered = Column(Boolean, default=False)
    triggered_at = Column(DateTime)
    triggered_price = Column(Numeric(20, 8))
    is_active = Column(Boolean, default=True)
    created_by = Column(String(100))
    created_date = Column(DateTime(timezone=True))
    created_program = Column(String(100))
    updated_by = Column(String(100))
    updated_date = Column(DateTime(timezone=True))
    updated_program = Column(String(100))

    # Relationships
    cryptocurrency = relationship("Cryptocurrency", back_populates="price_alerts")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'))
    cryptocurrency_id = Column(Integer, ForeignKey('cryptocurrencies.id'))
    transaction_type = Column(String(10))
    quantity = Column(Numeric(30, 8), nullable=False)
    price_per_unit = Column(Numeric(20, 8), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    fee = Column(Numeric(15, 6), default=0)
    transaction_date = Column(DateTime, nullable=False)
    notes = Column(Text)
    created_by = Column(String(100))
    created_date = Column(DateTime(timezone=True))
    created_program = Column(String(100))
    updated_by = Column(String(100))
    updated_date = Column(DateTime(timezone=True))
    updated_program = Column(String(100))

    # Relationships
    portfolio = relationship("Portfolio", back_populates="transactions")
    cryptocurrency = relationship("Cryptocurrency", back_populates="transactions")

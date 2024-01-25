from sqlalchemy import Date, Double, Float, create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Stock(Base):
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True)
    arg = Column(String(50))
    sector = Column(String(50))
    code = Column(String(50), unique=True, nullable=False)
    pe_ratio = Column(Float)
    stock_details = relationship('StockDetails', back_populates='stock')

class StockDetails(Base):
    __tablename__ = 'stock_details'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    close = Column(Float)
    altman_z_score = Column(Float)
    f_score = Column(Integer)
    sloan_ratio = Column(Float)
    stock_id = Column(Integer, ForeignKey('stocks.id'))
    stock = relationship('Stock', back_populates='stock_details')

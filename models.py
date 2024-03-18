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
    
    def __repr__(self):
        return f"<Stock(id={self.id},\n arg='{self.arg}',\n sector='{self.sector}',\n code='{self.code}',\n pe_ratio={self.pe_ratio})>"
    

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
    
    def __repr__(self):
        return f"<StockDetails(id={self.id},\n date={self.date},\n close={self.close},\n altman_z_score={self.altman_z_score},\n f_score={self.f_score},\n sloan_ratio={self.sloan_ratio},\n stock_id={self.stock_id})>"

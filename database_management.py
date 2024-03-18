import os
from requests import session
import pymysql
from sqlalchemy import Engine, event, create_engine, null, text
from sqlalchemy.orm import scoped_session, sessionmaker

from models import Base, Stock, StockDetails

try:
    engine = create_engine("mysql+pymysql://root:password@localhost:3306/stockscrapper")
    session = scoped_session(sessionmaker(autoflush=False, autocommit=False, bind=engine))
    Base.metadata.create_all(engine)
    
    def getStock(code):
        stock = session.query(Stock).filter_by(code=code).first()
        return stock
    
    def getArgStock(arg):
        stock = session.query(Stock).filter_by(arg=arg).first()
        return stock
    
    def addStock(arg, code, sector):
        newStock = Stock(arg = arg, code = code, sector = sector)
        session.add(newStock)
        session.commit()
    
    def getStockDetails(code):
        stock = session.query(Stock).filter_by(code=code).first()
        if not stock:
            return null
        stockDetails = session.query(StockDetails).filter_by(stock_id=stock.id).order_by(StockDetails.date.desc()).first()
        return stockDetails
        
    def getStockDetailsAllDates(code):
        stock = session.query(Stock).filter_by(code=code).first()
        stockDetails = []
        if stock:
            stockDetails = session.query(StockDetails).filter_by(stock_id=stock.id).order_by(StockDetails.date.desc()).all()
        
        return stockDetails

    def addStockDetails(close, date, altman, f_score, sloan, s_id):
        newStockDetails = StockDetails(
            close = close,
            date = date,
            altman_z_score = altman,
            f_score = f_score,
            sloan_ratio = sloan,
            stock_id = s_id
        )
        session.add(newStockDetails)
        session.commit()
        

    #! Why this?
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print(result)
        print("Connection successful")

except Exception as e:
    print(f"Connection failed: {e}")

finally:
    session.remove()
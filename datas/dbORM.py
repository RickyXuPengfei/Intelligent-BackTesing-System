import pymysql

pymysql.install_as_MySQLdb()
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Float, DateTime
from sqlalchemy.orm import sessionmaker
import pandas as pd
import os

engine = create_engine('mysql://root:@localhost:3306/AutoTrading?charset=utf8')

Base = declarative_base()


class BitCoin(Base):
    __tablename__ = 'BitCoin'

    datetime = Column(DateTime, primary_key=True)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    adj_close = Column(Float, nullable=True)


if __name__ == '__main__':
    # Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    data = pd.io.parsers.read_csv(os.path.join('bitcoin.csv'),
                                  header=0, index_col=0)
    data_rows = data.iterrows()
    add_data = [BitCoin(datetime=row[0], open=float(getattr(row[1], 'open')), high=float(getattr(row[1], 'high')),
                        low=float(getattr(row[1], 'low')), close=float(getattr(row[1], 'close')),
                        volume=float(getattr(row[1], 'volume')), adj_close=float(getattr(row[1], 'adj_close'))) for row
                in data_rows]
    # session.add_all(add_data)
    # session.commit()
    # a = session.execute("show tables")
    # print (a.next()[0])

    data = pd.read_sql_query("select * from BitCoin", session.bind, index_col="datetime")
    print(data.loc[data.index[2:100], 'open':"close"])

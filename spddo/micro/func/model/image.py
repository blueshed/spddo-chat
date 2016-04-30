'''
Created on 30 Apr 2016

@author: peterb
'''
from blueshed.micro.orm.orm_utils import Base
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import String, Integer, DateTime
import datetime


class Image(Base):

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    path = Column(String(255))
    uploaded = Column(DateTime, default=datetime.datetime.now)

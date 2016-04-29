from sqlalchemy.types import String, Integer
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.orm import relationship
from blueshed.micro.orm.orm_utils import _Base_
from sqlalchemy.ext.declarative.api import declarative_base

Base = declarative_base(cls=_Base_)


class User(Base):

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    email = Column(String(128))
    password = Column(String(80))
    subscriptions = relationship('Subscription', uselist=True,
                                 primaryjoin='Subscription.user_id==User.id',
                                 remote_side='Subscription.user_id',
                                 back_populates='user')


class Subscription(Base):

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey('service.id'))
    service = relationship('Service', uselist=False,
                           primaryjoin='Subscription.service_id==Service.id',
                           remote_side='Service.id')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', uselist=False,
                        primaryjoin='Subscription.user_id==User.id',
                        remote_side='User.id',
                        back_populates='subscriptions')


class Service(Base):

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    cookie_url = Column(String(255), doc='client url to place cookie')
    cors = Column(String(255), doc='our cors to accept backdoor requests')
    token = Column(String(255), doc='token to validate backdoor requests')

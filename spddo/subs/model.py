from sqlalchemy.types import String, Integer, Numeric, DateTime, Date, Time, Enum, Boolean, Text
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.orm import relationship, backref
from blueshed.micro.utils.orm_utils import Base


class User(Base):

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    email = Column(String(128))
    password = Column(String(80))
    roles = relationship('Role', uselist=True,
                         primaryjoin='Role.user_id==User.id',
                         remote_side='Role.user_id',
                         back_populates='user')
    subscriptions = relationship('Subscription', uselist=True,
                                 primaryjoin='Subscription.user_id==User.id',
                                 remote_side='Subscription.user_id',
                                 back_populates='user')


class Role(Base):

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', uselist=False,
                        primaryjoin='Role.user_id==User.id',
                        remote_side='User.id',
                        back_populates='roles')
    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship('Group', uselist=False,
                         primaryjoin='Role.group_id==Group.id',
                         remote_side='Group.id',
                         back_populates='roles')


class Group(Base):

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    roles = relationship('Role', uselist=True,
                         primaryjoin='Role.group_id==Group.id',
                         remote_side='Role.group_id',
                         back_populates='group')
    subscriptions = relationship('Subscription', uselist=True,
                                 primaryjoin='Subscription.group_id==Group.id',
                                 remote_side='Subscription.group_id',
                                 back_populates='group')


class Subscription(Base):

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship('Group', uselist=False,
                         primaryjoin='Subscription.group_id==Group.id',
                         remote_side='Group.id',
                         back_populates='subscriptions')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', uselist=False,
                        primaryjoin='Subscription.user_id==User.id',
                        remote_side='User.id',
                        back_populates='subscriptions')
    payment_id = Column(Integer, ForeignKey('payment.id'))
    payment = relationship('Payment', uselist=False,
                           primaryjoin='Subscription.payment_id==Payment.id',
                           remote_side='Payment.id',
                           back_populates='subscriptions')
    service_id = Column(Integer, ForeignKey('service.id'))
    service = relationship('Service', uselist=False,
                           primaryjoin='Subscription.service_id==Service.id',
                           remote_side='Service.id',
                           back_populates='subscriptions')
    from_date = Column(Date)
    to_date = Column(Date)
    prefs = Column(Text)
    cost = Column(Numeric(36, 12))


class Service(Base):

    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    description = Column(String(255))
    prefs = Column(Text)
    cost = Column(Numeric(36, 12))
    duration = Column(Integer)
    subscriptions = relationship('Subscription', uselist=True,
                                 primaryjoin='Subscription.service_id==Service.id',
                                 remote_side='Subscription.service_id',
                                 back_populates='service')


class Payment(Base):

    PAYEE = ['user', 'group']

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    amount = Column(Numeric(36, 12))
    payee = Column(Enum(*PAYEE))
    subscriptions = relationship('Subscription', uselist=True,
                                 primaryjoin='Subscription.payment_id==Payment.id',
                                 remote_side='Subscription.payment_id',
                                 back_populates='payment')

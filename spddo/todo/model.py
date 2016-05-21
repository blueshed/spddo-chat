from blueshed.micro.orm.orm_utils import Base
from sqlalchemy.types import String, Integer, DateTime
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.orm import relationship


user_permissions_user = Table('user_permissions_user', Base.metadata,
                              Column(
                                  'permissions_id', Integer, ForeignKey('user.id')),
                              Column(
                                  'user_id', Integer, ForeignKey('user.id')),
                              mysql_comment='{\"back_populates\":\"User.permissions\"}',
                              mysql_engine='InnoDB')


class Permission(Base):

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)


class User(Base):

    id = Column(Integer, primary_key=True)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255))
    permissions = relationship('User',
                               primaryjoin='User.id==user_permissions_user.c.permissions_id',
                               secondaryjoin='User.id==user_permissions_user.c.user_id',
                               secondary='user_permissions_user',
                               lazy='joined')
    todos = relationship('ToDo', uselist=True,
                         cascade='all,delete-orphan', passive_deletes=True,
                         primaryjoin='ToDo.person_id==User.id',
                         remote_side='ToDo.person_id',
                         back_populates='person')


class ToDo(Base):

    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
    person = relationship('User', uselist=False,
                          primaryjoin='ToDo.person_id==User.id',
                          remote_side='User.id',
                          back_populates='todos')
    description = Column(String(255))
    created = Column(DateTime)
    done = Column(DateTime)

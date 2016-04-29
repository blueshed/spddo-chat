from blueshed.micro.orm import db_connection
from blueshed.micro.utils.base_context import BaseContext
from tests.actions import model
import datetime


class Context(BaseContext):
    """ Extend BaseContext to include a db session """

    @property
    def session(self):
        return db_connection.session()

    def flushed(self, request=None):
        if self.broadcasts:
            with self.session as session:
                now = datetime.datetime.now()
                user = self.cookies.get('current_user')
                user_id = user.get("id") if user else None
                for signal, message in self.broadcasts:
                    session.add(model.Log(signal=signal,
                                          message=message,
                                          created_by=user_id,
                                          created=now))
                session.commit()

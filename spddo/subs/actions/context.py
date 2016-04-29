import logging
from blueshed.micro.orm import db_connection
from blueshed.micro.utils.base_context import BaseContext
from tornado.ioloop import IOLoop
from spddo.subs.actions.sync_auth import sync_auth
from spddo.subs.actions.active_subscriptions import active_subscriptions_for
from spddo.subs import model


class Context(BaseContext):
    """ Extend BaseContext to include a db session """

    @property
    def session(self):
        return db_connection.session()

    def synced(self, future):
        try:
            result = future.result()
            logging.info("synced %s", result)
        except Exception as ex:
            logging.exception(ex)

    def flushed(self, request=None):
        BaseContext.flushed(self)
        sync_user_subs = set()
        with self.session as session:
            for signal, message in self.broadcasts:
                if signal in ["user-added", "user-changed"]:
                    user = session.query(model.User).get(message["id"])
                    IOLoop.instance().add_future(
                        sync_auth("save_user.js", **{
                            'user_id': user.id,
                            'name': user.name,
                            'email': user.email,
                            'password': user.password
                        }),
                        self.synced)
                elif signal in ["service-added", "service-changed"]:
                    service = session.query(model.Service).get(message["id"])
                    IOLoop.instance().add_future(
                        sync_auth("save_service.js", **{
                            "service_id": service.id,
                            "name": service.name,
                            "cookie_url": service.token_url,
                            "cors": service.cors
                        }),
                        self.synced)
                elif signal == "subscription-active":
                    sync_user_subs.add(message.get("user_id"))

                for user_id in sync_user_subs:
                    subs = {
                        "user_id": user_id,
                        "service_ids": [s.service_id
                                        for s in active_subscriptions_for(
                                            session,
                                            user_id,
                                            loaded=False)]
                    }
                    IOLoop.instance().add_future(
                        sync_auth("set_subscriptions.js", **subs),
                        self.synced)

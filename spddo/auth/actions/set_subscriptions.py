from spddo.auth import model


def set_subscriptions(context: 'micro_context',
                      user_id: int,
                      service_ids: list):
    '''
        removes old subscriptions, if any, and inserts new, if any
    '''
    with context.session as session:
        user = session.query(model.User).get(user_id)
        if user is None:
            raise Exception("no such user")
        session.query(model.Subscription).\
            filter(model.Subscription.user == user).\
            delete()
        session.flush()
        for service_id in service_ids:
            service = session.query(model.Service).get(service_id)
            if service is None:
                raise Exception("Service unknown {}".format(service_id))
            session.add(model.Subscription(user=user, service=service))
        session.commit()

from blueshed.micro.utils.orm_utils import connect
from contextlib import contextmanager
import logging
from blueshed.micro.utils import resources

_session_ = None
_engine_ = None


def db_init(db_url, db_echo=False, db_pool_recycle=None):
    global _session_, _engine_
    _engine_, _session_ = connect(db_url, db_echo, db_pool_recycle)
    logging.info("connecting to: %s", db_url)


def register_db(resource_name, db_url, db_echo=False, db_pool_recycle=None):
    engine, Session = connect(db_url, db_echo, db_pool_recycle)
    logging.info("connecting to: %s", resource_name)
    resources.set_resource(resource_name, (engine, Session))


@contextmanager
def session(resource_name=None):
    """Provide a transactional scope around a series of operations."""
    if resource_name is not None:
        _, Session = resources.get_resource(resource_name)
        session = Session()
    else:
        global _session_
        assert _session_
        session = _session_()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
